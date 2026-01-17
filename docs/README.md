# Documentation Index

Welcome to the CIRCERO repository documentation. This documentation covers the metadata.stash.python Kodi addon and related tools.

## Quick Links

### Getting Started
- [Installation Guide](INSTALLATION.md) - How to install the addon
- [Configuration Guide](CONFIGURATION.md) - How to configure each scraper
- [Scrapers Overview](SCRAPERS.md) - Overview of all 7 supported scrapers

### Scraper-Specific Documentation
- [Stash Integration](integrations/STASH.md) - StashApp metadata scraper
- [AEBN Integration](integrations/AEBN.md) - Adult Entertainment Broadcast Network
- [Aylo Network](integrations/AYLO_NETWORK.md) - Brazzers, FakeHub, CzechHunter, GayWire
- [PrimalFetish](integrations/PRIMALFETISH.md) - Primal Fetish Network
- [Frame Extraction](integrations/FRAME_EXTRACTION.md) - Frame extraction feature

### Development
- [Development Guide](DEVELOPMENT.md) - Contributing and development workflow
- [Changelog](CHANGELOG.md) - Version history and changes

## Repository Structure

```
repo.circero/
├── metadata.stash.python/     # Main metadata scraper addon
├── repository.circero/          # Repository addon for easy installation
├── docs/                        # Documentation (you are here)
├── tools/                       # Development tools and scripts
└── .github/                     # GitHub workflows and templates
```

## Features

The metadata.stash.python addon supports **7 different scrapers**:

1. **Stash** - Self-hosted media library with GraphQL API
2. **AEBN** - Commercial adult entertainment database
3. **Brazzers** - Direct Aylo API access for Brazzers content
4. **FakeHub** - Multi-site support (FakeTaxi, FakeHostel, PublicAgent)
5. **CzechHunter** - Multi-studio (Czech Hunter, Debt Dandy, Dirty Scout)
6. **GayWire** - Guy Selector support
7. **PrimalFetish** - Primal Fetish Network

## Support

- **Issues**: [GitHub Issues](https://github.com/CIRCERO/repo.circero/issues)
- **Discussions**: [GitHub Discussions](https://github.com/CIRCERO/repo.circero/discussions)

## License

This project is licensed under the MIT License - see the [LICENSE.txt](../LICENSE.txt) file for details.
