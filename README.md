# CIRCERO Kodi Addon Repository

Professional Kodi metadata scraper supporting **7 different sources** for comprehensive media library management.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Kodi Version](https://img.shields.io/badge/Kodi-19%2B%20(Matrix)-blue.svg)](https://kodi.tv/)
[![Python](https://img.shields.io/badge/Python-2.7%20%7C%203.x-green.svg)](https://www.python.org/)

## 🎯 Features

The `metadata.stash.python` addon provides unified metadata scraping from multiple sources:

### Supported Scrapers

| Scraper | Description | Authentication | Status |
|---------|-------------|----------------|--------|
| 🏠 **Stash** | Self-hosted media library with GraphQL API | API Key | ✅ Ready |
| 💿 **AEBN** | Commercial adult entertainment database | Username/Password | ✅ Ready |
| 🔥 **Brazzers** | Direct API access via Aylo network | None | ✅ Ready |
| 🚕 **FakeHub** | Multi-site (FakeTaxi, FakeHostel, PublicAgent) | None | ✅ Ready |
| 🇨🇿 **CzechHunter** | Multi-studio (Debt Dandy, Dirty Scout) | None | ✅ Ready |
| 🌈 **GayWire** | Guy Selector support | None | ✅ Ready |
| ⚡ **PrimalFetish** | Primal Fetish Network | None | ✅ Ready |

### Key Features

✨ **7 Scrapers in One**: Choose the best source for your content  
🔄 **Easy Switching**: Change scrapers without reinstalling  
🚀 **No Dependencies**: Self-contained with no external packages  
🔒 **Secure**: API keys stored in Kodi settings  
⚡ **Fast**: Optimized with caching and retry logic  
🎨 **Complete Metadata**: Titles, plots, cast, images, and more  
🔧 **Configurable**: Timeouts, retries, caching options  

## 📦 Installation

### Method 1: Install from Repository (Recommended)

1. **Download Repository Addon**
   - Get `repository.circero-1.0.0.zip` from [Releases](https://github.com/CIRCERO/repo.circero/releases)
   - Or: `https://raw.githubusercontent.com/CIRCERO/repo.circero/main/repo/repository.circero-1.0.0.zip`

2. **Install in Kodi**
   - Settings → Add-ons → Install from zip file
   - Select the downloaded ZIP
   - Wait for "Repository enabled" notification

3. **Install Addon**
   - Add-ons → Install from repository → CIRCERO Repository
   - Information providers → Movie information → Stash
   - Click Install

4. **Configure**
   - Configure addon (select scraper and enter credentials)
   - Start scraping!

### Method 2: Manual Installation

1. Download `metadata.stash.python-{version}.zip` from [Releases](https://github.com/CIRCERO/repo.circero/releases)
2. Install in Kodi: Settings → Add-ons → Install from zip file
3. Select downloaded ZIP file

**Note**: Manual installations don't receive automatic updates.

For detailed instructions, see [Installation Guide](docs/INSTALLATION.md).

## 🚀 Quick Start

### For Stash Users

```
1. Configure → Select "stash" as Scraper Type
2. Enter your Stash URL: http://localhost:9999
3. Enter your API Key (from Stash Settings > Security)
4. Done! Start scanning your library
```

### For AEBN Users

```
1. Configure → Select "aebn" as Scraper Type
2. Enter AEBN URL, username, and password
3. Done! Start scanning your library
```

### For Aylo Network (Brazzers, FakeHub, etc.)

```
1. Configure → Select scraper (brazzers, fakehub, czechhunter, gaywire, or primalfetish)
2. That's it! No authentication needed
3. Start scanning your library
```

## 📖 Documentation

Comprehensive documentation is available in the [docs](docs/) directory:

- **[Installation Guide](docs/INSTALLATION.md)** - Installation methods and troubleshooting
- **[Configuration Guide](docs/CONFIGURATION.md)** - Configure each scraper
- **[Scrapers Overview](docs/SCRAPERS.md)** - Compare and choose scrapers
- **[Development Guide](docs/DEVELOPMENT.md)** - Contributing and adding scrapers

### Scraper-Specific Docs

- [Stash Integration](docs/integrations/STASH.md)
- [AEBN Integration](docs/integrations/AEBN.md)
- [Aylo Network (Brazzers, FakeHub, CzechHunter, GayWire)](docs/integrations/AYLO_NETWORK.md)
- [PrimalFetish](docs/integrations/PRIMALFETISH.md)
- [Frame Extraction Feature](docs/integrations/FRAME_EXTRACTION.md)

## 🛠️ Configuration

Access settings: **Settings → Add-ons → My add-ons → Information providers → Movie information → Stash → Configure**

### Available Settings

- **Scraper Type**: Choose your data source
- **Stash URL & API Key**: For Stash scraper
- **AEBN Credentials**: For AEBN scraper
- **Connection Timeout**: Network timeout (10-300s)
- **Max Retry Attempts**: Failed request retries (1-10)
- **Result Caching**: Optional caching (Stash only)
- **Cache Duration**: Cache lifetime (1-168 hours)

See [Configuration Guide](docs/CONFIGURATION.md) for details.

## 🔧 Development

### Setting Up

```bash
# Clone repository
git clone https://github.com/CIRCERO/repo.circero.git
cd repo.circero

# Link to Kodi for development
ln -s $(pwd)/metadata.stash.python ~/.kodi/addons/metadata.stash.python

# Make changes and test in Kodi
```

### Adding a New Scraper

1. Implement scraper logic in `metadata.stash.python/python/lib/stashscraper/`
2. Create Kodi adapter
3. Register in `scraper.py`
4. Add to settings.xml
5. Document in `docs/`
6. Test thoroughly

See [Development Guide](docs/DEVELOPMENT.md) for complete instructions.

### Building Repository

```bash
python tools/generate_repo.py
```

Generates repository files in `repo/` directory.

## 📁 Repository Structure

```
repo.circero/
├── metadata.stash.python/      # Main metadata scraper addon
│   ├── addon.xml
│   ├── python/
│   │   ├── scraper.py         # Main entry point
│   │   └── lib/               # Libraries
│   │       ├── AyloAPI/       # Aylo network API
│   │       └── stashscraper/  # Scraper implementations
│   └── resources/
│       └── settings.xml       # Configuration
├── repository.circero/         # Repository addon
├── docs/                       # Documentation
├── tools/                      # Development tools
└── .github/                    # GitHub workflows
```

## 🧪 Validation

Validate your installation:

```bash
# Check installation
python tools/validate_installation.py

# Check dependencies
python tools/validate_dependencies.py

# Check PrimalFetish integration
python tools/validate_primalfetish.py
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-scraper`)
3. Make your changes
4. Test thoroughly
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) and [Development Guide](docs/DEVELOPMENT.md).

## 📜 License

This project is licensed under the MIT License - see [LICENSE.txt](LICENSE.txt).

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/CIRCERO/repo.circero/issues)
- **Discussions**: [GitHub Discussions](https://github.com/CIRCERO/repo.circero/discussions)
- **Documentation**: [docs/](docs/)

## 📝 Changelog

See [CHANGELOG.md](docs/CHANGELOG.md) for version history and changes.

### Latest Version: 2.0.0 (January 2026)

- ✅ Enhanced error handling with retry logic
- ✅ Configurable timeouts
- ✅ Optional result caching
- ✅ All 7 scrapers fully operational
- ✅ Improved logging and debugging
- ✅ Production ready

## ⭐ Star History

If you find this project useful, please consider starring it on GitHub!

## 🙏 Acknowledgments

- [Kodi](https://kodi.tv/) - Media center software
- [StashApp](https://stashapp.cc/) - Media library management
- [Aylo](https://aylo.com/) - Content network API
- Community contributors and testers

---

**Made with ❤️ by CIRCERO**
