# -*- coding: utf-8 -*-
"""
Rapidgator Integration Module
Search and download higher quality video files from Rapidgator premium
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import os
import re
import time

try:
    from urllib2 import Request, urlopen, HTTPError, URLError
    from urllib import urlencode
except ImportError:  # py3
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError
    from urllib.parse import urlencode

try:
    import xbmc
    import xbmcgui
    import xbmcvfs
except ImportError:
    # For testing outside Kodi
    xbmc = None
    xbmcgui = None
    xbmcvfs = None


class RapidgatorAPI:
    """
    Rapidgator API client for premium account operations.
    Uses Rapidgator's official API v1.
    """
    
    API_BASE = "https://rapidgator.net/api/v2"
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session_id = None
        self.session_expires = 0
        
    def _log(self, msg, level=None):
        """Log message to Kodi log"""
        if xbmc:
            log_level = level if level else xbmc.LOGDEBUG
            xbmc.log('[Rapidgator] {}'.format(msg), log_level)
        else:
            print('[Rapidgator] {}'.format(msg))
    
    def _make_request(self, endpoint, params=None, method='GET'):
        """Make API request to Rapidgator"""
        try:
            url = "{}/{}".format(self.API_BASE, endpoint)
            
            if params:
                if method == 'GET':
                    url += '?' + urlencode(params)
                    data = None
                else:
                    data = urlencode(params).encode('utf-8')
            else:
                data = None
            
            request = Request(url)
            request.add_header('User-Agent', 'Kodi Stash Scraper/1.0')
            request.add_header('Accept', 'application/json')
            
            if method == 'POST' and data:
                request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            response = urlopen(request, data, timeout=30)
            result = json.loads(response.read().decode('utf-8'))
            
            return result
            
        except HTTPError as e:
            self._log("HTTP Error: {} - {}".format(e.code, e.reason), xbmc.LOGERROR if xbmc else None)
            return {'status': 'error', 'error': str(e)}
        except URLError as e:
            self._log("URL Error: {}".format(e.reason), xbmc.LOGERROR if xbmc else None)
            return {'status': 'error', 'error': str(e)}
        except Exception as e:
            self._log("Request Error: {}".format(str(e)), xbmc.LOGERROR if xbmc else None)
            return {'status': 'error', 'error': str(e)}
    
    def login(self):
        """
        Login to Rapidgator and get session token.
        Returns True if successful.
        """
        try:
            # Check if we have a valid session
            if self.session_id and time.time() < self.session_expires:
                return True
            
            self._log("Logging in to Rapidgator...")
            
            result = self._make_request('user/login', {
                'login': self.username,
                'password': self.password
            }, method='POST')
            
            if result.get('status') == 200 and result.get('response'):
                self.session_id = result['response'].get('session_id')
                # Session typically valid for 1 hour
                self.session_expires = time.time() + 3500
                self._log("Login successful", xbmc.LOGINFO if xbmc else None)
                return True
            else:
                error = result.get('response', {}).get('error', 'Unknown error')
                self._log("Login failed: {}".format(error), xbmc.LOGERROR if xbmc else None)
                return False
                
        except Exception as e:
            self._log("Login error: {}".format(str(e)), xbmc.LOGERROR if xbmc else None)
            return False
    
    def get_account_info(self):
        """Get account information including premium status"""
        if not self.login():
            return None
        
        result = self._make_request('user/info', {'sid': self.session_id})
        
        if result.get('status') == 200:
            return result.get('response', {})
        return None
    
    def is_premium(self):
        """Check if account has premium subscription"""
        info = self.get_account_info()
        if info:
            # Premium accounts have is_premium flag or premium_end_time > now
            return info.get('is_premium', False) or info.get('premium_end_time', 0) > time.time()
        return False
    
    def search_files(self, query, page=1):
        """
        Search for files on Rapidgator.
        Note: Rapidgator doesn't have an official search API,
        so we use external search engines or file listing sites.
        
        Returns list of file info dicts.
        """
        self._log("Searching for: {}".format(query))
        
        # Clean up search query
        clean_query = self._clean_search_query(query)
        
        # Try multiple search approaches
        results = []
        
        # Approach 1: Use Rapidgator's folder search (if available)
        folder_results = self._search_via_folders(clean_query)
        results.extend(folder_results)
        
        # Approach 2: Use external aggregator sites
        if not results:
            external_results = self._search_external(clean_query)
            results.extend(external_results)
        
        return results
    
    def _clean_search_query(self, query):
        """Clean and optimize search query"""
        # Remove common words and special characters
        clean = re.sub(r'[^\w\s\-]', ' ', query)
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        # Remove common filler words
        stopwords = ['the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'a', 'an']
        words = [w for w in clean.split() if w.lower() not in stopwords]
        
        return ' '.join(words)
    
    def _search_via_folders(self, query):
        """Search using Rapidgator folder/file listing"""
        # This would require folder access - placeholder for now
        return []
    
    def _search_external(self, query):
        """
        Search external file hosting aggregators.
        This searches sites that index Rapidgator links.
        """
        results = []
        
        # Common search patterns for adult content file hosts
        search_engines = [
            self._search_filesearch,
            self._search_filelist,
        ]
        
        for search_func in search_engines:
            try:
                found = search_func(query)
                if found:
                    results.extend(found)
                    if len(results) >= 10:  # Limit results
                        break
            except Exception as e:
                self._log("Search engine error: {}".format(str(e)))
                continue
        
        return results
    
    def _search_filesearch(self, query):
        """Search via file search aggregator"""
        # Placeholder - would implement actual search
        # In practice, this would scrape a file search site
        return []
    
    def _search_filelist(self, query):
        """Search via file listing site"""
        # Placeholder - would implement actual search
        return []
    
    def get_file_info(self, file_id):
        """Get information about a specific file"""
        if not self.login():
            return None
        
        result = self._make_request('file/info', {
            'sid': self.session_id,
            'file_id': file_id
        })
        
        if result.get('status') == 200:
            return result.get('response', {})
        return None
    
    def get_download_link(self, file_id):
        """
        Get direct download link for a file.
        Requires premium account.
        """
        if not self.login():
            return None
        
        result = self._make_request('file/download', {
            'sid': self.session_id,
            'file_id': file_id
        })
        
        if result.get('status') == 200:
            return result.get('response', {}).get('url')
        
        self._log("Failed to get download link: {}".format(result.get('error', 'Unknown')))
        return None


class RapidgatorDownloader:
    """
    Download manager for Rapidgator files with progress tracking.
    """
    
    def __init__(self, api, download_path):
        self.api = api
        self.download_path = download_path
        self.current_download = None
        self._cancelled = False
        
    def _log(self, msg, level=None):
        """Log message"""
        if xbmc:
            log_level = level if level else xbmc.LOGDEBUG
            xbmc.log('[RapidgatorDownloader] {}'.format(msg), log_level)
        else:
            print('[RapidgatorDownloader] {}'.format(msg))
    
    def download(self, file_id, filename=None, progress_callback=None):
        """
        Download a file from Rapidgator.
        
        Args:
            file_id: Rapidgator file ID
            filename: Optional custom filename
            progress_callback: Optional callback(downloaded, total, speed)
        
        Returns:
            Path to downloaded file or None
        """
        self._cancelled = False
        
        try:
            # Get download link
            self._log("Getting download link for file: {}".format(file_id))
            download_url = self.api.get_download_link(file_id)
            
            if not download_url:
                self._log("Failed to get download URL", xbmc.LOGERROR if xbmc else None)
                return None
            
            # Get file info for filename
            if not filename:
                file_info = self.api.get_file_info(file_id)
                if file_info:
                    filename = file_info.get('name', 'download_{}.mp4'.format(file_id))
                else:
                    filename = 'download_{}.mp4'.format(file_id)
            
            # Create output path
            output_path = os.path.join(self.download_path, filename)
            
            # Ensure download directory exists
            if not os.path.exists(self.download_path):
                os.makedirs(self.download_path)
            
            self._log("Downloading to: {}".format(output_path))
            self.current_download = output_path
            
            # Download with progress
            return self._download_file(download_url, output_path, progress_callback)
            
        except Exception as e:
            self._log("Download error: {}".format(str(e)), xbmc.LOGERROR if xbmc else None)
            return None
    
    def _download_file(self, url, output_path, progress_callback=None):
        """Download file with progress tracking"""
        try:
            request = Request(url)
            request.add_header('User-Agent', 'Kodi Stash Scraper/1.0')
            
            response = urlopen(request, timeout=60)
            
            # Get file size
            total_size = int(response.headers.get('Content-Length', 0))
            
            # Download in chunks
            chunk_size = 1024 * 1024  # 1MB chunks
            downloaded = 0
            start_time = time.time()
            
            with open(output_path, 'wb') as f:
                while not self._cancelled:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Calculate speed
                    elapsed = time.time() - start_time
                    speed = downloaded / elapsed if elapsed > 0 else 0
                    
                    # Progress callback
                    if progress_callback:
                        progress_callback(downloaded, total_size, speed)
            
            if self._cancelled:
                # Clean up partial file
                if os.path.exists(output_path):
                    os.remove(output_path)
                self._log("Download cancelled")
                return None
            
            self._log("Download complete: {} bytes".format(downloaded))
            return output_path
            
        except Exception as e:
            self._log("Download failed: {}".format(str(e)), xbmc.LOGERROR if xbmc else None)
            if os.path.exists(output_path):
                os.remove(output_path)
            return None
    
    def cancel(self):
        """Cancel current download"""
        self._cancelled = True


class RapidgatorSearcher:
    """
    High-level search interface for finding videos on Rapidgator.
    Matches scraped content with Rapidgator files.
    """
    
    # Quality keywords for parsing filenames
    QUALITY_PATTERNS = {
        '2160p': [r'2160p', r'4k', r'uhd'],
        '1080p': [r'1080p', r'fullhd', r'fhd'],
        '720p': [r'720p', r'hd'],
        '480p': [r'480p', r'sd'],
    }
    
    QUALITY_ORDER = ['2160p', '1080p', '720p', '480p']
    
    def __init__(self, api):
        self.api = api
    
    def _log(self, msg, level=None):
        """Log message"""
        if xbmc:
            log_level = level if level else xbmc.LOGDEBUG
            xbmc.log('[RapidgatorSearcher] {}'.format(msg), log_level)
        else:
            print('[RapidgatorSearcher] {}'.format(msg))
    
    def search_for_scene(self, title, studio=None, performers=None, date=None):
        """
        Search for a scene on Rapidgator.
        
        Args:
            title: Scene title
            studio: Studio name (optional)
            performers: List of performer names (optional)
            date: Release date (optional)
        
        Returns:
            List of matched files with quality info
        """
        results = []
        
        # Build search queries
        queries = self._build_search_queries(title, studio, performers, date)
        
        for query in queries:
            self._log("Searching: {}".format(query))
            
            found = self.api.search_files(query)
            for item in found:
                # Parse quality from filename
                quality = self._detect_quality(item.get('name', ''))
                size = item.get('size', 0)
                
                results.append({
                    'file_id': item.get('file_id'),
                    'name': item.get('name'),
                    'size': size,
                    'size_formatted': self._format_size(size),
                    'quality': quality,
                    'url': item.get('url'),
                    'query': query
                })
            
            if results:
                break  # Found results, stop searching
        
        # Sort by quality (best first)
        results.sort(key=lambda x: self.QUALITY_ORDER.index(x['quality']) 
                     if x['quality'] in self.QUALITY_ORDER else 999)
        
        return results
    
    def _build_search_queries(self, title, studio=None, performers=None, date=None):
        """Build list of search queries to try"""
        queries = []
        
        # Clean title
        clean_title = re.sub(r'[^\w\s\-]', '', title)
        
        # Try with studio
        if studio:
            queries.append("{} {}".format(studio, clean_title))
        
        # Try with performers
        if performers and len(performers) > 0:
            # Try first performer + title
            queries.append("{} {}".format(performers[0], clean_title))
            
            # Try studio + first performer
            if studio:
                queries.append("{} {}".format(studio, performers[0]))
        
        # Try title alone
        queries.append(clean_title)
        
        # Try with date
        if date:
            year = date.split('-')[0] if '-' in date else date[:4]
            queries.append("{} {}".format(clean_title, year))
        
        return queries
    
    def _detect_quality(self, filename):
        """Detect video quality from filename"""
        filename_lower = filename.lower()
        
        for quality, patterns in self.QUALITY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, filename_lower):
                    return quality
        
        return 'unknown'
    
    def _format_size(self, size_bytes):
        """Format file size for display"""
        if size_bytes <= 0:
            return 'Unknown'
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return "{:.1f} {}".format(size_bytes, unit)
            size_bytes /= 1024
        
        return "{:.1f} PB".format(size_bytes)
    
    def filter_by_quality(self, results, min_quality='1080p', prefer_4k=True):
        """
        Filter results by quality requirements.
        
        Args:
            results: List of search results
            min_quality: Minimum acceptable quality
            prefer_4k: Prefer 4K when available
        
        Returns:
            Filtered and sorted list
        """
        if not results:
            return []
        
        # Get minimum quality index
        min_idx = self.QUALITY_ORDER.index(min_quality) if min_quality in self.QUALITY_ORDER else 999
        
        # Filter by minimum quality
        filtered = [r for r in results 
                   if r['quality'] in self.QUALITY_ORDER 
                   and self.QUALITY_ORDER.index(r['quality']) <= min_idx]
        
        # Sort: best quality first
        filtered.sort(key=lambda x: self.QUALITY_ORDER.index(x['quality']) 
                      if x['quality'] in self.QUALITY_ORDER else 999)
        
        # If prefer 4K, move 4K results to top
        if prefer_4k:
            four_k = [r for r in filtered if r['quality'] == '2160p']
            others = [r for r in filtered if r['quality'] != '2160p']
            filtered = four_k + others
        
        return filtered


def prompt_rapidgator_search(details, settings):
    """
    Prompt user to search Rapidgator for higher quality version.
    
    Args:
        details: Scene details from scraper
        settings: Addon settings
    
    Returns:
        Path to downloaded file or None
    """
    if not xbmcgui:
        return None
    
    try:
        dialog = xbmcgui.Dialog()
        
        # Check if auto-search is enabled
        auto_search = settings.getSettingBool('rapidgator_auto_search')
        confirm = settings.getSettingBool('rapidgator_confirm_download')
        
        # Ask user if not auto
        if not auto_search:
            if not dialog.yesno(
                settings.getLocalizedString(32083),  # "Search for higher quality?"
                settings.getLocalizedString(32084)   # "Would you like to search Rapidgator..."
            ):
                return None
        
        # Get credentials
        username = settings.getSettingString('rapidgator_username')
        password = settings.getSettingString('rapidgator_password')
        
        if not username or not password:
            dialog.notification(
                "Rapidgator",
                "Please configure Rapidgator credentials in settings",
                xbmcgui.NOTIFICATION_WARNING
            )
            return None
        
        # Initialize API
        api = RapidgatorAPI(username, password)
        
        # Login
        if not api.login():
            dialog.notification(
                "Rapidgator",
                settings.getLocalizedString(32080),  # "Login failed"
                xbmcgui.NOTIFICATION_ERROR
            )
            return None
        
        # Show progress dialog
        progress = xbmcgui.DialogProgress()
        progress.create("Rapidgator", settings.getLocalizedString(32072))  # "Searching..."
        
        try:
            # Build search parameters from details
            title = details.get('info', {}).get('title', '')
            studio = details.get('info', {}).get('studio', [])
            studio_name = studio[0] if studio else None
            
            performers = [c.get('name') for c in details.get('cast', []) if c.get('name')]
            date = details.get('info', {}).get('premiered', '')
            
            # Search
            searcher = RapidgatorSearcher(api)
            results = searcher.search_for_scene(title, studio_name, performers, date)
            
            progress.close()
            
            if not results:
                dialog.notification(
                    "Rapidgator",
                    settings.getLocalizedString(32074),  # "No results found"
                    xbmcgui.NOTIFICATION_INFO
                )
                return None
            
            # Filter by quality preferences
            min_quality = settings.getSettingString('rapidgator_min_quality') or '1080p'
            prefer_4k = settings.getSettingBool('rapidgator_prefer_4k')
            
            filtered = searcher.filter_by_quality(results, min_quality, prefer_4k)
            
            if not filtered:
                dialog.notification(
                    "Rapidgator",
                    "No results match quality requirements",
                    xbmcgui.NOTIFICATION_INFO
                )
                return None
            
            # Build selection list
            items = []
            for r in filtered:
                label = "[{}] {} ({})".format(r['quality'], r['name'][:50], r['size_formatted'])
                items.append(label)
            
            # Show selection dialog
            selected = dialog.select(
                settings.getLocalizedString(32081),  # "Select version to download"
                items
            )
            
            if selected < 0:
                return None  # User cancelled
            
            chosen = filtered[selected]
            
            # Confirm download
            if confirm:
                msg = settings.getLocalizedString(32076) % (chosen['quality'], chosen['size_formatted'])
                if not dialog.yesno(
                    settings.getLocalizedString(32075),  # "Download from Rapidgator?"
                    msg
                ):
                    return None
            
            # Download
            download_path = settings.getSettingString('rapidgator_download_path')
            if not download_path:
                download_path = xbmcvfs.translatePath('special://temp/') if xbmcvfs else '/tmp'
            
            downloader = RapidgatorDownloader(api, download_path)
            
            # Show download progress
            progress = xbmcgui.DialogProgress()
            progress.create(
                "Rapidgator",
                settings.getLocalizedString(32082) % chosen['name'][:40]  # "Downloading..."
            )
            
            def progress_callback(downloaded, total, speed):
                if progress.iscanceled():
                    downloader.cancel()
                    return
                
                if total > 0:
                    percent = int((downloaded / total) * 100)
                    speed_mb = speed / 1024 / 1024
                    progress.update(
                        percent,
                        "Downloaded: {} / {}".format(
                            searcher._format_size(downloaded),
                            searcher._format_size(total)
                        ),
                        "Speed: {:.1f} MB/s".format(speed_mb)
                    )
            
            result_path = downloader.download(
                chosen['file_id'],
                filename=chosen['name'],
                progress_callback=progress_callback
            )
            
            progress.close()
            
            if result_path:
                dialog.notification(
                    "Rapidgator",
                    settings.getLocalizedString(32078),  # "Download complete"
                    xbmcgui.NOTIFICATION_INFO
                )
                
                # Handle replacing original file
                if settings.getSettingBool('rapidgator_replace_original'):
                    # TODO: Implement file replacement logic
                    pass
                
                return result_path
            else:
                dialog.notification(
                    "Rapidgator",
                    settings.getLocalizedString(32079),  # "Download failed"
                    xbmcgui.NOTIFICATION_ERROR
                )
                return None
                
        except Exception as e:
            progress.close()
            xbmc.log("[Rapidgator] Error: {}".format(str(e)), xbmc.LOGERROR)
            return None
        
    except Exception as e:
        if xbmc:
            xbmc.log("[Rapidgator] Error in prompt: {}".format(str(e)), xbmc.LOGERROR)
        return None


# For testing
if __name__ == '__main__':
    # Test search functionality
    api = RapidgatorAPI('test_user', 'test_pass')
    searcher = RapidgatorSearcher(api)
    
    results = searcher.search_for_scene(
        title="Test Scene Title",
        studio="Test Studio",
        performers=["Performer One", "Performer Two"]
    )
    
    print("Results:", json.dumps(results, indent=2))
