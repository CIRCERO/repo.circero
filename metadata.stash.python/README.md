# metadata.stash.python

Multi-source metadata scraper for Kodi supporting 7 different data sources.

## Overview

This Kodi addon provides comprehensive metadata scraping from multiple sources, allowing you to choose the best data source for your content.

## Supported Scrapers

1. **Stash** - Self-hosted media library (GraphQL API)
2. **AEBN** - Commercial database (requires account)
3. **Brazzers** - Aylo network (no auth required)
4. **FakeHub** - Aylo network (no auth required)
5. **CzechHunter** - Aylo network (no auth required)
6. **GayWire** - Aylo network (no auth required)
7. **PrimalFetish** - Aylo network (no auth required)

## Features

✨ 7 scrapers in one addon  
🔄 Easy switching between sources  
🚀 No external dependencies  
⚡ Fast with caching and retry logic  
🎨 Complete metadata (titles, plots, cast, images)  
🔧 Highly configurable  

## Installation

### From Repository

1. Install `repository.circero` from repository ZIP
2. Install addon from CIRCERO Repository
3. Configure your preferred scraper
4. Start scraping!

### Manual Installation

1. Download addon ZIP from releases
2. Install from ZIP in Kodi
3. Configure settings

See [Installation Guide](../docs/INSTALLATION.md) for detailed instructions.

## Configuration

Access settings: **Settings → Add-ons → My add-ons → Information providers → Movie information → Stash → Configure**

### Select Scraper

Choose from the **Scraper Type** dropdown:
- `stash` - For Stash users
- `aebn` - For AEBN users
- `brazzers`, `fakehub`, `czechhunter`, `gaywire`, `primalfetish` - For Aylo network content

### Scraper-Specific Settings

**Stash**:
- Stash URL (e.g., `http://localhost:9999`)
- API Key

**AEBN**:
- AEBN URL
- Username
- Password

**Aylo Network**: No configuration needed!

See [Configuration Guide](../docs/CONFIGURATION.md) for complete details.

## Usage

Once configured, the addon integrates seamlessly with Kodi:

1. Add video sources to your Kodi library
2. Set content type to "Movies"
3. Select "Stash" as the scraper
4. Kodi automatically fetches metadata during library scans

### Manual Search

1. Right-click on a video
2. Select "Information"
3. Click "Refresh" to search
4. Select matching result

### Direct Lookup

Enter scene ID or URL for direct metadata fetch.

## Documentation

Complete documentation available at:
- [Main Documentation](../docs/README.md)
- [Installation Guide](../docs/INSTALLATION.md)
- [Configuration Guide](../docs/CONFIGURATION.md)
- [Scrapers Overview](../docs/SCRAPERS.md)

## Requirements

- **Kodi**: 19.x (Matrix) or newer
- **Python**: 3.x (included with Kodi)
- **Internet**: Required for metadata fetching

## Troubleshooting

### Cannot Connect

- Verify URLs and credentials
- Check firewall settings
- Review Kodi logs

### No Results Found

- Verify content exists in selected source
- Try different search terms
- Check scraper selection

### Import Errors

Run validation scripts:
```bash
python ../tools/validate_installation.py
python ../tools/validate_dependencies.py
```

See [Configuration Guide](../docs/CONFIGURATION.md#troubleshooting) for more help.

## Version

**Current Version**: 2.0.0 (January 2026)

See [CHANGELOG](../docs/CHANGELOG.md) for version history.

## License

MIT License - See [LICENSE.txt](LICENSE.txt)

## Support

- [GitHub Issues](https://github.com/CIRCERO/repo.circero/issues)
- [Documentation](../docs/)
- [GitHub Discussions](https://github.com/CIRCERO/repo.circero/discussions)

---

Part of the [CIRCERO Repository](https://github.com/CIRCERO/repo.circero)
