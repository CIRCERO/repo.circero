"""
FakeHub Scraper Adapter for Kodi
Bridges between FakeHub.py and the Kodi addon structure
"""

import xbmc
from .FakeHub import fakehub

try:
    from ..AyloAPI.scrape import scene_search, scene_from_url
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from AyloAPI.scrape import scene_search, scene_from_url


class FakeHubScraper:
    """Kodi-compatible FakeHub scraper"""
    
    def __init__(self):
        self.domains = ['fakehub', 'fakehostel', 'faketaxi', 'publicagent']
    
    def search(self, title, year=None):
        """Search for scenes"""
        try:
            result = scene_search(title, search_domains=self.domains, postprocess=fakehub)
            
            if isinstance(result, dict) and 'error' in result:
                return result
            
            scenes = []
            if isinstance(result, list):
                for item in result:
                    scenes.append({
                        'id': item.get('id', ''),
                        'title': item.get('title', 'Untitled'),
                        'date': item.get('date', ''),
                        'image': item.get('image', ''),
                        'studio': item.get('studio', {}).get('name', 'FakeHub') if isinstance(item.get('studio'), dict) else 'FakeHub'
                    })
            
            return scenes
            
        except Exception as e:
            xbmc.log("FakeHub search error: {}".format(str(e)), xbmc.LOGERROR)
            return {'error': str(e)}
    
    def get_details(self, scene_id):
        """Get scene details"""
        try:
            url = "https://www.fakehub.com/scene/{}".format(scene_id)
            result = scene_from_url(url, postprocess=fakehub)
            
            if isinstance(result, dict) and 'error' in result:
                return result
            
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
            
            if result.get('duration'):
                info['duration'] = int(result['duration'])
            
            studio = result.get('studio', {})
            if isinstance(studio, dict):
                info['studio'].append(studio.get('name', 'FakeHub'))
            else:
                info['studio'].append('FakeHub')
            
            for tag in result.get('tags', []):
                info['tag'].append(tag)
            
            cast = []
            for idx, performer in enumerate(result.get('performers', [])):
                if isinstance(performer, dict):
                    cast.append({
                        'name': performer.get('name', 'Unknown'),
                        'role': '',
                        'order': idx,
                        'thumbnail': performer.get('image', '')
                    })
            
            available_art = {}
            images = result.get('images', [])
            if images:
                primary = images[0]
                available_art['poster'] = [{'url': primary, 'preview': primary}]
                available_art['thumb'] = [{'url': primary, 'preview': primary}]
                available_art['fanart'] = [{'url': primary, 'preview': primary}]
                
                for img in images[:15]:
                    for art_type in ['poster', 'fanart']:
                        if art_type not in available_art:
                            available_art[art_type] = []
                        available_art[art_type].append({'url': img, 'preview': img})
            
            return {
                'info': info,
                'cast': cast,
                'uniqueids': {'fakehub': scene_id},
                'available_art': available_art
            }
            
        except Exception as e:
            xbmc.log("FakeHub details error: {}".format(str(e)), xbmc.LOGERROR)
            return {'error': str(e)}
