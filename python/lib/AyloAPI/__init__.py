"""
AyloAPI - Aylo (MindGeek) Network Scraper
Self-contained implementation for Kodi addon

Supports scraping from Aylo/MindGeek network sites including:
- Brazzers
- FakeHub (FakeHub, FakeTaxi, FakeHostel, PublicAgent)
- Czech Hunter (CzechHunter, DebtDandy, DirtyScout)
- Gay Wire
- Primal Fetish Network
"""

import json
import ssl
import sys
import xbmc

try:
    from urllib import urlencode
    from urllib2 import Request, urlopen, HTTPError, URLError
except ImportError:  # py2 / py3
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError


class AyloAPI:
    """Core API client for Aylo/MindGeek network"""
    
    # Base API URL
    API_BASE = "https://site-api.project1service.com/v2"
    
    # Authentication endpoints for different sites
    AUTH_ENDPOINTS = {
        'primalfetish': 'https://www.primalfetishnetwork.com/api/auth/login',
        'primalfetishnetwork': 'https://www.primalfetishnetwork.com/api/auth/login',
        'brazzers': 'https://www.brazzers.com/api/auth/login',
    }
    
    # Domain mappings
    DOMAIN_MAP = {
        'brazzers': 'brazzers.com',
        'fakehub': 'fakehub.com',
        'fakehostel': 'fakehostel.com',
        'faketaxi': 'faketaxi.com',
        'publicagent': 'publicagent.com',
        'czechhunter': 'bigstr.com',
        'debtdandy': 'bigstr.com',
        'dirtyscout': 'bigstr.com',
        'gaywire': 'gaywire.com',
        'guyselector': 'guyselector.com',
        'primalfetish': 'primalfetishnetwork.com',
        'primalfetishnetwork': 'primalfetishnetwork.com'
    }
    
    def __init__(self, username=None, password=None, site=None):
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        self.username = username
        self.password = password
        self.site = site
        self.auth_token = None
        self.is_authenticated = False
    
    def login(self, username=None, password=None, site=None):
        """
        Authenticate with the site to get premium access.
        
        Args:
            username: Account username/email
            password: Account password
            site: Site name (e.g., 'primalfetish')
            
        Returns:
            bool: True if login successful
        """
        if username:
            self.username = username
        if password:
            self.password = password
        if site:
            self.site = site
        
        if not self.username or not self.password:
            xbmc.log("AyloAPI: No credentials provided", xbmc.LOGWARNING)
            return False
        
        auth_url = self.AUTH_ENDPOINTS.get(self.site)
        if not auth_url:
            xbmc.log("AyloAPI: No auth endpoint for site: {}".format(self.site), xbmc.LOGWARNING)
            return False
        
        try:
            xbmc.log("AyloAPI: Attempting login to {}".format(self.site), xbmc.LOGINFO)
            
            login_data = json.dumps({
                'email': self.username,
                'password': self.password
            }).encode('utf-8')
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            request = Request(auth_url, data=login_data, headers=headers)
            response = urlopen(request, timeout=30, context=self.ssl_context)
            result = json.loads(response.read().decode('utf-8'))
            
            # Extract token from response
            if result.get('token') or result.get('access_token') or result.get('jwt'):
                self.auth_token = result.get('token') or result.get('access_token') or result.get('jwt')
                self.is_authenticated = True
                xbmc.log("AyloAPI: Login successful", xbmc.LOGINFO)
                return True
            else:
                xbmc.log("AyloAPI: Login response missing token", xbmc.LOGWARNING)
                return False
                
        except HTTPError as e:
            xbmc.log("AyloAPI: Login failed - HTTP {}: {}".format(e.code, e.reason), xbmc.LOGERROR)
            return False
        except Exception as e:
            xbmc.log("AyloAPI: Login error - {}".format(str(e)), xbmc.LOGERROR)
            return False
    
    def _make_request(self, endpoint, params=None):
        """Make API request"""
        try:
            url = "{}/{}".format(self.API_BASE, endpoint)
            if params:
                url = "{}?{}".format(url, urlencode(params))
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            # Add auth token if authenticated
            if self.auth_token:
                headers['Authorization'] = 'Bearer {}'.format(self.auth_token)
            
            request = Request(url, headers=headers)
            response = urlopen(request, timeout=30, context=self.ssl_context)
            return json.loads(response.read().decode('utf-8'))
            
        except HTTPError as e:
            xbmc.log("AyloAPI HTTP Error {}: {}".format(e.code, e.reason), xbmc.LOGERROR)
            return {'error': 'HTTP {}'.format(e.code)}
        except Exception as e:
            xbmc.log("AyloAPI Error: {}".format(str(e)), xbmc.LOGERROR)
            return {'error': str(e)}
    
    def search_scenes(self, query, domains=None):
        """Search for scenes across domains"""
        params = {
            'search': query,
            'limit': 20
        }
        
        if domains:
            params['sites'] = ','.join([self.DOMAIN_MAP.get(d, d) for d in domains])
        
        result = self._make_request('scenes', params)
        
        if 'error' in result:
            return result
        
        scenes = []
        for item in result.get('data', []):
            scenes.append(self._parse_scene_summary(item))
        
        return scenes
    
    def get_scene(self, scene_id):
        """Get detailed scene information"""
        result = self._make_request('scenes/{}'.format(scene_id))
        
        if 'error' in result:
            return result
        
        return self._parse_scene_detail(result.get('data', {}))
    
    def get_scene_by_url(self, url):
        """Get scene by URL"""
        # Extract scene ID or slug from URL
        parts = url.rstrip('/').split('/')
        if len(parts) >= 2:
            scene_identifier = parts[-1]
            return self.get_scene(scene_identifier)
        return {'error': 'Invalid URL'}
    
    def search_performers(self, query, domains=None):
        """Search for performers"""
        params = {
            'search': query,
            'limit': 20
        }
        
        if domains:
            params['sites'] = ','.join([self.DOMAIN_MAP.get(d, d) for d in domains])
        
        result = self._make_request('models', params)
        
        if 'error' in result:
            return result
        
        performers = []
        for item in result.get('data', []):
            performers.append(self._parse_performer_summary(item))
        
        return performers
    
    def get_performer(self, performer_id):
        """Get detailed performer information"""
        result = self._make_request('models/{}'.format(performer_id))
        
        if 'error' in result:
            return result
        
        return self._parse_performer_detail(result.get('data', {}))
    
    def _parse_scene_summary(self, data):
        """Parse scene search result"""
        return {
            'id': str(data.get('id', '')),
            'title': data.get('title', 'Untitled'),
            'url': data.get('url', ''),
            'date': data.get('release_date', ''),
            'image': self._get_best_image(data.get('images', {})),
            'studio': {
                'name': data.get('site', {}).get('name', ''),
                'url': data.get('site', {}).get('url', '')
            },
            'performers': [
                {'name': p.get('name', ''), 'url': p.get('url', '')}
                for p in data.get('models', [])
            ]
        }
    
    def _parse_scene_detail(self, data):
        """Parse detailed scene data"""
        # Extract tags/categories
        tags = []
        for tag in data.get('tags', []):
            if isinstance(tag, dict):
                tags.append(tag.get('name', ''))
            else:
                tags.append(str(tag))
        
        # Extract performers with details
        performers = []
        for p in data.get('models', []):
            performers.append({
                'name': p.get('name', ''),
                'url': p.get('url', ''),
                'image': self._get_best_image(p.get('images', {}))
            })
        
        return {
            'id': str(data.get('id', '')),
            'title': data.get('title', 'Untitled'),
            'description': data.get('description', ''),
            'url': data.get('url', ''),
            'date': data.get('release_date', ''),
            'duration': data.get('duration', 0),
            'studio': {
                'name': data.get('site', {}).get('name', ''),
                'parent': {'name': data.get('network', {}).get('name', '')},
                'url': data.get('site', {}).get('url', '')
            },
            'tags': tags,
            'performers': performers,
            'images': self._get_all_images(data.get('images', {}))
        }
    
    def _parse_performer_summary(self, data):
        """Parse performer search result"""
        return {
            'name': data.get('name', ''),
            'url': data.get('url', ''),
            'image': self._get_best_image(data.get('images', {}))
        }
    
    def _parse_performer_detail(self, data):
        """Parse detailed performer data"""
        return {
            'name': data.get('name', ''),
            'url': data.get('url', ''),
            'images': self._get_all_images(data.get('images', {})),
            'bio': data.get('bio', ''),
            'birthdate': data.get('birthdate', ''),
            'measurements': data.get('measurements', '')
        }
    
    def _get_best_image(self, images):
        """Get the best quality image from images dict"""
        if not images:
            return ''
        
        # Priority: poster > listing > thumb
        for key in ['poster', 'listing', 'thumb', 'screenshot']:
            if key in images and images[key]:
                img = images[key]
                if isinstance(img, list) and img:
                    return img[0].get('url', '') if isinstance(img[0], dict) else str(img[0])
                elif isinstance(img, dict):
                    return img.get('url', '')
                elif isinstance(img, str):
                    return img
        
        return ''
    
    def _get_all_images(self, images):
        """Get all images from images dict"""
        all_imgs = []
        if not images:
            return all_imgs
        
        for _, value in images.items():
            if isinstance(value, list):
                for img in value:
                    url = img.get('url', '') if isinstance(img, dict) else str(img)
                    if url:
                        all_imgs.append(url)
            elif isinstance(value, dict):
                url = value.get('url', '')
                if url:
                    all_imgs.append(url)
            elif isinstance(value, str) and value:
                all_imgs.append(value)
        
        return all_imgs


# Global API instance
_api = AyloAPI()


def scraper_args():
    """Parse command-line arguments for scrapers"""
    if len(sys.argv) < 2:
        return None, {}
    
    operation = sys.argv[1]
    args = {}
    
    # Parse remaining args as JSON if provided
    if len(sys.argv) > 2:
        try:
            args = json.loads(sys.argv[2])
        except (json.JSONDecodeError, ValueError):
            # Fall back to simple key=value parsing
            for arg in sys.argv[2:]:
                if '=' in arg:
                    key, value = arg.split('=', 1)
                    args[key] = value
    
    return operation, args


def scene_search(name, search_domains=None, postprocess=None):
    """Search for scenes by name"""
    result = _api.search_scenes(name, search_domains)
    
    if postprocess and not isinstance(result, dict) or 'error' not in result:
        if isinstance(result, list):
            result = [postprocess(item, _api) for item in result]
        else:
            result = postprocess(result, _api)
    
    return result


def scene_from_url(url, postprocess=None):
    """Get scene from URL"""
    result = _api.get_scene_by_url(url)
    
    if postprocess and (not isinstance(result, dict) or 'error' not in result):
        result = postprocess(result, _api)
    
    return result


def scene_from_fragment(args, search_domains=None, postprocess=None):
    """Get scene from fragment/args"""
    if 'url' in args:
        return scene_from_url(args['url'], postprocess)
    elif 'name' in args or 'title' in args:
        name = args.get('name') or args.get('title')
        return scene_search(name, search_domains, postprocess)
    return {'error': 'No URL or name provided'}


def performer_search(name, search_domains=None, postprocess=None):
    """Search for performers by name"""
    result = _api.search_performers(name, search_domains)
    
    if postprocess and (not isinstance(result, dict) or 'error' not in result):
        if isinstance(result, list):
            result = [postprocess(item, _api) for item in result]
        else:
            result = postprocess(result, _api)
    
    return result


def performer_from_url(url, postprocess=None):
    """Get performer from URL"""
    parts = url.rstrip('/').split('/')
    if len(parts) >= 2:
        performer_id = parts[-1]
        result = _api.get_performer(performer_id)
        
        if postprocess and (not isinstance(result, dict) or 'error' not in result):
            result = postprocess(result, _api)
        
        return result
    return {'error': 'Invalid URL'}


def performer_from_fragment(args, postprocess=None):
    """Get performer from fragment/args"""
    if 'url' in args:
        return performer_from_url(args['url'], postprocess)
    elif 'name' in args:
        results = performer_search(args['name'], postprocess=postprocess)
        return results[0] if results and isinstance(results, list) else results
    return {'error': 'No URL or name provided'}


def movie_from_url(url, postprocess=None):
    """Get movie/series from URL (stub - not commonly used)"""
    return {'error': 'Movie API not implemented'}


def gallery_from_url(url, postprocess=None):
    """Get gallery from URL"""
    # Galleries are typically part of scenes
    return scene_from_url(url, postprocess)


def gallery_from_fragment(args, search_domains=None, postprocess=None):
    """Get gallery from fragment"""
    return scene_from_fragment(args, search_domains, postprocess)
