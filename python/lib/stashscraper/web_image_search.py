"""
Web Image Search Module
Searches Google and Bing for images and downloads them for Kodi metadata
"""

import json
import os
import hashlib
import xbmc

try:
    from urllib2 import Request, urlopen, HTTPError, quote
except ImportError:  # py3
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError
    from urllib.parse import quote


class WebImageSearch:
    """Search for images on Google and Bing"""
    
    def __init__(self, cache_dir=None, google_api_key=None, google_cx=None, bing_api_key=None):
        """
        Initialize web image searcher
        
        Args:
            cache_dir: Directory to cache downloaded images
            google_api_key: Google Custom Search API key
            google_cx: Google Custom Search Engine ID
            bing_api_key: Bing Search API key
        """
        self.cache_dir = cache_dir or self._get_default_cache_dir()
        self.google_api_key = google_api_key
        self.google_cx = google_cx
        self.bing_api_key = bing_api_key
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir)
                xbmc.log("Created image cache directory: {}".format(self.cache_dir), xbmc.LOGINFO)
            except Exception as e:
                xbmc.log("Failed to create cache directory: {}".format(str(e)), xbmc.LOGERROR)
    
    def _get_default_cache_dir(self):
        """Get default cache directory in Kodi's addon data"""
        try:
            import xbmcaddon
            addon = xbmcaddon.Addon()
            addon_data = xbmc.translatePath(addon.getAddonInfo('profile'))
            return os.path.join(addon_data, 'image_cache')
        except:
            return os.path.join(os.path.expanduser('~'), '.kodi', 'userdata', 'addon_data', 'metadata.stash.python', 'image_cache')
    
    def search_images(self, query, max_results=5, search_engine='both'):
        """
        Search for images using Google and/or Bing
        
        Args:
            query: Search query (e.g., "Movie Title 2023")
            max_results: Maximum number of results to return
            search_engine: 'google', 'bing', or 'both'
            
        Returns:
            List of image URLs
        """
        images = []
        
        if search_engine in ['google', 'both'] and self.google_api_key and self.google_cx:
            try:
                google_images = self._search_google(query, max_results)
                images.extend(google_images)
                xbmc.log("Found {} images from Google for: {}".format(len(google_images), query), xbmc.LOGINFO)
            except Exception as e:
                xbmc.log("Google image search failed: {}".format(str(e)), xbmc.LOGERROR)
        
        if search_engine in ['bing', 'both'] and self.bing_api_key:
            try:
                bing_images = self._search_bing(query, max_results)
                images.extend(bing_images)
                xbmc.log("Found {} images from Bing for: {}".format(len(bing_images), query), xbmc.LOGINFO)
            except Exception as e:
                xbmc.log("Bing image search failed: {}".format(str(e)), xbmc.LOGERROR)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_images = []
        for img in images:
            if img not in seen:
                seen.add(img)
                unique_images.append(img)
        
        return unique_images[:max_results]
    
    def _search_google(self, query, max_results=5):
        """
        Search Google Custom Search for images
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of image URLs
        """
        if not self.google_api_key or not self.google_cx:
            xbmc.log("Google API key or CX not configured", xbmc.LOGDEBUG)
            return []
        
        # Google Custom Search API endpoint
        base_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.google_api_key,
            'cx': self.google_cx,
            'q': query,
            'searchType': 'image',
            'num': min(max_results, 10),  # Google API max is 10
            'imgSize': 'large',
            'safe': 'off'  # Can be changed to 'medium' or 'high' based on preference
        }
        
        # Build URL
        param_str = '&'.join(['{}={}'.format(k, quote(str(v))) for k, v in params.items()])
        url = "{}?{}".format(base_url, param_str)
        
        try:
            request = Request(url)
            response = urlopen(request, timeout=10)
            data = json.loads(response.read().decode('utf-8'))
            
            images = []
            if 'items' in data:
                for item in data['items']:
                    if 'link' in item:
                        images.append(item['link'])
            
            return images
        
        except HTTPError as e:
            xbmc.log("Google API HTTP Error: {} - {}".format(e.code, e.reason), xbmc.LOGERROR)
            return []
        except Exception as e:
            xbmc.log("Google search error: {}".format(str(e)), xbmc.LOGERROR)
            return []
    
    def _search_bing(self, query, max_results=5):
        """
        Search Bing Image Search for images
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of image URLs
        """
        if not self.bing_api_key:
            xbmc.log("Bing API key not configured", xbmc.LOGDEBUG)
            return []
        
        # Bing Image Search API endpoint
        url = "https://api.bing.microsoft.com/v7.0/images/search"
        
        headers = {
            'Ocp-Apim-Subscription-Key': self.bing_api_key
        }
        
        params = {
            'q': query,
            'count': min(max_results, 50),  # Bing API max is 150
            'imageType': 'Photo',
            'size': 'Large',
            'safeSearch': 'Off'  # Can be 'Moderate' or 'Strict'
        }
        
        # Build URL
        param_str = '&'.join(['{}={}'.format(k, quote(str(v))) for k, v in params.items()])
        full_url = "{}?{}".format(url, param_str)
        
        try:
            request = Request(full_url, headers=headers)
            response = urlopen(request, timeout=10)
            data = json.loads(response.read().decode('utf-8'))
            
            images = []
            if 'value' in data:
                for item in data['value']:
                    if 'contentUrl' in item:
                        images.append(item['contentUrl'])
            
            return images
        
        except HTTPError as e:
            xbmc.log("Bing API HTTP Error: {} - {}".format(e.code, e.reason), xbmc.LOGERROR)
            return []
        except Exception as e:
            xbmc.log("Bing search error: {}".format(str(e)), xbmc.LOGERROR)
            return []
    
    def download_image(self, image_url, filename=None):
        """
        Download an image and cache it locally
        
        Args:
            image_url: URL of the image to download
            filename: Optional filename (will generate from URL hash if not provided)
            
        Returns:
            Local file path of the downloaded image, or None if failed
        """
        if not image_url:
            return None
        
        # Generate filename from URL hash if not provided
        if not filename:
            url_hash = hashlib.md5(image_url.encode('utf-8')).hexdigest()
            # Try to get file extension from URL
            ext = self._get_extension_from_url(image_url)
            filename = "{}.{}".format(url_hash, ext)
        
        cache_path = os.path.join(self.cache_dir, filename)
        
        # Return cached file if it already exists
        if os.path.exists(cache_path):
            xbmc.log("Using cached image: {}".format(cache_path), xbmc.LOGDEBUG)
            return cache_path
        
        # Download the image
        try:
            xbmc.log("Downloading image from: {}".format(image_url), xbmc.LOGINFO)
            request = Request(image_url)
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            response = urlopen(request, timeout=15)
            image_data = response.read()
            
            # Save to cache
            with open(cache_path, 'wb') as f:
                f.write(image_data)
            
            xbmc.log("Image cached successfully: {}".format(cache_path), xbmc.LOGINFO)
            return cache_path
        
        except HTTPError as e:
            xbmc.log("Failed to download image (HTTP {}): {}".format(e.code, image_url), xbmc.LOGERROR)
            return None
        except Exception as e:
            xbmc.log("Image download error: {}".format(str(e)), xbmc.LOGERROR)
            return None
    
    def _get_extension_from_url(self, url):
        """Extract file extension from URL, default to jpg"""
        try:
            # Get the path part of the URL
            path = url.split('?')[0]  # Remove query parameters
            ext = path.split('.')[-1].lower()
            
            # Validate it's a common image extension
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']:
                return ext
            
            return 'jpg'  # Default
        except:
            return 'jpg'
    
    def search_and_download(self, query, max_results=3, search_engine='both'):
        """
        Search for images and download them
        
        Args:
            query: Search query
            max_results: Maximum number of images to download
            search_engine: 'google', 'bing', or 'both'
            
        Returns:
            List of local file paths of downloaded images
        """
        image_urls = self.search_images(query, max_results, search_engine)
        
        downloaded_paths = []
        for url in image_urls:
            path = self.download_image(url)
            if path:
                downloaded_paths.append(path)
            
            if len(downloaded_paths) >= max_results:
                break
        
        return downloaded_paths
    
    def clear_cache(self, max_age_days=30):
        """
        Clear old cached images
        
        Args:
            max_age_days: Remove files older than this many days
        """
        try:
            import time
            now = time.time()
            max_age_seconds = max_age_days * 24 * 60 * 60
            
            removed_count = 0
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                if os.path.isfile(filepath):
                    file_age = now - os.path.getmtime(filepath)
                    if file_age > max_age_seconds:
                        try:
                            os.remove(filepath)
                            removed_count += 1
                        except:
                            pass
            
            if removed_count > 0:
                xbmc.log("Cleared {} old cached images".format(removed_count), xbmc.LOGINFO)
        
        except Exception as e:
            xbmc.log("Cache cleanup error: {}".format(str(e)), xbmc.LOGERROR)
