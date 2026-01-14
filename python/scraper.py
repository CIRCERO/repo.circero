# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import json
import sys
import os
import re
import tempfile
from xml.etree import ElementTree as ET
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

try:
    import xbmcvfs
except ImportError:
    xbmcvfs = None

try:
    from lib.stashscraper.stash import StashScraper
    from lib.stashscraper.aebn import AEBNScraper
    from lib.stashscraper.brazzers_adapter import BrazzersScraper
    from lib.stashscraper.fakehub_adapter import FakeHubScraper
    from lib.stashscraper.czechhunter_adapter import CzechHunterScraper
    from lib.stashscraper.gaywire_adapter import GayWireScraper
    from lib.stashscraper.primalfetish_adapter import PrimalFetishScraper
    from lib.stashscraper.web_image_search import WebImageSearch
    from lib.stashscraper.rapidgator import prompt_rapidgator_search
    from scraper_datahelper import get_params
    from scraper_config import configure_scraped_details
    IMPORT_SUCCESS = True
    IMPORT_ERROR = None
except Exception as e:
    IMPORT_SUCCESS = False
    IMPORT_ERROR = str(e)
    # Define dummy classes to prevent further errors
    class StashScraper: pass
    class AEBNScraper: pass
    class BrazzersScraper: pass
    class FakeHubScraper: pass
    class CzechHunterScraper: pass
    class GayWireScraper: pass
    class PrimalFetishScraper: pass
    def get_params(args): return {}
    def configure_scraped_details(details, settings): return details
    def prompt_rapidgator_search(details, settings): return None

ADDON_SETTINGS = xbmcaddon.Addon()
ID = ADDON_SETTINGS.getAddonInfo('id')

def log(msg, level=xbmc.LOGDEBUG):
    xbmc.log(msg='[{addon}]: {msg}'.format(addon=ID, msg=msg), level=level)

# Log import status
if not IMPORT_SUCCESS:
    log("CRITICAL: Import failed: {}".format(IMPORT_ERROR), xbmc.LOGERROR)
else:
    log("All imports successful", xbmc.LOGINFO)

def get_stash_scraper(settings):
    stash_url = settings.getSettingString('stash_url')
    api_key = settings.getSettingString('api_key')
    return StashScraper(stash_url, api_key, settings)

def get_aebn_scraper(settings):
    aebn_url = settings.getSettingString('aebn_url')
    username = settings.getSettingString('aebn_username')
    password = settings.getSettingString('aebn_password')
    return AEBNScraper(aebn_url, username, password)

def get_active_scraper(settings):
    """Get the active scraper based on settings"""
    if not IMPORT_SUCCESS:
        log("Cannot create scraper - imports failed: {}".format(IMPORT_ERROR), xbmc.LOGERROR)
        raise ImportError("Scraper imports failed: {}".format(IMPORT_ERROR))
    
    scraper_type = settings.getSettingString('scraper_type')
    log("Creating scraper of type: {}".format(scraper_type), xbmc.LOGINFO)
    
    try:
        if scraper_type == 'aebn':
            return get_aebn_scraper(settings), 'aebn'
        elif scraper_type == 'brazzers':
            return BrazzersScraper(), 'brazzers'
        elif scraper_type == 'fakehub':
            return FakeHubScraper(), 'fakehub'
        elif scraper_type == 'czechhunter':
            return CzechHunterScraper(), 'czechhunter'
        elif scraper_type == 'gaywire':
            return GayWireScraper(), 'gaywire'
        elif scraper_type == 'primalfetish':
            return PrimalFetishScraper(settings), 'primalfetish'
        else:
            return get_stash_scraper(settings), 'stash'
    except Exception as e:
        log("Error creating scraper '{}': {}".format(scraper_type, str(e)), xbmc.LOGERROR)
        raise

def search_for_movie(title, year, handle, settings):
    log("Find movie/scene with title '{title}' from year '{year}'".format(title=title, year=year), xbmc.LOGINFO)
    
    try:
        scraper, scraper_type = get_active_scraper(settings)
    except Exception as e:
        error_msg = "Failed to initialize scraper: {}".format(str(e))
        log(error_msg, xbmc.LOGERROR)
        xbmcgui.Dialog().notification("Stash Scraper Error", error_msg, xbmcgui.NOTIFICATION_ERROR)
        return

    try:
        search_results = scraper.search(title, year)
    except Exception as e:
        error_msg = "Search failed: {}".format(str(e))
        log(error_msg, xbmc.LOGERROR)
        xbmcgui.Dialog().notification("Stash Scraper Error", error_msg, xbmcgui.NOTIFICATION_ERROR)
        return
    
    if not search_results:
        log("No results found for '{title}'".format(title=title), xbmc.LOGINFO)
        return

    if 'error' in search_results:
        header = "{} Scraper error searching instance".format(scraper_type.upper())
        xbmcgui.Dialog().notification(header, search_results['error'], xbmcgui.NOTIFICATION_WARNING)
        log(header + ': ' + search_results['error'], xbmc.LOGWARNING)
        return

    for scene in search_results:
        listitem = _searchresult_to_listitem(scene)
        uniqueids = {scraper_type: str(scene['id'])}
        xbmcplugin.addDirectoryItem(handle=handle, url=build_lookup_string(uniqueids),
            listitem=listitem, isFolder=True)

def _searchresult_to_listitem(scene):
    scene_label = scene['title']

    scene_date = scene.get('date', '')
    if scene_date:
        scene_label += ' ({})'.format(scene_date)

    listitem = xbmcgui.ListItem(scene_label, offscreen=True)

    infotag = listitem.getVideoInfoTag()
    infotag.setTitle(scene['title'])
    if scene_date:
        try:
            year = int(scene_date.split('-')[0])
            infotag.setYear(year)
        except (ValueError, IndexError):
            pass

    if scene.get('image'):
        listitem.setArt({'thumb': scene['image']})

    return listitem

def get_details(input_uniqueids, handle, settings, fail_silently=False):
    if not input_uniqueids:
        return False
    
    # Determine which scraper to use based on uniqueid
    scraper_type = None
    scene_id = None
    
    if 'stash' in input_uniqueids:
        scraper_type = 'stash'
        scene_id = input_uniqueids['stash']
        scraper = get_stash_scraper(settings)
    elif 'aebn' in input_uniqueids:
        scraper_type = 'aebn'
        scene_id = input_uniqueids['aebn']
        scraper = get_aebn_scraper(settings)
    elif 'brazzers' in input_uniqueids:
        scraper_type = 'brazzers'
        scene_id = input_uniqueids['brazzers']
        scraper = BrazzersScraper()
    elif 'fakehub' in input_uniqueids:
        scraper_type = 'fakehub'
        scene_id = input_uniqueids['fakehub']
        scraper = FakeHubScraper()
    elif 'czechhunter' in input_uniqueids:
        scraper_type = 'czechhunter'
        scene_id = input_uniqueids['czechhunter']
        scraper = CzechHunterScraper()
    elif 'gaywire' in input_uniqueids:
        scraper_type = 'gaywire'
        scene_id = input_uniqueids['gaywire']
        scraper = GayWireScraper()
    elif 'primalfetish' in input_uniqueids:
        scraper_type = 'primalfetish'
        scene_id = input_uniqueids['primalfetish']
        scraper = PrimalFetishScraper()
    else:
        return False
    
    # Check if auto-scraping from external sources is enabled (only for Stash)
    if scraper_type == 'stash' and settings.getSettingBool('auto_scrape_external'):
        log("Auto-scraping enabled, attempting to scrape from external sources", xbmc.LOGINFO)
        
        # Get scraper source preference
        scraper_source = settings.getSettingString('scraper_source')
        if not scraper_source:
            scraper_source = 'stashdb'  # Default to StashDB
        
        scraped_data = None
        source_name = scraper_source.upper()
        
        # Try primary source
        log("Attempting to scrape from {}".format(source_name), xbmc.LOGINFO)
        scraped_data = scraper.scrape_scene(scene_id, scraper_source)
        
        # If primary fails and fallback is enabled, try alternative
        if (not scraped_data or 'error' in scraped_data) and settings.getSettingBool('fallback_scraper'):
            fallback_source = 'tpdb' if scraper_source == 'stashdb' else 'stashdb'
            log("Primary source failed, trying fallback: {}".format(fallback_source.upper()), xbmc.LOGINFO)
            scraped_data = scraper.scrape_scene(scene_id, fallback_source)
            if scraped_data and 'error' not in scraped_data:
                source_name = fallback_source.upper()
        
        if scraped_data and 'error' not in scraped_data:
            log("Successfully scraped from {}, updating scene".format(source_name), xbmc.LOGINFO)
            
            # Ask user if they want to apply the scraped data
            if settings.getSettingBool('confirm_scrape'):
                dialog = xbmcgui.Dialog()
                title = scraped_data.get('title', 'Unknown')
                studio_obj = scraped_data.get('studio')
                studio = studio_obj.get('name', 'Unknown') if isinstance(studio_obj, dict) else 'Unknown'
                message = "Found match on {}:\n{}\nStudio: {}\n\nApply this metadata?".format(
                    source_name, title, studio)
                
                if dialog.yesno("Stash Scraper - Confirm", message):
                    update_result = scraper.update_scene(scene_id, scraped_data)
                    if update_result and 'error' not in update_result:
                        xbmcgui.Dialog().notification("Stash Scraper", 
                                                    "Scene updated from {}".format(source_name), 
                                                    xbmcgui.NOTIFICATION_INFO)
                    else:
                        log("Failed to update scene: {}".format(update_result.get('error', 'Unknown error')), 
                            xbmc.LOGWARNING)
            else:
                # Auto-apply without confirmation
                scraper.update_scene(scene_id, scraped_data)
                xbmcgui.Dialog().notification("Stash Scraper", 
                                            "Scene updated from {}".format(source_name), 
                                            xbmcgui.NOTIFICATION_INFO)
        else:
            error_msg = scraped_data.get('error', 'No results') if scraped_data else 'No results'
            log("No external scrape results: {}".format(error_msg), xbmc.LOGINFO)
    
    # Now get the details (possibly updated) from Stash
    details = scraper.get_details(scene_id)
    if not details:
        return False
    
    if 'error' in details:
        if fail_silently:
            return False
        header = "Stash Scraper error with Stash instance"
        xbmcgui.Dialog().notification(header, details['error'], xbmcgui.NOTIFICATION_WARNING)
        log(header + ': ' + details['error'], xbmc.LOGWARNING)
        return False

    details = configure_scraped_details(details, settings)

    # Add web image search if enabled
    if settings.getSettingBool('enable_web_image_search'):
        details = add_web_images(details, settings)

    # Offer frame extraction if enabled
    if settings.getSettingBool('enable_frame_extraction') and settings.getSettingBool('frame_prompt_on_scrape'):
        details = prompt_frame_extraction(details, settings, handle)

    # Offer Rapidgator search for higher quality version
    if settings.getSettingBool('enable_rapidgator'):
        downloaded_path = prompt_rapidgator_search(details, settings)
        if downloaded_path:
            log("Rapidgator download completed: {}".format(downloaded_path), xbmc.LOGINFO)
            # Store the downloaded file path in details for potential use
            details['rapidgator_download'] = downloaded_path

    listitem = xbmcgui.ListItem(details['info']['title'], offscreen=True)
    infotag = listitem.getVideoInfoTag()
    set_info(infotag, details['info'])
    infotag.setCast(build_cast(details.get('cast', [])))
    infotag.setUniqueIDs(details['uniqueids'], scraper_type)
    
    if details.get('available_art'):
        set_artwork(listitem, details['available_art'])

    # Create NFO file if enabled
    if settings.getSettingBool('create_nfo'):
        create_nfo_file(details, settings)

    xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=listitem)
    return True
    
def normalize_details(details, scraper_type):
    """
    Enforce a canonical schema across all scrapers.
    """
    if not isinstance(details, dict):
        return {"error": "Invalid scraper response"}

    details.setdefault("info", {})
    details.setdefault("cast", [])
    details.setdefault("uniqueids", {})
    details.setdefault("available_art", {})

    # Ensure unique ID exists
    if scraper_type not in details["uniqueids"]:
        details["uniqueids"][scraper_type] = details["uniqueids"].get("stash", "")

    # Normalize artwork → URL only
    def norm_art(v):
        if isinstance(v, list) and v:
            v = v[0]
        if isinstance(v, dict):
            return v.get("url") or v.get("preview")
        return v

    for k in ("poster", "thumb", "fanart"):
        if k in details["available_art"]:
            details["available_art"][k] = norm_art(details["available_art"][k])

    # Normalize cast
    clean_cast = []
    for c in details.get("cast", []):
        if not c.get("name"):
            continue
        clean_cast.append({
            "name": c.get("name"),
            "role": c.get("role", ""),
            "order": int(c.get("order", 0)),
            "thumbnail": c.get("thumbnail", ""),
        })
    details["cast"] = clean_cast

    return details
    
def set_info(infotag, info_dict):
    infotag.setTitle(info_dict['title'])
    if 'originaltitle' in info_dict:
        infotag.setOriginalTitle(info_dict['originaltitle'])
    if 'plot' in info_dict:
        infotag.setPlot(info_dict['plot'])
    if 'tagline' in info_dict:
        infotag.setTagLine(info_dict['tagline'])
    if 'studio' in info_dict:
        infotag.setStudios(info_dict['studio'])
    if 'genre' in info_dict:
        infotag.setGenres(info_dict['genre'])
    if 'tag' in info_dict:
        infotag.setTags(info_dict['tag'])
    if 'director' in info_dict:
        infotag.setDirectors(info_dict['director'])
    if 'premiered' in info_dict:
        infotag.setPremiered(info_dict['premiered'])
    if 'duration' in info_dict:
        infotag.setDuration(info_dict['duration'])
    if 'rating' in info_dict:
        infotag.setRating(info_dict['rating'])

def build_cast(cast_list):
    return [xbmc.Actor(cast['name'], cast.get('role', ''), cast.get('order', 0), cast.get('thumbnail', '')) 
            for cast in cast_list]

def set_artwork(listitem, available_art):
    # Set primary artwork
    art_dict = {}
    if 'poster' in available_art:
        if isinstance(available_art['poster'], list):
            art_dict['poster'] = available_art['poster'][0]
        else:
            art_dict['poster'] = available_art['poster']
    if 'thumb' in available_art:
        if isinstance(available_art['thumb'], list):
            art_dict['thumb'] = available_art['thumb'][0]
        else:
            art_dict['thumb'] = available_art['thumb']
    if 'fanart' in available_art:
        if isinstance(available_art['fanart'], list):
            art_dict['fanart'] = available_art['fanart'][0]
        else:
            art_dict['fanart'] = available_art['fanart']
    if art_dict:
        listitem.setArt(art_dict)
    
    # Add all available artwork options for "Choose art" dialog
    art_types = {
        'poster': available_art.get('poster_list', []),
        'fanart': available_art.get('fanart_list', []),
        'thumb': available_art.get('thumb_list', []),
        'landscape': available_art.get('landscape_list', [])
    }
    
    for art_type, url_list in art_types.items():
        if url_list and isinstance(url_list, list):
            for url in url_list:
                if url:
                    try:
                        listitem.addAvailableArtwork(url, art_type)
                    except:
                        pass

def add_web_images(details, settings):
    """Add web-searched images to details if enabled and needed"""
    try:
        # Check if we should use web search as fallback only
        fallback_only = settings.getSettingBool('web_search_fallback_only')
        existing_art = details.get('available_art', {})
        
        # If fallback only, skip if we already have images
        if fallback_only and (existing_art.get('poster') or existing_art.get('thumb')):
            log("Web image search skipped - existing images found (fallback mode)", xbmc.LOGDEBUG)
            return details
        
        # Get search settings
        search_engine = settings.getSettingString('web_search_engine') or 'bing'
        max_images = int(settings.getSettingString('max_web_images') or '3')
        
        # Get API keys
        google_api_key = settings.getSettingString('google_api_key')
        google_cx = settings.getSettingString('google_cx')
        bing_api_key = settings.getSettingString('bing_api_key')
        
        # Create search query from title and studio
        title = details['info'].get('title', '')
        studio = details['info'].get('studio', [])
        studio_name = studio[0] if studio else ''
        
        query = title
        if studio_name:
            query = "{} {}".format(studio_name, title)
        
        log("Searching web for images: {}".format(query), xbmc.LOGINFO)
        
        # Initialize web image searcher
        searcher = WebImageSearch(
            google_api_key=google_api_key,
            google_cx=google_cx,
            bing_api_key=bing_api_key
        )
        
        # Search for images
        image_urls = searcher.search_images(query, max_results=max_images, search_engine=search_engine)
        
        if image_urls:
            log("Found {} web images".format(len(image_urls)), xbmc.LOGINFO)
            
            # Initialize available_art if not exists
            if 'available_art' not in details:
                details['available_art'] = {}
            
            # Initialize artwork lists
            if 'poster_list' not in details['available_art']:
                details['available_art']['poster_list'] = []
            if 'fanart_list' not in details['available_art']:
                details['available_art']['fanart_list'] = []
            if 'thumb_list' not in details['available_art']:
                details['available_art']['thumb_list'] = []
            if 'landscape_list' not in details['available_art']:
                details['available_art']['landscape_list'] = []
            
            # Add all web images to all art type lists so user can choose
            for img_url in image_urls:
                details['available_art']['poster_list'].append(img_url)
                details['available_art']['fanart_list'].append(img_url)
                details['available_art']['thumb_list'].append(img_url)
                details['available_art']['landscape_list'].append(img_url)
            
            log("Added {} web images to artwork lists".format(len(image_urls)), xbmc.LOGINFO)
            
            # Set first image as default if none exists
            if not details['available_art'].get('poster') and len(image_urls) > 0:
                details['available_art']['poster'] = image_urls[0]
            if not details['available_art'].get('thumb') and len(image_urls) > 0:
                details['available_art']['thumb'] = image_urls[0]
            if not details['available_art'].get('fanart') and len(image_urls) > 1:
                details['available_art']['fanart'] = image_urls[1]
        else:
            log("No web images found", xbmc.LOGINFO)
    
    except Exception as e:
        log("Error adding web images: {}".format(str(e)), xbmc.LOGERROR)
        import traceback
        log("Traceback: {}".format(traceback.format_exc()), xbmc.LOGERROR)
    
    return details

def create_nfo_file(details, settings):
    """Create NFO file with scraped metadata"""
    try:
        nfo_path = settings.getSettingString('nfo_path')
        if not nfo_path:
            log("NFO path not configured, skipping NFO creation", xbmc.LOGDEBUG)
            return

        # Check if scene has meaningful metadata before creating NFO
        info = details.get('info', {})
        title = info.get('title', '').strip()
        
        # Skip if no title or title is placeholder/empty
        if not title or title.lower() in ['untitled', 'unknown', 'scene']:
            log("Skipping NFO creation: Scene has no meaningful title", xbmc.LOGINFO)
            return
        
        # Check if there's any substantial metadata
        has_plot = bool(info.get('plot', '').strip())
        has_studio = bool(info.get('studio', []))
        has_performers = bool(details.get('cast', []))
        has_tags = bool(info.get('tag', []))
        has_date = bool(info.get('premiered', '').strip())
        
        # Require at least title + one other piece of metadata
        if not any([has_plot, has_studio, has_performers, has_tags, has_date]):
            log("Skipping NFO creation: Scene '{}' has no additional metadata".format(title), xbmc.LOGINFO)
            return
        
        log("Scene '{}' has sufficient metadata, creating NFO".format(title), xbmc.LOGINFO)

        # Create NFO directory if it doesn't exist
        try:
            if not os.path.exists(nfo_path):
                os.makedirs(nfo_path)
        except OSError as e:
            log("Cannot create NFO directory: {}".format(str(e)), xbmc.LOGERROR)
            if settings.getSettingBool('nfo_notification'):
                xbmcgui.Dialog().notification("Stash Scraper", "Cannot create NFO directory", 
                                            xbmcgui.NOTIFICATION_ERROR)
            return

        # Build filename from title and stash ID
        stash_id = details['uniqueids'].get('stash', 'unknown')
        
        # Log the original title for debugging
        log("Creating NFO for title: '{}'".format(title), xbmc.LOGDEBUG)
        
        # Sanitize title - keep more characters for better filenames
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_', '.')).strip()
        
        # If title is empty or becomes empty after sanitization, use ID
        if not safe_title:
            safe_title = "stash_{}".format(stash_id)
            log("Title empty after sanitization, using: {}".format(safe_title), xbmc.LOGINFO)
        else:
            # Clean up multiple spaces and limit length
            safe_title = ' '.join(safe_title.split())  # Remove multiple spaces
            if len(safe_title) > 100:
                safe_title = safe_title[:100].strip()
            # Replace spaces with underscores for filename
            safe_title = safe_title.replace(' ', '_')
        
        nfo_filename = "{}.nfo".format(safe_title)
        full_path = os.path.join(nfo_path, nfo_filename)

        # Build NFO XML
        root = ET.Element('movie')
        
        info = details['info']
        
        # Add title
        title_elem = ET.SubElement(root, 'title')
        title_elem.text = info.get('title', '')
        
        # Add original title if different
        if 'originaltitle' in info and info['originaltitle'] != info.get('title'):
            orig_title = ET.SubElement(root, 'originaltitle')
            orig_title.text = info['originaltitle']
        
        # Add plot
        if 'plot' in info and info['plot']:
            plot_elem = ET.SubElement(root, 'plot')
            plot_elem.text = info['plot']
        
        # Add outline/tagline
        if 'tagline' in info and info['tagline']:
            tagline_elem = ET.SubElement(root, 'tagline')
            tagline_elem.text = info['tagline']
        
        # Add year
        if 'premiered' in info and info['premiered']:
            premiered = info['premiered']
            try:
                year = premiered.split('-')[0]
                if year:
                    year_elem = ET.SubElement(root, 'year')
                    year_elem.text = year
                    premiered_elem = ET.SubElement(root, 'premiered')
                    premiered_elem.text = premiered
            except:
                pass
        
        # Add runtime
        if 'duration' in info:
            runtime = ET.SubElement(root, 'runtime')
            runtime.text = str(info['duration'])
        
        # Add rating
        if 'rating' in info:
            rating_elem = ET.SubElement(root, 'rating')
            rating_elem.text = str(info['rating'])
        
        # Add studios
        if 'studio' in info and info['studio']:
            for studio in info['studio']:
                if studio:
                    studio_elem = ET.SubElement(root, 'studio')
                    studio_elem.text = studio
        
        # Add genres
        if 'genre' in info and info['genre']:
            for genre in info['genre']:
                if genre:
                    genre_elem = ET.SubElement(root, 'genre')
                    genre_elem.text = genre
        
        # Add tags
        if 'tag' in info and info['tag']:
            for tag in info['tag']:
                if tag:
                    tag_elem = ET.SubElement(root, 'tag')
                    tag_elem.text = tag
        
        # Add director
        if 'director' in info and info['director']:
            for director in info['director']:
                if director:
                    director_elem = ET.SubElement(root, 'director')
                    director_elem.text = director
        
        # Add actors/cast
        if details.get('cast'):
            for actor in details['cast']:
                if actor.get('name'):
                    actor_elem = ET.SubElement(root, 'actor')
                    name_elem = ET.SubElement(actor_elem, 'name')
                    name_elem.text = actor['name']
                    if actor.get('role'):
                        role_elem = ET.SubElement(actor_elem, 'role')
                        role_elem.text = actor['role']
                    if actor.get('thumbnail'):
                        thumb_elem = ET.SubElement(actor_elem, 'thumb')
                        thumb_elem.text = actor['thumbnail']
        
        # Add unique IDs
        uniqueid_elem = ET.SubElement(root, 'uniqueid')
        uniqueid_elem.set('type', 'stash')
        uniqueid_elem.set('default', 'true')
        uniqueid_elem.text = details['uniqueids'].get('stash', '')
        
        # Add artwork
        if details.get('available_art'):
            art = details['available_art']
            if 'thumb' in art and art['thumb']:
                thumb = ET.SubElement(root, 'thumb')
                thumb.text = art['thumb']
            if 'fanart' in art and art['fanart']:
                fanart = ET.SubElement(root, 'fanart')
                fanart_thumb = ET.SubElement(fanart, 'thumb')
                fanart_thumb.text = art['fanart']
            if 'poster' in art and art['poster']:
                poster = ET.SubElement(root, 'poster')
                poster.text = art['poster']
        
        # Write to file - manual indentation for Python 2/3 compatibility
        tree = ET.ElementTree(root)
        # Try ET.indent if available (Python 3.9+), otherwise skip formatting
        try:
            ET.indent(tree, space="  ")
        except AttributeError:
            # ET.indent not available, write without indentation
            pass
        
        tree.write(full_path, encoding='utf-8', xml_declaration=True)
        
        log("NFO file created successfully: {}".format(full_path), xbmc.LOGINFO)
        
        # Show notification to user
        if settings.getSettingBool('nfo_notification'):
            xbmcgui.Dialog().notification("Stash Scraper", "NFO file created: {}".format(nfo_filename), 
                                        xbmcgui.NOTIFICATION_INFO, 3000)
    
    except Exception as e:
        log("Error creating NFO file: {}".format(str(e)), xbmc.LOGERROR)
        if settings.getSettingBool('nfo_notification'):
            xbmcgui.Dialog().notification("Stash Scraper", "Error creating NFO file", 
                                        xbmcgui.NOTIFICATION_ERROR)

def build_lookup_string(uniqueids):
    return json.dumps(uniqueids)

def parse_lookup_string(uniqueids):
    try:
        return json.loads(uniqueids)
    except ValueError:
        log("Can't parse this lookup string\n" + uniqueids, xbmc.LOGWARNING)
        return None

def extract_video_frame(video_path, time_seconds, output_path):
    """
    Extract a frame from a video file at the specified time position.
    Uses Kodi's built-in Player methods to capture the frame.
    
    Args:
        video_path: Full path to the video file
        time_seconds: Time position in seconds to capture frame
        output_path: Full path where the frame image should be saved
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Validate video path
        if not video_path or not os.path.exists(video_path):
            log("Video path does not exist: {}".format(video_path), xbmc.LOGERROR)
            return False
        
        log("Extracting frame from {} at {}s".format(video_path, time_seconds), xbmc.LOGINFO)
        
        # Use FFmpeg if available (Kodi has it built-in)
        try:
            # Try to use xbmc.executebuiltin with PlayerControl(RepeatOff)
            player = xbmc.Player()
            
            # Check if a video is already playing
            was_playing = player.isPlaying()
            
            # Start playing the video in background
            player.play(video_path)
            
            # Wait for playback to start
            timeout = 30  # 30 seconds timeout
            while not player.isPlaying() and timeout > 0:
                xbmc.sleep(100)
                timeout -= 0.1
            
            if not player.isPlaying():
                log("Failed to start video playback for frame extraction", xbmc.LOGERROR)
                return False
            
            # Seek to desired position
            player.seekTime(float(time_seconds))
            xbmc.sleep(500)  # Wait for seek to complete
            
            # Capture the frame using Kodi's screenshot functionality
            xbmc.executebuiltin('TakeScreenshot("{}")'.format(output_path))
            xbmc.sleep(200)  # Wait for screenshot to be saved
            
            # Stop playback if it wasn't playing before
            if not was_playing:
                player.stop()
            
            # Verify the file was created
            if os.path.exists(output_path):
                log("Frame extracted successfully: {}".format(output_path), xbmc.LOGINFO)
                return True
            else:
                log("Frame file was not created", xbmc.LOGERROR)
                return False
                
        except Exception as e:
            log("Error during frame extraction: {}".format(str(e)), xbmc.LOGERROR)
            return False
            
    except Exception as e:
        log("Failed to extract frame: {}".format(str(e)), xbmc.LOGERROR)
        return False

def get_video_file_path(details, settings):
    """
    Try to find the video file path associated with the scene.
    For Stash scraper, query the Stash API for the file path.
    
    Returns:
        Video file path or None
    """
    try:
        # Check if we have a stash uniqueid
        if 'stash' in details.get('uniqueids', {}):
            scene_id = details['uniqueids']['stash']
            scraper = get_stash_scraper(settings)
            
            # Query Stash for scene files
            # This assumes the StashScraper has a method to get file paths
            if hasattr(scraper, 'get_scene_files'):
                files = scraper.get_scene_files(scene_id)
                if files and len(files) > 0:
                    return files[0].get('path')
        
        return None
        
    except Exception as e:
        log("Error getting video file path: {}".format(str(e)), xbmc.LOGERROR)
        return None

def prompt_frame_extraction(details, settings, handle):
    """
    Prompt user to extract frames from video and add to artwork options.
    
    Args:
        details: Scene details dict
        settings: Addon settings
        handle: Kodi handle
    
    Returns:
        Updated details dict with extracted frames added to available_art
    """
    try:
        dialog = xbmcgui.Dialog()
        
        # Ask user if they want to extract frames
        if not dialog.yesno(
            ADDON_SETTINGS.getLocalizedString(32049),  # "Extract Frame"
            ADDON_SETTINGS.getLocalizedString(32057)   # "Would you like to extract frames..."
        ):
            return details
        
        # Try to get video file path
        video_path = get_video_file_path(details, settings)
        
        # If we couldn't get it automatically, ask user
        if not video_path:
            video_path = dialog.browse(1, "Select Video File", 'files', '', False, False, '')
            if not video_path:
                return details
        
        # Get extraction method
        extraction_method = settings.getSettingString('frame_extraction_method') or 'manual'
        
        frames = []
        
        if extraction_method == 'manual':
            # Manual mode: let user select time position
            time_input = dialog.numeric(2, 
                ADDON_SETTINGS.getLocalizedString(32050),  # "Select time position"
                defaultt="00:05:00")
            
            if time_input:
                # Parse time (format: HH:MM:SS)
                time_parts = time_input.split(':')
                if len(time_parts) == 3:
                    hours, minutes, seconds = map(int, time_parts)
                    time_seconds = hours * 3600 + minutes * 60 + seconds
                    
                    # Extract the frame
                    frame_path = extract_single_frame(video_path, time_seconds, settings)
                    if frame_path:
                        frames.append(frame_path)
                        
        else:  # auto mode
            # Auto mode: extract multiple frames at intervals
            frame_count = int(settings.getSettingString('auto_frame_count') or '5')
            
            # Get video duration (if available)
            try:
                player = xbmc.Player()
                player.play(video_path)
                
                timeout = 30
                while not player.isPlaying() and timeout > 0:
                    xbmc.sleep(100)
                    timeout -= 0.1
                
                if player.isPlaying():
                    duration = player.getTotalTime()
                    player.stop()
                    
                    # Extract frames at even intervals
                    interval = duration / (frame_count + 1)
                    for i in range(1, frame_count + 1):
                        time_seconds = int(interval * i)
                        frame_path = extract_single_frame(video_path, time_seconds, settings)
                        if frame_path:
                            frames.append(frame_path)
                            
            except Exception as e:
                log("Error in auto frame extraction: {}".format(str(e)), xbmc.LOGERROR)
        
        # Add extracted frames to available artwork
        if frames:
            if 'available_art' not in details:
                details['available_art'] = {}
            
            for art_type in ['poster_list', 'fanart_list', 'thumb_list']:
                if art_type not in details['available_art']:
                    details['available_art'][art_type] = []
                details['available_art'][art_type].extend(frames)
            
            dialog.notification(
                "Stash Scraper",
                ADDON_SETTINGS.getLocalizedString(32054),  # "Frame extracted successfully"
                xbmcgui.NOTIFICATION_INFO,
                3000
            )
        else:
            dialog.notification(
                "Stash Scraper",
                ADDON_SETTINGS.getLocalizedString(32055),  # "Failed to extract frame"
                xbmcgui.NOTIFICATION_ERROR,
                3000
            )
        
        return details
        
    except Exception as e:
        log("Error in prompt_frame_extraction: {}".format(str(e)), xbmc.LOGERROR)
        return details

def extract_single_frame(video_path, time_seconds, settings):
    """
    Extract a single frame and save it to storage.
    
    Returns:
        Path to extracted frame or None
    """
    try:
        # Get storage path
        storage_path = settings.getSettingString('frame_storage_path')
        if not storage_path:
            storage_path = tempfile.gettempdir()
        
        # Create output filename
        video_basename = os.path.splitext(os.path.basename(video_path))[0]
        # Clean filename for filesystem safety
        safe_basename = re.sub(r'[^\w\-_]', '_', video_basename)
        output_filename = "{}_{}.jpg".format(safe_basename, int(time_seconds))
        output_path = os.path.join(storage_path, output_filename)
        
        # Extract the frame
        if extract_video_frame(video_path, time_seconds, output_path):
            return output_path
        else:
            return None
            
    except Exception as e:
        log("Error extracting single frame: {}".format(str(e)), xbmc.LOGERROR)
        return None

def run():
    try:
        params = get_params(sys.argv[1:])
        enddir = True
        
        # Check import status first
        if not IMPORT_SUCCESS:
            log("CRITICAL: Cannot run scraper - imports failed: {}".format(IMPORT_ERROR), xbmc.LOGERROR)
            xbmcgui.Dialog().notification(
                "Stash Scraper Error", 
                "Import failed: {}".format(IMPORT_ERROR[:50]), 
                xbmcgui.NOTIFICATION_ERROR, 
                5000
            )
            if enddir and 'handle' in params:
                xbmcplugin.endOfDirectory(params['handle'])
            return
        
        if 'action' in params:
            settings = ADDON_SETTINGS
            action = params["action"]
            log("Running action: {}".format(action), xbmc.LOGINFO)
            
            if action == 'find' and 'title' in params:
                search_for_movie(params["title"], params.get("year"), params['handle'], settings)
            elif action == 'getdetails' and ('url' in params or 'uniqueIDs' in params):
                unique_ids = parse_lookup_string(params.get('uniqueIDs') or params.get('url'))
                enddir = not get_details(unique_ids, params['handle'], settings, fail_silently='uniqueIDs' in params)
            else:
                log("unhandled action: {}".format(action), xbmc.LOGWARNING)
        else:
            log("No action in 'params' to act on", xbmc.LOGWARNING)
        
        if enddir and 'handle' in params:
            xbmcplugin.endOfDirectory(params['handle'])
            
    except Exception as e:
        log("CRITICAL ERROR in run(): {}".format(str(e)), xbmc.LOGERROR)
        import traceback
        log("Traceback: {}".format(traceback.format_exc()), xbmc.LOGERROR)
        try:
            xbmcgui.Dialog().notification(
                "Stash Scraper Error", 
                "Critical error: {}".format(str(e)[:50]), 
                xbmcgui.NOTIFICATION_ERROR,
                5000
            )
        except:
            pass

if __name__ == '__main__':
    run()