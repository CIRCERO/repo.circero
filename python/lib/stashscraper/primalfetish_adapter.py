"""
Primal Fetish Network Scraper Adapter for Kodi
Bridges between PrimalFetish.py and the Kodi addon structure
Supports authenticated access for premium content
"""

import json
import xbmc
import xbmcaddon
from .PrimalFetish import primalfetish

try:
    from ..AyloAPI import AyloAPI
    from ..AyloAPI.scrape import scene_search, scene_from_url
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from AyloAPI import AyloAPI
    from AyloAPI.scrape import scene_search, scene_from_url


class PrimalFetishScraper:
    """Kodi-compatible Primal Fetish Network scraper with authentication support"""
    
    def __init__(self, settings=None):
        self.domains = ['primalfetish', 'primalfetishnetwork']
        self.settings = settings
        self.api = None
        self.is_authenticated = False
        
        # Try to authenticate if credentials are available
        self._init_auth()
    
    def _init_auth(self):
        """Initialize authentication with stored credentials"""
        try:
            if not self.settings:
                self.settings = xbmcaddon.Addon()
            
            username = self.settings.getSettingString('primalfetish_username')
            password = self.settings.getSettingString('primalfetish_password')
            
            if username and password:
                xbmc.log("PrimalFetish: Attempting authentication...", xbmc.LOGINFO)
                self.api = AyloAPI(username=username, password=password, site='primalfetish')
                
                if self.api.login():
                    self.is_authenticated = True
                    xbmc.log("PrimalFetish: Authentication successful - premium access enabled", xbmc.LOGINFO)
                else:
                    xbmc.log("PrimalFetish: Authentication failed - using public access", xbmc.LOGWARNING)
                    self.api = AyloAPI()
            else:
                xbmc.log("PrimalFetish: No credentials configured - using public access", xbmc.LOGINFO)
                self.api = AyloAPI()
                
        except Exception as e:
            xbmc.log("PrimalFetish: Auth init error - {}".format(str(e)), xbmc.LOGERROR)
            self.api = AyloAPI()
    
    def search(self, title, year=None):
        """Search for scenes"""
        try:
            # Use the Primal Fetish-specific search
            result = scene_search(title, search_domains=self.domains, postprocess=primalfetish)
            
            if isinstance(result, dict) and 'error' in result:
                return result
            
            # Convert to Kodi format
            scenes = []
            if isinstance(result, list):
                for item in result:
                    scenes.append({
                        'id': item.get('id', ''),
                        'title': item.get('title', 'Untitled'),
                        'date': item.get('date', ''),
                        'image': item.get('image', ''),
                        'studio': item.get('studio', {}).get('name', 'Primal Fetish Network') if isinstance(item.get('studio'), dict) else 'Primal Fetish Network'
                    })
            
            return scenes
            
        except Exception as e:
            xbmc.log("Primal Fetish search error: {}".format(str(e)), xbmc.LOGERROR)
            return {'error': str(e)}
    
    def get_details(self, scene_id):
        """Get scene details with premium content if authenticated"""
        try:
            # Construct URL from ID
            url = "https://www.primalfetishnetwork.com/scene/{}".format(scene_id)
            result = scene_from_url(url, postprocess=primalfetish)
            
            if isinstance(result, dict) and 'error' in result:
                return result
            
            # Convert to Kodi format
            info = {
                'title': result.get('title', 'Untitled'),
                'originaltitle': result.get('title', 'Untitled'),
                'plot': result.get('description', ''),
                'tagline': result.get('url', ''),
                'studio': [],
                'genre': [],
                'tag': [],
                'director': [],
                'premiered': result.get('date', '')
            }
            
            # Add duration
            if result.get('duration'):
                info['duration'] = int(result['duration'])
            
            # Add studio
            studio = result.get('studio', {})
            if isinstance(studio, dict):
                studio_name = studio.get('name', 'Primal Fetish Network')
                info['studio'].append(studio_name)
                
                # Add parent studio if present
                parent = studio.get('parent', {})
                if isinstance(parent, dict) and parent.get('name'):
                    parent_name = parent['name']
                    if parent_name and parent_name != studio_name:
                        info['studio'].append(parent_name)
            else:
                info['studio'].append('Primal Fetish Network')
            
            # Add tags
            for tag in result.get('tags', []):
                if isinstance(tag, str):
                    info['tag'].append(tag)
                elif isinstance(tag, dict):
                    info['tag'].append(tag.get('name', ''))
            
            # Build cast
            cast = []
            performers = result.get('performers', [])
            for idx, performer in enumerate(performers):
                if isinstance(performer, dict):
                    cast.append({
                        'name': performer.get('name', 'Unknown'),
                        'role': '',
                        'order': idx,
                        'thumbnail': performer.get('image', '')
                    })
            
            # Build available art - use higher quality if authenticated
            available_art = {}
            images = result.get('images', [])
            
            if images:
                # Primary images
                primary = images[0] if images else None
                if primary:
                    available_art['poster'] = primary
                    available_art['thumb'] = primary
                    available_art['fanart'] = primary
                
                # All images for selection
                available_art['poster_list'] = images[:10]
                available_art['fanart_list'] = images[:10]
                available_art['thumb_list'] = images[:10]
            
            # If authenticated, try to get higher quality images
            if self.is_authenticated:
                try:
                    premium_images = self._get_premium_images(scene_id)
                    if premium_images:
                        xbmc.log("PrimalFetish: Retrieved {} premium images".format(len(premium_images)), xbmc.LOGINFO)
                        # Override with premium images
                        if premium_images:
                            available_art['poster'] = premium_images[0]
                            available_art['thumb'] = premium_images[0]
                            if len(premium_images) > 1:
                                available_art['fanart'] = premium_images[1]
                            available_art['poster_list'] = premium_images
                            available_art['fanart_list'] = premium_images
                            available_art['thumb_list'] = premium_images
                except Exception as e:
                    xbmc.log("PrimalFetish: Error getting premium images - {}".format(str(e)), xbmc.LOGWARNING)
            
            return {
                'info': info,
                'cast': cast,
                'uniqueids': {'primalfetish': scene_id},
                'available_art': available_art
            }
            
        except Exception as e:
            xbmc.log("Primal Fetish get_details error: {}".format(str(e)), xbmc.LOGERROR)
            return {'error': str(e)}
    
    def _get_premium_images(self, scene_id):
        """Get high-quality images using authenticated API"""
        if not self.is_authenticated or not self.api:
            return []
        
        try:
            # Make authenticated request for scene details
            result = self.api._make_request('scenes/{}'.format(scene_id))
            
            if 'error' in result:
                return []
            
            images = []
            data = result.get('data', result)
            
            # Extract high-res images
            if data.get('images'):
                img_data = data['images']
                # Try to get highest quality versions
                for quality in ['full', 'large', 'medium', 'poster', 'thumb']:
                    if img_data.get(quality):
                        img_url = img_data[quality]
                        if isinstance(img_url, dict):
                            img_url = img_url.get('url', '')
                        if img_url and img_url not in images:
                            images.append(img_url)
            
            # Also check for gallery images
            if data.get('gallery'):
                for img in data['gallery'][:15]:
                    img_url = img.get('url', '') if isinstance(img, dict) else str(img)
                    if img_url and img_url not in images:
                        images.append(img_url)
            
            return images
            
        except Exception as e:
            xbmc.log("PrimalFetish: Premium images error - {}".format(str(e)), xbmc.LOGERROR)
            return []
    
    def get_stream_url(self, scene_id, quality='1080p'):
        """Get video stream URL (requires authentication)"""
        if not self.is_authenticated:
            xbmc.log("PrimalFetish: Stream URL requires authentication", xbmc.LOGWARNING)
            return None
        
        try:
            result = self.api._make_request('scenes/{}/stream'.format(scene_id))
            
            if 'error' in result:
                return None
            
            data = result.get('data', result)
            
            # Get stream URL for requested quality
            streams = data.get('streams', {})
            if quality in streams:
                return streams[quality]
            
            # Fallback to any available quality
            for q in ['1080p', '720p', '480p', '360p']:
                if q in streams:
                    return streams[q]
            
            return None
            
        except Exception as e:
            xbmc.log("PrimalFetish: Stream URL error - {}".format(str(e)), xbmc.LOGERROR)
            return None


# Convenience function for direct use
def get_scraper(settings=None):
    """Factory function to create scraper instance"""
    return PrimalFetishScraper(settings)
