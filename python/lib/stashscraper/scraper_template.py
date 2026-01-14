"""
Template for creating a new scraper for the Stash addon.

This template shows the structure needed to integrate a new scraper.
Follow this pattern to create scrapers for other sites/APIs.

Key Requirements:
1. Implement search(title, year) method
2. Implement get_details(scene_id) method
3. Return data in the specified format
4. Handle errors gracefully
5. Support SSL/HTTPS connections
6. Implement authentication if required
"""

import json
import ssl
import xbmc

try:
    from urllib import urlencode
    from urllib2 import Request, urlopen, HTTPError, URLError
except ImportError:  # py2 / py3
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError


class TemplateScraperName:
    """Scraper for [Your Site Name Here]"""
    
    def __init__(self, base_url, username=None, password=None, api_key=None):
        """
        Initialize the scraper with configuration.
        
        Args:
            base_url: Base URL of the API (e.g., https://api.example.com)
            username: Optional username for authentication
            password: Optional password for authentication
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.api_key = api_key
        self.session_token = None
        
        # Create SSL context for HTTPS (allows self-signed certificates)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    def _authenticate(self):
        """
        Authenticate with the API and get session token.
        Implement this if your API requires authentication.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Example: POST to /api/login with username/password
            login_url = "{}/api/login".format(self.base_url)
            
            data = urlencode({
                'username': self.username,
                'password': self.password
            }).encode('utf-8')
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            request = Request(login_url, data=data, headers=headers)
            response = urlopen(request, timeout=30, context=self.ssl_context)
            result = json.loads(response.read().decode('utf-8'))
            
            # Extract token from response (adjust based on your API)
            self.session_token = result.get('token') or result.get('session_id')
            return self.session_token is not None
            
        except Exception as e:
            xbmc.log("Authentication error: {}".format(str(e)), xbmc.LOGERROR)
            return False
    
    def _make_request(self, endpoint, params=None, method='GET', data=None):
        """
        Make an authenticated request to the API.
        
        Args:
            endpoint: API endpoint (e.g., 'search', 'scenes/123')
            params: Query parameters as dict
            method: HTTP method (GET, POST, etc.)
            data: Request body data for POST/PUT requests
        
        Returns:
            dict: Parsed JSON response or error dict
        """
        # Authenticate if needed and not already authenticated
        if self.username and not self.session_token:
            if not self._authenticate():
                return {'error': 'Authentication failed'}
        
        try:
            # Build URL
            url = "{}/api/{}".format(self.base_url, endpoint)
            if params:
                url = "{}?{}".format(url, urlencode(params))
            
            # Build headers
            headers = {'Accept': 'application/json'}
            
            # Add authentication header (adjust based on your API)
            if self.session_token:
                headers['Authorization'] = 'Bearer {}'.format(self.session_token)
            elif self.api_key:
                headers['X-API-Key'] = self.api_key
            
            # Prepare request data
            request_data = None
            if data:
                headers['Content-Type'] = 'application/json'
                request_data = json.dumps(data).encode('utf-8')
            
            # Make request
            request = Request(url, data=request_data, headers=headers)
            if method != 'GET':
                request.get_method = lambda: method
            
            response = urlopen(request, timeout=30, context=self.ssl_context)
            result = json.loads(response.read().decode('utf-8'))
            
            return result
            
        except HTTPError as e:
            # Handle 401 Unauthorized - token may have expired
            if e.code == 401 and self.username:
                self.session_token = None
                if self._authenticate():
                    return self._make_request(endpoint, params, method, data)
            
            error_msg = "HTTP Error {}: {}".format(e.code, e.reason)
            xbmc.log("API error: {}".format(error_msg), xbmc.LOGERROR)
            return {'error': error_msg}
            
        except URLError as e:
            error_msg = "Connection error: {}".format(str(e.reason))
            xbmc.log("Connection error: {}".format(error_msg), xbmc.LOGERROR)
            return {'error': error_msg}
            
        except Exception as e:
            error_msg = "Request error: {}".format(str(e))
            xbmc.log("Request error: {}".format(error_msg), xbmc.LOGERROR)
            return {'error': error_msg}
    
    def search(self, title, year=None):
        """
        Search for scenes by title.
        
        Args:
            title: Scene title to search for
            year: Optional year to filter by
        
        Returns:
            list: List of scene dicts with minimal info, or dict with 'error' key
        """
        # Build search parameters
        params = {
            'q': title,
            'type': 'scene',
            'limit': 20
        }
        
        if year:
            params['year'] = year
        
        # Make API request (adjust endpoint to match your API)
        result = self._make_request('search', params)
        
        if 'error' in result:
            return result
        
        # Parse results - adjust based on your API response structure
        scenes = []
        results = result.get('results', []) or result.get('data', []) or result.get('scenes', [])
        
        for item in results:
            scenes.append({
                'id': str(item.get('id', '')),
                'title': item.get('title', 'Untitled'),
                'date': item.get('release_date', '') or item.get('date', ''),
                'image': item.get('thumbnail', '') or item.get('image', ''),
                'studio': self._extract_studio_name(item),
                'performers': self._extract_performer_names(item)
            })
        
        return scenes
    
    def get_details(self, scene_id):
        """
        Get detailed information about a scene.
        
        Args:
            scene_id: ID of the scene
        
        Returns:
            dict: Scene details with info, cast, uniqueids, and available_art
        """
        # Make API request (adjust endpoint to match your API)
        result = self._make_request('scenes/{}'.format(scene_id))
        
        if 'error' in result:
            return result
        
        # Extract scene from response (adjust based on your API structure)
        scene = result.get('scene', {}) or result.get('data', {}) or result
        if not scene:
            return {'error': 'Scene not found'}
        
        # Build info dict - this is the format Kodi expects
        info = {
            'title': scene.get('title', 'Untitled'),
            'originaltitle': scene.get('original_title', scene.get('title', 'Untitled')),
            'plot': scene.get('description', '') or scene.get('synopsis', ''),
            'tagline': scene.get('tagline', ''),
            'studio': [],
            'genre': [],
            'tag': [],
            'director': [],
            'premiered': scene.get('release_date', '') or scene.get('date', '')
        }
        
        # Add duration (convert to seconds if needed)
        if scene.get('duration'):
            duration = scene['duration']
            # If duration is in minutes, convert to seconds
            if duration < 500:  # Assume anything under 500 is minutes
                duration = duration * 60
            info['duration'] = int(duration)
        
        # Add rating (0-10 scale)
        if scene.get('rating'):
            rating = float(scene['rating'])
            # Convert to 0-10 scale if needed
            if rating > 10:
                rating = rating / 10.0
            info['rating'] = rating
        
        # Add studio
        studio_name = self._extract_studio_name(scene)
        if studio_name:
            info['studio'].append(studio_name)
        
        # Add directors
        directors = scene.get('directors', []) or scene.get('director', [])
        if directors:
            if isinstance(directors, list):
                for director in directors:
                    director_name = director.get('name', director) if isinstance(director, dict) else str(director)
                    info['director'].append(director_name)
            else:
                info['director'].append(str(directors))
        
        # Add tags and genres
        tags = scene.get('tags', []) or scene.get('categories', [])
        for tag in tags:
            tag_name = tag.get('name', tag) if isinstance(tag, dict) else str(tag)
            info['tag'].append(tag_name)
            
            # Classify some tags as genres
            if any(keyword in tag_name.lower() for keyword in ['anal', 'oral', 'group']):
                info['genre'].append(tag_name)
        
        # Build cast list
        cast = []
        performers = scene.get('performers', []) or scene.get('models', []) or scene.get('stars', [])
        for idx, performer in enumerate(performers):
            if isinstance(performer, dict):
                cast.append({
                    'name': performer.get('name', 'Unknown'),
                    'role': performer.get('role', ''),
                    'order': idx,
                    'thumbnail': performer.get('image', '') or performer.get('thumbnail', '')
                })
            else:
                cast.append({
                    'name': str(performer),
                    'role': '',
                    'order': idx,
                    'thumbnail': ''
                })
        
        # Build artwork dict
        available_art = self._build_artwork(scene)
        
        # Return in the format expected by scraper.py
        return {
            'info': info,
            'cast': cast,
            'uniqueids': {'yoursite': scene_id},  # Change 'yoursite' to your scraper name
            'available_art': available_art
        }
    
    def _extract_studio_name(self, scene):
        """Helper to extract studio name from scene data"""
        studio = scene.get('studio')
        if studio:
            if isinstance(studio, dict):
                return studio.get('name', '')
            return str(studio)
        return ''
    
    def _extract_performer_names(self, scene):
        """Helper to extract list of performer names"""
        performers = scene.get('performers', []) or scene.get('models', [])
        names = []
        for p in performers:
            if isinstance(p, dict):
                names.append(p.get('name', ''))
            else:
                names.append(str(p))
        return names
    
    def _build_artwork(self, scene):
        """Helper to build artwork dict from scene data"""
        available_art = {}
        
        # Primary image
        primary_image = scene.get('image') or scene.get('thumbnail') or scene.get('poster')
        if primary_image:
            available_art['poster'] = [{'url': primary_image, 'preview': primary_image}]
            available_art['thumb'] = [{'url': primary_image, 'preview': primary_image}]
            available_art['fanart'] = [{'url': primary_image, 'preview': primary_image}]
        
        # Additional images/gallery
        images = scene.get('images', []) or scene.get('gallery', []) or scene.get('screenshots', [])
        for img in images[:15]:  # Limit to 15 images
            img_url = img.get('url', img) if isinstance(img, dict) else str(img)
            if img_url:
                for art_type in ['poster', 'fanart']:
                    if art_type not in available_art:
                        available_art[art_type] = []
                    available_art[art_type].append({
                        'url': img_url,
                        'preview': img_url
                    })
        
        return available_art


# Example usage and testing
if __name__ == '__main__':
    # This allows testing the scraper directly
    scraper = TemplateScraperName(
        base_url='https://api.example.com',
        username='your_username',
        password='your_password'
    )
    
    # Test search
    results = scraper.search('test scene', 2023)
    print("Search results:", json.dumps(results, indent=2))
    
    # Test get_details
    if results and isinstance(results, list) and len(results) > 0:
        scene_id = results[0]['id']
        details = scraper.get_details(scene_id)
        print("Scene details:", json.dumps(details, indent=2))
