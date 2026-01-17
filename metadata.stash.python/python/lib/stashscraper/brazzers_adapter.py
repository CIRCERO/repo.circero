"""
Brazzers Scraper Adapter for Kodi
Bridges between Brazzers.py and the Kodi addon structure
"""

import xbmc
from .Brazzers import brazzers

try:
    from ..AyloAPI.scrape import scene_search, scene_from_url
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from AyloAPI.scrape import scene_search, scene_from_url


class BrazzersScraper:
    """Kodi-compatible Brazzers scraper"""
    
    def __init__(self):
        self.domains = ['brazzers']
    
    def search(self, title, year=None):
        """Search for scenes"""
        try:
            # Use the Brazzers-specific search
            result = scene_search(title, search_domains=self.domains, postprocess=brazzers)
            
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
                        'studio': item.get('studio', {}).get('name', 'Brazzers') if isinstance(item.get('studio'), dict) else 'Brazzers'
                    })
            
            return scenes
            
        except Exception as e:
            xbmc.log("Brazzers search error: {}".format(str(e)), xbmc.LOGERROR)
            return {'error': str(e)}
    
    def get_details(self, scene_id):
        """Get scene details"""
        try:
            # Construct URL from ID
            url = "https://www.brazzers.com/video/{}".format(scene_id)
            result = scene_from_url(url, postprocess=brazzers)
            
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
                studio_name = studio.get('name', 'Brazzers')
                info['studio'].append(studio_name)
            else:
                info['studio'].append('Brazzers')
            
            # Add tags
            for tag in result.get('tags', []):
                info['tag'].append(tag)
            
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
            
            # Build artwork
            available_art = {}
            images = result.get('images', [])
            if images:
                primary = images[0] if images else None
                if primary:
                    available_art['poster'] = [{'url': primary, 'preview': primary}]
                    available_art['thumb'] = [{'url': primary, 'preview': primary}]
                    available_art['fanart'] = [{'url': primary, 'preview': primary}]
                
                # Add additional images
                for img in images[:15]:
                    for art_type in ['poster', 'fanart']:
                        if art_type not in available_art:
                            available_art[art_type] = []
                        available_art[art_type].append({'url': img, 'preview': img})
            
            return {
                'info': info,
                'cast': cast,
                'uniqueids': {'brazzers': scene_id},
                'available_art': available_art
            }
            
        except Exception as e:
            xbmc.log("Brazzers details error: {}".format(str(e)), xbmc.LOGERROR)
            return {'error': str(e)}
