import json
import ssl
import time
import xbmc

try:
    from urllib2 import Request, urlopen, HTTPError, URLError
except ImportError:  # py2 / py3
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError

try:
    from .web_image_search import WebImageSearch
    WEB_IMAGE_SEARCH_AVAILABLE = True
except ImportError:
    WEB_IMAGE_SEARCH_AVAILABLE = False
    xbmc.log("Web image search module not available", xbmc.LOGWARNING)


class StashScraper:
    """Scraper for StashApp API"""
    
    def __init__(self, stash_url, api_key, settings=None):
        self.stash_url = stash_url.rstrip('/')
        self.api_key = api_key
        self.graphql_url = "{}/graphql".format(self.stash_url)
        self.settings = settings
        
        # Get retry settings from user configuration
        if settings:
            self.timeout = settings.getSettingInt('connection_timeout') or 30
            self.max_retries = settings.getSettingInt('max_retries') or 3
        else:
            self.timeout = 30
            self.max_retries = 3
        
        self.retry_delay = 2  # seconds
        
        # Create SSL context that doesn't verify certificates (for self-signed certs)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        xbmc.log("[Stash Scraper] Initialized with URL: {} (timeout: {}s, retries: {})".format(
            self.stash_url, self.timeout, self.max_retries), xbmc.LOGINFO)
        
        # Initialize web image search if enabled
        self.web_search = None
        if settings and WEB_IMAGE_SEARCH_AVAILABLE:
            if settings.getSettingBool('enable_web_image_search'):
                google_key = settings.getSettingString('google_api_key')
                google_cx = settings.getSettingString('google_cx')
                bing_key = settings.getSettingString('bing_api_key')
                
                self.web_search = WebImageSearch(
                    google_api_key=google_key,
                    google_cx=google_cx,
                    bing_api_key=bing_key
                )
                xbmc.log("Web image search initialized", xbmc.LOGINFO)
    
    def _make_request(self, query, variables=None, retry_count=0):
        """Make a GraphQL request to Stash with retry logic"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            if self.api_key:
                headers['ApiKey'] = self.api_key
            
            data = {'query': query}
            if variables:
                data['variables'] = variables
            
            xbmc.log("[Stash Scraper] Making request (attempt {}/{})".format(retry_count + 1, self.max_retries + 1), xbmc.LOGDEBUG)
            
            request = Request(
                self.graphql_url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers
            )
            
            # Use SSL context for HTTPS connections
            response = urlopen(request, timeout=self.timeout, context=self.ssl_context)
            result = json.loads(response.read().decode('utf-8'))
            
            if 'errors' in result:
                error_detail = result['errors'][0].get('message', 'Unknown error')
                xbmc.log("[Stash Scraper] GraphQL error: {}".format(error_detail), xbmc.LOGERROR)
                return {'error': 'GraphQL error: {}'.format(error_detail)}
            
            xbmc.log("[Stash Scraper] Request successful", xbmc.LOGDEBUG)
            return result.get('data', {})
        
        except HTTPError as e:
            error_msg = "HTTP Error {}: {}".format(e.code, e.reason)
            xbmc.log("[Stash Scraper] HTTP error: {}".format(error_msg), xbmc.LOGERROR)
            
            # Retry on server errors (5xx) but not client errors (4xx)
            if e.code >= 500 and retry_count < self.max_retries:
                xbmc.log("[Stash Scraper] Retrying after server error...", xbmc.LOGWARNING)
                time.sleep(self.retry_delay)
                return self._make_request(query, variables, retry_count + 1)
            
            return {'error': error_msg}
        
        except URLError as e:
            error_msg = "Connection error: {}".format(str(e.reason))
            xbmc.log("[Stash Scraper] Connection error: {}".format(error_msg), xbmc.LOGERROR)
            
            # Retry on connection errors
            if retry_count < self.max_retries:
                xbmc.log("[Stash Scraper] Retrying after connection error...", xbmc.LOGWARNING)
                time.sleep(self.retry_delay)
                return self._make_request(query, variables, retry_count + 1)
            
            return {'error': error_msg}
        
        except Exception as e:
            error_msg = "Unexpected error: {}".format(str(e))
            xbmc.log("[Stash Scraper] Unexpected error: {}".format(error_msg), xbmc.LOGERROR)
            return {'error': error_msg}
    
    def search(self, title, year=None):
        """Search for scenes by title"""
        query = """
query findScenes($scene_filter: SceneFilterType, $filter: FindFilterType!) {
  findScenes(scene_filter: $scene_filter, filter: $filter) {
    count
    scenes {
      id
      title
      date
      details
      rating100
      paths {
        screenshot
      }
      studio {
        name
      }
    }
  }
}
        """
        
        variables = {
            'filter': {
                'q': title,
                'per_page': 20,
                'sort': 'title',
                'direction': 'ASC'
            },
            'scene_filter': {}
        }
        
        result = self._make_request(query, variables)
        
        if 'error' in result:
            return result
        
        if not result.get('findScenes') or not result['findScenes'].get('scenes'):
            return []
        
        scenes = []
        for scene in result['findScenes']['scenes']:
            # Filter by year if provided
            if year and scene.get('date'):
                try:
                    scene_year = scene['date'].split('-')[0]
                    if scene_year != str(year):
                        continue
                except (ValueError, IndexError):
                    pass
            
            scenes.append({
                'id': scene['id'],
                'title': scene.get('title', 'Untitled'),
                'date': scene.get('date', ''),
                'image': scene['paths'].get('screenshot', '') if scene.get('paths') else ''
            })
        
        return scenes
    
    def get_details(self, scene_id):
        """Get detailed information for a specific scene"""
        query = """
query findScene($id: ID!) {
  findScene(id: $id) {
    id
    title
    details
    date
    rating100
    paths {
      screenshot
      stream
    }
    files {
      duration
      video_codec
      audio_codec
      width
      height
    }
    studio {
      name
      image_path
    }
    performers {
      name
      image_path
    }
    tags {
      name
    }
  }
}
        """
        
        variables = {'id': scene_id}
        result = self._make_request(query, variables)
        
        if 'error' in result:
            return result
        
        scene = result.get('findScene')
        if not scene:
            return {'error': 'Scene not found'}
        
        # Build info dict
        info = {
            'title': scene.get('title', 'Untitled'),
            'originaltitle': scene.get('title', 'Untitled'),
            'plot': scene.get('details', ''),
            'tagline': scene.get('url', ''),
            'studio': [],
            'genre': [],
            'tag': [],
            'director': [],
            'premiered': scene.get('date', '')
        }
        
        # Add duration (files is an array)
        if scene.get('files') and len(scene['files']) > 0 and scene['files'][0].get('duration'):
            info['duration'] = int(float(scene['files'][0]['duration']))
        
        # Add rating (convert from 0-100 to 0-10)
        if scene.get('rating100'):
            info['rating'] = float(scene['rating100']) / 10.0
        
        # Add studio
        if scene.get('studio'):
            info['studio'].append(scene['studio']['name'])
        
        # Add tags as genres and tags
        if scene.get('tags'):
            for tag in scene['tags']:
                tag_name = tag['name']
                info['tag'].append(tag_name)
                # Some tags might be genres
                if self._is_genre_tag(tag_name):
                    info['genre'].append(tag_name)
        
        # Build cast list from performers
        cast = []
        if scene.get('performers'):
            for idx, performer in enumerate(scene['performers']):
                cast.append({
                    'name': performer['name'],
                    'role': performer.get('disambiguation', ''),
                    'order': idx,
                    'thumbnail': performer.get('image_path', '')
                })
        
        # Build artwork dict
        available_art = {}
        if scene.get('paths'):
            paths = scene['paths']
            if paths.get('screenshot'):
                available_art['thumb'] = paths['screenshot']
                available_art['poster'] = paths['screenshot']
            if paths.get('webp'):
                available_art['fanart'] = paths['webp']
            elif paths.get('screenshot'):
                available_art['fanart'] = paths['screenshot']
        
        # Use web search as fallback if no images found or if not in fallback-only mode
        if self.web_search and self.settings:
            fallback_only = self.settings.getSettingBool('web_search_fallback_only')
            
            # Check if we should search the web
            should_search = False
            if fallback_only:
                # Only search if no images from Stash
                should_search = not available_art or len(available_art) == 0
            else:
                # Always search to supplement existing images
                should_search = True
            
            if should_search:
                try:
                    # Build search query from title and studio
                    title = scene.get('title', '')
                    studio_name = scene.get('studio', {}).get('name', '') if scene.get('studio') else ''
                    search_query = "{} {}".format(title, studio_name).strip()
                    
                    if search_query:
                        xbmc.log("Searching web for images: {}".format(search_query), xbmc.LOGINFO)
                        
                        search_engine = self.settings.getSettingString('web_search_engine')
                        max_images = int(self.settings.getSettingInt('max_web_images'))
                        
                        # Search and download images
                        downloaded_images = self.web_search.search_and_download(
                            search_query, 
                            max_results=max_images,
                            search_engine=search_engine
                        )
                        
                        # Add downloaded images to available art
                        if downloaded_images:
                            xbmc.log("Found {} web images for scene".format(len(downloaded_images)), xbmc.LOGINFO)
                            
                            # If no poster/thumb, use first web image
                            if not available_art.get('poster') and len(downloaded_images) > 0:
                                available_art['poster'] = downloaded_images[0]
                            if not available_art.get('thumb') and len(downloaded_images) > 0:
                                available_art['thumb'] = downloaded_images[0]
                            
                            # If no fanart, use second web image (or first if only one)
                            if not available_art.get('fanart') and len(downloaded_images) > 0:
                                available_art['fanart'] = downloaded_images[1 if len(downloaded_images) > 1 else 0]
                            
                            # Store all web images for potential use
                            available_art['web_images'] = downloaded_images
                        
                except Exception as e:
                    xbmc.log("Web image search failed: {}".format(str(e)), xbmc.LOGERROR)
        
        return {
            'info': info,
            'cast': cast,
            'uniqueids': {'stash': scene_id},
            'available_art': available_art
        }
    
    def scrape_scene(self, scene_id, scraper_source='stashdb'):
        """Trigger Stash to scrape a scene from external sources (StashDB or TPDB)
        
        Args:
            scene_id: The scene ID to scrape
            scraper_source: 'stashdb' or 'tpdb'
        """
        query = """
mutation ScrapeSingleScene($source: ScraperSourceInput!, $input: ScrapeSingleSceneInput!) {
  scrapeSingleScene(source: $source, input: $input) {
    title
    details
    date
    studio {
      stored_id
      name
    }
    performers {
      stored_id
      name
    }
    tags {
      stored_id
      name
    }
    image
  }
}
        """
        
        # Configure source based on scraper type
        if scraper_source.lower() == 'tpdb':
            source_config = {
                'scraper_id': 'builtin_tpdb'
            }
        else:  # Default to stashdb
            source_config = {
                'stash_box_endpoint': 0  # Use first configured stash-box
            }
        
        variables = {
            'source': source_config,
            'input': {
                'scene_id': scene_id
            }
        }
        
        result = self._make_request(query, variables)
        
        if 'error' in result:
            return result
        
        scraped_data = result.get('scrapeSingleScene')
        if not scraped_data:
            return {'error': 'No results from scraper'}
        
        return scraped_data
    
    def update_scene(self, scene_id, scraped_data):
        """Update scene with scraped metadata"""
        query = """
mutation SceneUpdate($input: SceneUpdateInput!) {
  sceneUpdate(input: $input) {
    id
  }
}
        """
        
        # Build update input from scraped data
        update_input = {
            'id': scene_id
        }
        
        if scraped_data.get('title'):
            update_input['title'] = scraped_data['title']
        if scraped_data.get('details'):
            update_input['details'] = scraped_data['details']
        if scraped_data.get('date'):
            update_input['date'] = scraped_data['date']
        if scraped_data.get('studio') and scraped_data['studio'].get('stored_id'):
            update_input['studio_id'] = scraped_data['studio']['stored_id']
        if scraped_data.get('performers'):
            update_input['performer_ids'] = [p['stored_id'] for p in scraped_data['performers'] if p.get('stored_id')]
        if scraped_data.get('tags'):
            update_input['tag_ids'] = [t['stored_id'] for t in scraped_data['tags'] if t.get('stored_id')]
        
        variables = {'input': update_input}
        result = self._make_request(query, variables)
        
        if 'error' in result:
            return result
        
        return result.get('sceneUpdate')
    
    def search_external(self, query_string, scraper_source='stashdb'):
        """Search external sources (StashDB or TPDB) for scenes
        
        Args:
            query_string: Search query
            scraper_source: 'stashdb' or 'tpdb'
        """
        query = """
query ScrapeScene($input: ScrapeSingleSceneInput!, $source: ScraperSourceInput!) {
  scrapeScene(input: $input, source: $source) {
    title
    details
    date
    remote_site_id
    studio {
      name
    }
    performers {
      name
    }
  }
}
        """
        
        # Configure source based on scraper type
        if scraper_source.lower() == 'tpdb':
            source_config = {
                'scraper_id': 'builtin_tpdb'
            }
        else:  # Default to stashdb
            source_config = {
                'stash_box_endpoint': 0
            }
        
        variables = {
            'source': source_config,
            'input': {
                'query': query_string
            }
        }
        
        result = self._make_request(query, variables)
        
        if 'error' in result:
            return result
        
        return result.get('scrapeScene', [])
    
    def _is_genre_tag(self, tag_name):
        """Determine if a tag should be treated as a genre"""
        # Common genre-like tags
        genre_keywords = [
            'action', 'comedy', 'drama', 'horror', 'thriller', 
            'romance', 'sci-fi', 'fantasy', 'documentary', 'animation'
        ]
        tag_lower = tag_name.lower()
        return any(keyword in tag_lower for keyword in genre_keywords)
