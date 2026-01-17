# Development Guide

Guide for contributing to the CIRCERO repository and developing new scrapers.

## Getting Started

### Prerequisites

- Python 3.x
- Git
- Kodi (for testing)
- Text editor or IDE

### Setting Up Development Environment

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/repo.circero.git
   cd repo.circero
   ```

2. **Create Development Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Link to Kodi** (for testing):
   ```bash
   # Linux/macOS
   ln -s $(pwd)/metadata.stash.python ~/.kodi/addons/metadata.stash.python
   
   # Windows (as Administrator)
   mklink /D "%APPDATA%\Kodi\addons\metadata.stash.python" "C:\path\to\repo.circero\metadata.stash.python"
   ```

## Repository Structure

```
repo.circero/
├── metadata.stash.python/      # Main addon
│   ├── addon.xml              # Addon metadata
│   ├── python/                # Python code
│   │   ├── scraper.py         # Main entry point
│   │   ├── scraper_config.py  # Configuration
│   │   ├── scraper_datahelper.py  # Data helpers
│   │   └── lib/               # Libraries
│   │       ├── AyloAPI/       # Aylo network API
│   │       └── stashscraper/  # Scraper implementations
│   └── resources/             # Resources
│       ├── settings.xml       # Settings definitions
│       └── language/          # Translations
├── repository.circero/         # Repository addon
├── docs/                      # Documentation
├── tools/                     # Development tools
└── .github/                   # GitHub configuration
```

## Adding a New Scraper

### Step 1: Implement Scraper Logic

Create a new scraper file in `metadata.stash.python/python/lib/stashscraper/`:

**Example**: `newscraper.py`

```python
# -*- coding: utf-8 -*-
"""
New Scraper implementation
"""

def search_scenes(query):
    """
    Search for scenes by title
    
    Args:
        query (str): Search query
        
    Returns:
        list: List of scene dictionaries with id, title, date, image
    """
    results = []
    # Implement search logic
    return results

def get_scene_details(scene_id):
    """
    Get detailed information for a scene
    
    Args:
        scene_id (str): Scene identifier
        
    Returns:
        dict: Scene details including title, plot, cast, images, etc.
    """
    details = {}
    # Implement details logic
    return details
```

### Step 2: Create Kodi Adapter

Create adapter file: `newscraper_adapter.py`

```python
# -*- coding: utf-8 -*-
"""
New Scraper Kodi Adapter
"""
from . import newscraper

class NewScraperScraper:
    """Kodi-compatible wrapper for New Scraper"""
    
    def search(self, title, year=None):
        """
        Search for scenes
        
        Returns list in Kodi format:
        [{
            'id': 'scene_id',
            'title': 'Scene Title',
            'date': '2026-01-01',
            'image': 'http://...',
            'studio': 'Studio Name'
        }]
        """
        results = newscraper.search_scenes(title)
        return self._format_search_results(results)
    
    def get_details(self, scene_id):
        """
        Get scene details
        
        Returns dict in Kodi NFO format:
        {
            'info': {
                'title': '...',
                'plot': '...',
                'studio': '...',
                'premiered': '...',
            },
            'cast': [...],
            'uniqueids': {'newscraper': scene_id},
            'available_art': {
                'poster': [...],
                'fanart': [...]
            }
        }
        """
        details = newscraper.get_scene_details(scene_id)
        return self._format_details(details)
    
    def _format_search_results(self, results):
        """Convert scraper format to Kodi format"""
        # Implementation
        pass
    
    def _format_details(self, details):
        """Convert scraper format to Kodi NFO format"""
        # Implementation
        pass
```

### Step 3: Register Scraper

Edit `metadata.stash.python/python/scraper.py`:

1. **Add import**:
   ```python
   from lib.stashscraper.newscraper_adapter import NewScraperScraper
   ```

2. **Add to get_active_scraper()**:
   ```python
   elif scraper_type == 'newscraper':
       return NewScraperScraper(), 'newscraper'
   ```

3. **Add to get_details()** (for direct ID lookup):
   ```python
   elif 'newscraper' in input_uniqueids:
       scraper_type = 'newscraper'
       scene_id = input_uniqueids['newscraper']
       scraper = NewScraperScraper()
   ```

### Step 4: Add Settings

Edit `metadata.stash.python/resources/settings.xml`:

1. **Add to scraper_type dropdown**:
   ```xml
   <setting label="32026" type="select" id="scraper_type" 
            default="stash" 
            values="stash|aebn|brazzers|fakehub|czechhunter|gaywire|primalfetish|newscraper"/>
   ```

2. **Add scraper-specific settings** (if needed):
   ```xml
   <setting label="New Scraper Settings" type="lsep" visible="eq(-1,newscraper)"/>
   <setting label="API Key" type="text" id="newscraper_api_key" 
            visible="eq(-2,newscraper)" default=""/>
   ```

### Step 5: Add Translations

Edit `metadata.stash.python/resources/language/resource.language.en_gb/strings.po`:

```po
msgctxt "#32100"
msgid "New Scraper"
msgstr ""

msgctxt "#32101"
msgid "API Key for New Scraper"
msgstr ""
```

### Step 6: Test

1. Restart Kodi
2. Configure addon with new scraper
3. Test search functionality
4. Test metadata fetch
5. Verify all fields populate correctly

### Step 7: Document

Create documentation in `docs/integrations/NEWSCRAPER.md`:

```markdown
# New Scraper Integration

## Overview
[Description of the scraper]

## Configuration
[Configuration steps]

## Usage
[Usage instructions]

## Troubleshooting
[Common issues and solutions]
```

## Testing

### Manual Testing

1. **Search Test**:
   - Add test video to Kodi
   - Trigger metadata search
   - Verify results are returned
   - Select result and verify details

2. **Direct Lookup Test**:
   - Right-click video
   - Choose "Information"
   - Enter scene ID
   - Verify metadata loads

3. **Error Handling Test**:
   - Test with invalid scene ID
   - Test with no network connection
   - Test with invalid API key (if applicable)
   - Verify appropriate error messages

### Validation Scripts

Run validation scripts:

```bash
python tools/validate_installation.py
python tools/validate_dependencies.py
```

Create scraper-specific validation if needed.

### Kodi Logs

Check Kodi logs for errors:

```bash
# Linux
tail -f ~/.kodi/temp/kodi.log

# Windows
type %APPDATA%\Kodi\kodi.log

# Filter for addon
tail -f ~/.kodi/temp/kodi.log | grep metadata.stash.python
```

## Code Style

### Python Style

- Follow PEP 8
- Use descriptive variable names
- Add docstrings to functions and classes
- Handle errors gracefully
- Log important events

### Example:

```python
def search_scenes(query, year=None):
    """
    Search for scenes by title and optional year
    
    Args:
        query (str): Search query string
        year (int, optional): Release year filter
        
    Returns:
        list: List of scene dictionaries, empty list if no results
        
    Raises:
        ConnectionError: If unable to connect to API
        ValueError: If query is empty or invalid
    """
    if not query:
        raise ValueError("Search query cannot be empty")
    
    try:
        # Implementation
        pass
    except Exception as e:
        log(f"Search failed: {str(e)}", level=xbmc.LOGERROR)
        return []
```

### Kodi Compatibility

- Support Python 2.7 and 3.x (use `from __future__ import` statements)
- Use `xbmc.log()` for logging
- Use Kodi's HTTP libraries when possible
- Handle missing dependencies gracefully

## Using AyloAPI

For Aylo network sites:

1. **Add domain mapping** to `metadata.stash.python/python/lib/AyloAPI/__init__.py`:
   ```python
   'newsiteid': 'newsite.com'
   ```

2. **Use AyloAPI functions**:
   ```python
   from AyloAPI.scrape import scraper_search, scraper_getdetails
   
   def search_scenes(query):
       return scraper_search(query, site='newsiteid')
   
   def get_scene_details(url):
       return scraper_getdetails(url)
   ```

## Committing Changes

### Commit Messages

Use clear, descriptive commit messages:

```
Add NewScraper support for example.com

- Implement scene search and details
- Add Kodi adapter
- Update settings and scraper.py
- Add documentation
```

### Pull Requests

1. Ensure all tests pass
2. Update documentation
3. Update CHANGELOG.md
4. Create pull request with description:
   - What was added/changed
   - Why the change was made
   - How to test it

## Building Repository

Generate repository files:

```bash
python tools/generate_repo.py
```

This creates:
- `repo/addons.xml`
- `repo/addons.xml.md5`
- `repo/metadata.stash.python-{version}.zip`
- `repo/repository.circero-{version}.zip`

## Version Management

### Updating Version

Edit `metadata.stash.python/addon.xml`:

```xml
<addon id="metadata.stash.python" version="2.1.0" ...>
```

### Changelog

Update `metadata.stash.python/changelog.txt`:

```
v2.1.0 (2026-01-20)
- Added NewScraper support
- Fixed bug in search
- Improved error handling
```

Update `docs/CHANGELOG.md` with detailed changes.

## Resources

### Kodi Development

- [Kodi Add-on Development](https://kodi.wiki/view/Add-on_development)
- [Python API](https://codedocs.xyz/xbmc/xbmc/)
- [Scraper Development](https://kodi.wiki/view/Scrapers)

### Python

- [PEP 8 Style Guide](https://pep8.org/)
- [Python 2/3 Compatibility](https://python-future.org/)

### Tools

- [Kodi Log Viewer](https://kodi.wiki/view/Log_file/Easy_access)
- [XML Validator](https://www.xmlvalidation.com/)

## Getting Help

- [GitHub Discussions](https://github.com/CIRCERO/repo.circero/discussions)
- [GitHub Issues](https://github.com/CIRCERO/repo.circero/issues)
- [Kodi Forums](https://forum.kodi.tv/)

## License

All contributions are licensed under MIT License. See LICENSE.txt for details.
