# Stash Scraper Module - Scrapers Overview

## Working Scrapers

### 1. Stash (stash.py) ?
- **Status**: Fully functional
- **Purpose**: Scrapes from StashApp GraphQL API
- **Dependencies**: None (uses standard Python libraries)
- **Configuration**: Requires Stash URL and API Key

### 2. AEBN (aebn.py) ?
- **Status**: Fully functional
- **Purpose**: Scrapes from Adult Entertainment Broadcast Network
- **Dependencies**: None (uses standard Python libraries)
- **Configuration**: Requires AEBN URL, username, and password
- **Features**:
  - Scene search by title and year
  - Detailed scene metadata
  - Performer information
  - Multiple image support

## Scrapers Requiring Adaptation

The following scrapers were imported from StashApp's community scrapers but require significant modifications to work with this addon:

### 3. Brazzers (Brazzers.py) ??
- **Status**: Requires dependencies
- **Dependencies Needed**:
  - `py_common` - StashApp logging utilities
  - `AyloAPI` - Aylo/MindGeek API wrapper
- **Adaptation Required**: 
  - Replace StashApp-specific imports
  - Implement direct API calls to Brazzers/Aylo API
  - Adapt to Kodi addon structure

### 4. CzechHunter (CzechHunter.py) ??
- **Status**: Requires dependencies
- **Dependencies Needed**:
  - `py_common` - StashApp logging utilities
  - `AyloAPI` - Aylo/MindGeek API wrapper
- **Studios Supported**: Czech Hunter, Debt Dandy, Dirty Scout
- **Adaptation Required**: Same as Brazzers

### 5. FakeHub (FakeHub.py) ??
- **Status**: Requires dependencies
- **Dependencies Needed**:
  - `py_common` - StashApp logging utilities
  - `AyloAPI` - Aylo/MindGeek API wrapper
- **Studios Supported**: FakeHub, Fake Hostel, Fake Taxi, Public Agent
- **Adaptation Required**: Same as Brazzers

### 6. GayWire (GayWire.py) ??
- **Status**: Requires dependencies
- **Dependencies Needed**:
  - `py_common` - StashApp logging utilities
  - `AyloAPI` - Aylo/MindGeek API wrapper
  - `requests` - HTTP library for redirect handling
- **Studios Supported**: Gay Wire, Guy Selector
- **Adaptation Required**: Same as Brazzers + implement redirect handling

## How to Make These Scrapers Work

### Option 1: Use AyloAPI Library (Recommended)
1. Download the AyloAPI library from StashApp repository
2. Adapt it to work without StashApp-specific features
3. Install as part of this addon

### Option 2: Implement Direct API Calls (More Work)
For each scraper, you would need to:

1. **Reverse engineer the API**:
   - Study the AyloAPI library to understand endpoints
   - Implement direct HTTP requests to the Aylo/MindGeek API

2. **Replace imports**:
   ```python
   # Remove these
   from py_common import log
   from AyloAPI.scrape import scene_search, scene_from_url
   
   # Add Kodi equivalents
   import xbmc
   import ssl
   try:
       from urllib2 import Request, urlopen
   except ImportError:
       from urllib.request import Request, urlopen
   ```

3. **Implement scraper methods**:
   - `search(title, year)` - Returns list of matching scenes
   - `get_details(scene_id)` - Returns full scene metadata
   - Match the output format used by stash.py and aebn.py

4. **Handle authentication**:
   - Implement login if required
   - Session management
   - Cookie handling

### Example Template Structure

```python
class BrazzersScraper:
    def __init__(self, username, password):
        self.base_url = "https://www.brazzers.com"
        # Initialize session, SSL context, etc.
    
    def _make_request(self, endpoint, params=None):
        # Implement API request handling
        pass
    
    def search(self, title, year=None):
        # Return list of scenes matching title
        return [{
            'id': '...',
            'title': '...',
            'date': '...',
            'image': '...',
            'studio': '...'
        }]
    
    def get_details(self, scene_id):
        # Return full scene metadata
        return {
            'info': {...},
            'cast': [...],
            'uniqueids': {'brazzers': scene_id},
            'available_art': {...}
        }
```

## Integration Steps

Once a scraper is adapted:

1. **Add to scraper.py**:
   ```python
   from lib.stashscraper.brazzers import BrazzersScraper
   
   def get_brazzers_scraper(settings):
       username = settings.getSettingString('brazzers_username')
       password = settings.getSettingString('brazzers_password')
       return BrazzersScraper(username, password)
   ```

2. **Update get_active_scraper()**:
   ```python
   elif scraper_type == 'brazzers':
       return get_brazzers_scraper(settings), 'brazzers'
   ```

3. **Add settings** in settings.xml

4. **Add string labels** in strings.po

## Current Status Summary

| Scraper | Status | Ready to Use | Dependencies |
|---------|--------|--------------|--------------|
| Stash | ? Complete | Yes | None |
| AEBN | ? Complete | Yes | None |
| Brazzers | ? Complete | Yes | AyloAPI |
| CzechHunter | ? Complete | Yes | AyloAPI |
| FakeHub | ? Complete | Yes | AyloAPI |
| GayWire | ? Complete | Yes | AyloAPI |
| PrimalFetish | ? Complete | Yes | AyloAPI |

## Recommendations

1. **Keep** stash.py and aebn.py as-is - they work perfectly
2. **AyloAPI-based scrapers** (Brazzers, FakeHub, CzechHunter, GayWire, PrimalFetish) are now integrated
3. **Alternative**: Use StashApp itself with these scrapers, then pull data into Kodi via the Stash scraper
