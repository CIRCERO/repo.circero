# Scrapers Overview

The metadata.stash.python addon supports **7 different metadata scrapers**. Each scraper connects to a different data source to fetch movie/scene metadata for your Kodi library.

## Scraper Comparison

| Scraper | Type | Authentication | Best For | Network |
|---------|------|----------------|----------|---------|
| **Stash** | Self-hosted | API Key | Private libraries, custom metadata | - |
| **AEBN** | Commercial | Username/Password | Commercial content database | - |
| **Brazzers** | Network API | None (Public API) | Brazzers content | Aylo |
| **FakeHub** | Network API | None (Public API) | FakeHub, FakeTaxi, FakeHostel, PublicAgent | Aylo |
| **CzechHunter** | Network API | None (Public API) | Czech Hunter, Debt Dandy, Dirty Scout | Aylo |
| **GayWire** | Network API | None (Public API) | Gay Wire, Guy Selector | Aylo |
| **PrimalFetish** | Network API | None (Public API) | Primal Fetish Network | Aylo |

## Detailed Scraper Information

### 1. Stash 🏠

**Status**: ✅ Fully Functional  
**Type**: Self-hosted GraphQL API

**Description**:  
Stash is a self-hosted media library management system. This scraper connects directly to your Stash instance to fetch metadata that you've already collected and organized.

**Use Cases**:
- You already use Stash for media management
- You want complete control over your metadata
- You have custom tags, performers, and organization
- Private content not available in public databases

**Requirements**:
- Running Stash instance (v0.8.0 or newer)
- Stash URL (e.g., `http://localhost:9999`)
- API Key (generated in Stash settings)

**Documentation**: [Stash Integration](integrations/STASH.md)

---

### 2. AEBN 💿

**Status**: ✅ Fully Functional  
**Type**: Commercial Database

**Description**:  
Adult Entertainment Broadcast Network (AEBN) is a major commercial database for adult content. This scraper connects to AEBN's database to fetch professional metadata.

**Use Cases**:
- Professional/commercial content
- High-quality metadata with official information
- Large commercial library
- DVD/Blu-ray releases

**Requirements**:
- AEBN account with API access
- AEBN URL
- Username and password

**Documentation**: [AEBN Integration](integrations/AEBN.md)

---

### 3. Brazzers 🔥

**Status**: ✅ Fully Functional  
**Type**: Aylo Network API

**Description**:  
Direct API access to Brazzers content metadata through the Aylo (formerly MindGeek) network API.

**Use Cases**:
- Brazzers content
- Official studio metadata
- High-quality images and descriptions
- Scene and performer information

**Requirements**:
- None - uses public API

**Documentation**: [Aylo Network - Brazzers](integrations/AYLO_NETWORK.md#brazzers)

---

### 4. FakeHub 🚕

**Status**: ✅ Fully Functional  
**Type**: Aylo Network API

**Description**:  
Multi-site support for the FakeHub network including FakeTaxi, FakeHostel, PublicAgent, and other FakeHub properties.

**Supported Sites**:
- FakeHub
- FakeTaxi
- FakeHostel
- PublicAgent
- And more...

**Requirements**:
- None - uses public API

**Documentation**: [Aylo Network - FakeHub](integrations/AYLO_NETWORK.md#fakehub)

---

### 5. CzechHunter 🇨🇿

**Status**: ✅ Fully Functional  
**Type**: Aylo Network API

**Description**:  
Multi-studio support for Czech content including Czech Hunter, Debt Dandy, and Dirty Scout.

**Supported Studios**:
- Czech Hunter
- Debt Dandy
- Dirty Scout

**Requirements**:
- None - uses public API

**Documentation**: [Aylo Network - CzechHunter](integrations/AYLO_NETWORK.md#czechhunter)

---

### 6. GayWire 🌈

**Status**: ✅ Fully Functional  
**Type**: Aylo Network API

**Description**:  
Support for Gay Wire network content including Guy Selector and related properties.

**Supported Sites**:
- Gay Wire
- Guy Selector

**Requirements**:
- None - uses public API

**Documentation**: [Aylo Network - GayWire](integrations/AYLO_NETWORK.md#gaywire)

---

### 7. PrimalFetish ⚡

**Status**: ✅ Fully Functional  
**Type**: Aylo Network API

**Description**:  
Complete support for the Primal Fetish Network through the Aylo API.

**Use Cases**:
- Primal Fetish content
- Complete scene metadata
- Performer information
- High-quality images

**Requirements**:
- None - uses public API

**Documentation**: [PrimalFetish Integration](integrations/PRIMALFETISH.md)

---

## Technology Stack

### Aylo Network Scrapers

Five of the seven scrapers (Brazzers, FakeHub, CzechHunter, GayWire, PrimalFetish) use the shared **AyloAPI** infrastructure:

**Benefits**:
- Consistent API interface
- Reliable data source
- No authentication required
- Regular updates from source
- SSL/HTTPS security

**Implementation**:
- Self-contained in `python/lib/AyloAPI/`
- No external dependencies
- Uses Python's built-in `urllib`
- Compatible with Python 2.7 and 3.x

### Independent Scrapers

- **Stash**: GraphQL API client
- **AEBN**: Custom HTTP API client

## Choosing a Scraper

**Choose Stash if**:
- You already use Stash
- You want full control over metadata
- You have private/custom content
- You want offline capability

**Choose AEBN if**:
- You have AEBN account access
- You need professional database
- You prefer official commercial metadata
- You have DVD/Blu-ray releases

**Choose Aylo Network scrapers if**:
- You have content from these specific networks
- You want no authentication hassle
- You need official studio metadata
- You want automatic updates

## Configuration

To select and configure a scraper:

1. Open Kodi **Settings** > **Add-ons**
2. Navigate to **My add-ons** > **Information providers** > **Movie information** > **Stash**
3. Click **Configure**
4. Select your preferred scraper from the **Scraper Type** dropdown
5. Configure scraper-specific settings

See [Configuration Guide](CONFIGURATION.md) for detailed setup instructions.

## Performance Notes

- **Stash**: Fast (local network), depends on your Stash instance
- **AEBN**: Moderate (requires authentication)
- **Aylo Network**: Fast (public API, no auth required)

## Limitations

- Each scraper only works with content from its respective source
- You can only use one scraper at a time
- Switching scrapers requires reconfiguration
- Some scrapers may have rate limits

## Adding More Scrapers

The addon is designed to be extensible. See [Development Guide](DEVELOPMENT.md) for information on adding new scrapers.
