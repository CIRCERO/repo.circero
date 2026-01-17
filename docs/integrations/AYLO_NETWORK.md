# Aylo Network Integration

Integration with the Aylo (formerly MindGeek) network API, supporting multiple major studios and networks.

## Overview

**Network**: Aylo (MindGeek)  
**Type**: Public API  
**Authentication**: None required  
**Status**: ✅ Fully Functional

The Aylo Network integration provides support for 5 different scrapers using a shared API infrastructure:
- Brazzers
- FakeHub
- CzechHunter
- GayWire
- PrimalFetish

## Shared Infrastructure

All Aylo-based scrapers use the **AyloAPI** library:

**Location**: `python/lib/AyloAPI/`

**Features**:
- Self-contained (no external dependencies)
- Uses Python's built-in `urllib`
- SSL/HTTPS support
- Domain mapping for all supported sites
- Scene and performer search
- Image handling

**Base API**: `https://site-api.project1service.com/v2`

## Scrapers

### Brazzers

**Scraper ID**: `brazzers`  
**Domain**: `brazzers.com`

**Features**:
- Official Brazzers content metadata
- Scene search by title
- Performer information
- High-quality images
- Studio information

**Configuration**: None required - select `brazzers` as Scraper Type

**Usage**:
1. Select `brazzers` in Scraper Type dropdown
2. Search by scene title
3. Select matching scene
4. Metadata automatically fetched

---

### FakeHub

**Scraper ID**: `fakehub`  
**Supported Sites**:
- FakeHub
- FakeTaxi
- FakeHostel
- PublicAgent
- And more FakeHub properties

**Features**:
- Multi-site support
- Unified search across all FakeHub properties
- Official metadata
- High-quality images

**Configuration**: None required

**Usage**: Same as Brazzers, searches across all FakeHub sites

---

### CzechHunter

**Scraper ID**: `czechhunter`  
**Supported Studios**:
- Czech Hunter
- Debt Dandy
- Dirty Scout

**Features**:
- Multi-studio support
- Official Czech content metadata
- Studio-specific organization

**Configuration**: None required

**Usage**: Same as Brazzers, searches across all supported studios

---

### GayWire

**Scraper ID**: `gaywire`  
**Supported Sites**:
- Gay Wire
- Guy Selector

**Features**:
- Official Gay Wire network metadata
- Multi-site support

**Configuration**: None required

**Usage**: Same as Brazzers, searches across Gay Wire properties

---

### PrimalFetish

**Scraper ID**: `primalfetish`  
**Domain**: `primalfetishnetwork.com`

**Features**:
- Complete Primal Fetish Network support
- Scene and performer metadata
- High-quality images
- Release dates and tags

**Configuration**: None required

**Usage**: Same as other Aylo scrapers

See [PrimalFetish Integration](PRIMALFETISH.md) for detailed documentation.

---

## Technical Details

### AyloAPI Architecture

```
Kodi Request
    ↓
scraper.py (routing)
    ↓
{scraper}_adapter.py (Kodi format conversion)
    ↓
{Scraper}.py (domain-specific logic)
    ↓
AyloAPI (API wrapper)
    ↓
Aylo/MindGeek API
    ↓
Response flows back up the chain
    ↓
Kodi receives metadata
```

### Domain Mapping

The AyloAPI automatically maps scraper types to correct domains:

```python
DOMAIN_MAP = {
    'brazzers': 'brazzers.com',
    'fakehub': 'fakehub.com',
    'czechhunter': 'czechhunter.com',
    'gaywire': 'gaywire.com',
    'primalfetish': 'primalfetishnetwork.com',
    # ... and many more
}
```

### API Endpoints

**Scene Search**:
```
GET /scenes?search={query}
```

**Scene Details**:
```
GET /scenes/{scene_id}
```

**Performer Search**:
```
GET /performers?search={query}
```

**Performer Details**:
```
GET /performers/{performer_id}
```

## Common Features

All Aylo network scrapers support:

✅ Scene search by title  
✅ Scene details by ID/URL  
✅ Performer search  
✅ Performer details  
✅ Multiple images (poster, fanart, screenshots)  
✅ Tags and categories  
✅ Studio information  
✅ Release dates and duration  
✅ No authentication required  
✅ SSL/HTTPS security  

## Configuration

**No configuration required!**

1. Select scraper from Scraper Type dropdown
2. Start using immediately
3. No API keys needed
4. No account required

## Usage Tips

### Search Best Practices

1. **Use Official Titles**: Search with the official scene title for best results
2. **Be Specific**: More specific titles return better matches
3. **Scene ID Lookup**: If you have the scene URL or ID, use direct lookup
4. **Check Multiple Scrapers**: If not found in one, try related scrapers

### Performance

- **Fast**: Public API with no authentication overhead
- **Reliable**: Backed by Aylo infrastructure
- **No Rate Limits**: (as of current implementation)

## Metadata Quality

All Aylo scrapers provide:
- **Official Data**: Direct from studio sources
- **High Quality Images**: Professional photography
- **Accurate Information**: Verified scene details
- **Complete Cast**: Full performer information
- **Up-to-date**: Regular updates from source

## Troubleshooting

### No Results Found

**Solutions**:
1. Verify scene title is correct
2. Try alternate titles or shorter queries
3. Check if content is from the selected network
4. Try different Aylo scraper if multi-network content
5. Check Kodi log for API response details

### Connection Errors

**Solutions**:
1. Check internet connection
2. Verify Aylo API is accessible
3. Check firewall settings
4. Review Kodi logs for detailed errors

### Slow Performance

**Causes**:
- Network latency
- Large result sets
- API load

**Solutions**:
- Use more specific search terms
- Try direct scene ID lookup
- Check network connection speed

## Adding New Aylo Sites

The AyloAPI infrastructure makes it easy to add new sites:

1. Add domain mapping to `AyloAPI/__init__.py`
2. Create scraper file (e.g., `NewSite.py`)
3. Create adapter file (e.g., `newsite_adapter.py`)
4. Add to `scraper.py` routing
5. Add to `settings.xml` dropdown

See [Development Guide](../DEVELOPMENT.md) for details.

## Code Organization

```
python/lib/
├── AyloAPI/
│   ├── __init__.py          # API client & domain mapping
│   └── scrape.py            # Scraping functions
├── stashscraper/
│   ├── Brazzers.py          # Brazzers domain logic
│   ├── brazzers_adapter.py  # Kodi adapter
│   ├── FakeHub.py           # FakeHub domain logic
│   ├── fakehub_adapter.py   # Kodi adapter
│   ├── CzechHunter.py       # Czech domain logic
│   ├── czechhunter_adapter.py
│   ├── GayWire.py           # GayWire domain logic
│   ├── gaywire_adapter.py
│   ├── PrimalFetish.py      # PrimalFetish domain logic
│   └── primalfetish_adapter.py
```

## Dependencies

**None!** The AyloAPI implementation is self-contained:
- Uses Python's built-in `urllib` (no `requests` needed)
- No external packages required
- Python 2.7 and 3.x compatible
- Works on all platforms

## Version History

### Latest Updates
- ✅ All 5 Aylo scrapers fully integrated
- ✅ Self-contained AyloAPI library
- ✅ No external dependencies
- ✅ Stable and production-ready

## Resources

- **Aylo Official**: https://aylo.com
- **Support**: https://github.com/CIRCERO/repo.circero/issues

## See Also

- [PrimalFetish Integration](PRIMALFETISH.md) - Detailed PrimalFetish documentation
- [Configuration Guide](../CONFIGURATION.md) - General configuration
- [Development Guide](../DEVELOPMENT.md) - Contributing new scrapers
