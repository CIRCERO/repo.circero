# Configuration Guide

This guide explains how to configure each of the 7 supported scrapers in the metadata.stash.python addon.

## Accessing Settings

1. Open **Kodi**
2. Go to **Settings** (gear icon) > **Add-ons**
3. Navigate to **My add-ons** > **Information providers** > **Movie information**
4. Select **Stash**
5. Click **Configure**

## General Settings

### Scraper Type
**Setting**: `Scraper Type`  
**Options**: `stash` | `aebn` | `brazzers` | `fakehub` | `czechhunter` | `gaywire` | `primalfetish`  
**Default**: `stash`

Select which scraper you want to use. After changing this setting, you'll need to configure the specific settings for that scraper (see below).

## Scraper-Specific Configuration

### 1. Stash Configuration

**Required Settings**:

#### Stash URL
- **Setting**: `Stash URL`
- **Example**: `http://localhost:9999` or `http://192.168.1.100:9999`
- **Description**: The URL where your Stash instance is running
- **Notes**: 
  - Include the protocol (`http://` or `https://`)
  - Include the port number if not default
  - Do not include trailing slash

#### API Key
- **Setting**: `API Key`
- **Example**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- **Description**: Your Stash API key for authentication
- **How to get it**:
  1. Open Stash web interface
  2. Go to Settings > Security
  3. Click "Generate API Key" or copy existing key

**Advanced Settings**:

#### Connection Timeout
- **Setting**: `Connection Timeout (seconds)`
- **Default**: `30`
- **Range**: `10-300`
- **Description**: How long to wait for Stash to respond before timing out

#### Max Retry Attempts
- **Setting**: `Max Retry Attempts`
- **Default**: `3`
- **Range**: `1-10`
- **Description**: Number of times to retry failed requests

#### Enable Result Caching
- **Setting**: `Enable Result Caching`
- **Default**: `false`
- **Description**: Cache search results to reduce API calls

#### Cache Duration
- **Setting**: `Cache Duration (hours)`
- **Default**: `24`
- **Range**: `1-168` (1 week)
- **Description**: How long to keep cached results

---

### 2. AEBN Configuration

**Required Settings**:

#### AEBN URL
- **Setting**: `AEBN URL`
- **Example**: `https://aebn.com` (or your specific AEBN instance URL)
- **Description**: The base URL for AEBN API access

#### Username
- **Setting**: `AEBN Username`
- **Description**: Your AEBN account username

#### Password
- **Setting**: `AEBN Password`
- **Description**: Your AEBN account password
- **Notes**: Password is stored securely in Kodi settings

---

### 3. Brazzers Configuration

**Required Settings**: None!

Brazzers scraper uses the public Aylo API and requires no authentication or configuration.

**How it works**:
1. Select `brazzers` as Scraper Type
2. The addon automatically uses the Aylo API
3. Search by scene title to find content

---

### 4. FakeHub Configuration

**Required Settings**: None!

FakeHub scraper uses the public Aylo API and requires no authentication or configuration.

**Supported Sites**:
- FakeHub
- FakeTaxi
- FakeHostel
- PublicAgent

**How it works**:
1. Select `fakehub` as Scraper Type
2. The addon automatically uses the Aylo API
3. Search by scene title to find content from any FakeHub property

---

### 5. CzechHunter Configuration

**Required Settings**: None!

CzechHunter scraper uses the public Aylo API and requires no authentication or configuration.

**Supported Studios**:
- Czech Hunter
- Debt Dandy
- Dirty Scout

**How it works**:
1. Select `czechhunter` as Scraper Type
2. The addon automatically uses the Aylo API
3. Search by scene title to find content

---

### 6. GayWire Configuration

**Required Settings**: None!

GayWire scraper uses the public Aylo API and requires no authentication or configuration.

**Supported Sites**:
- Gay Wire
- Guy Selector

**How it works**:
1. Select `gaywire` as Scraper Type
2. The addon automatically uses the Aylo API
3. Search by scene title to find content

---

### 7. PrimalFetish Configuration

**Required Settings**: None!

PrimalFetish scraper uses the public Aylo API and requires no authentication or configuration.

**How it works**:
1. Select `primalfetish` as Scraper Type
2. The addon automatically uses the Aylo API
3. Search by scene title to find content from Primal Fetish Network

---

## Using the Addon

### Searching for Content

Once configured, the addon integrates with Kodi's media library:

1. Add a video source to your Kodi library
2. Set the content type to "Movies"
3. When prompted to choose a scraper, select "Stash"
4. Kodi will automatically search for metadata when scanning your library

### Manual Metadata Lookup

To manually search for metadata:

1. Right-click on a video in your library
2. Select "Information"
3. Click "Refresh"
4. Search by title or enter the scene ID

### Scene ID Lookup

For direct scene lookup (bypasses search):

1. Right-click on a video
2. Select "Information"
3. Enter the scene ID or URL in the search field
4. The format depends on the scraper:
   - Stash: Scene ID number
   - AEBN: AEBN movie ID
   - Aylo scrapers: Scene URL or ID

## Troubleshooting

### "Cannot connect to Stash"
- Verify Stash URL is correct and includes protocol
- Check that Stash is running
- Verify API key is correct
- Check firewall settings
- Try increasing connection timeout

### "Authentication failed" (AEBN)
- Verify username and password are correct
- Check that your AEBN account is active
- Verify AEBN URL is correct

### "No results found"
- Try different search terms
- Verify the content exists in the selected source
- Check Kodi logs for error messages
- Try switching to a different scraper

### Slow Performance
- For Stash: Enable result caching
- For Stash: Reduce connection timeout
- Check your network connection
- Verify the source API is responsive

### Import Errors
Check the Kodi log file (`~/.kodi/temp/kodi.log`) for detailed error messages.

Run validation scripts:
```bash
python tools/validate_installation.py
python tools/validate_dependencies.py
```

## Best Practices

### Stash
- Use a local network connection for best performance
- Enable SSL/HTTPS if exposing Stash to the internet
- Use caching to reduce load on your Stash instance
- Keep your Stash instance updated

### AEBN
- Store credentials securely
- Don't share your account credentials
- Be aware of any rate limits on the API

### Aylo Network Scrapers
- No configuration needed - just select and use!
- Search terms should match scene titles closely
- Use specific titles for best results

## Advanced Configuration

### Switching Between Scrapers

You can switch scrapers at any time:

1. Go to addon settings
2. Change "Scraper Type"
3. Configure new scraper settings if needed
4. Refresh metadata for affected content

**Note**: Switching scrapers does not automatically re-scrape your library. You'll need to refresh metadata manually or re-scan your library.

### Multiple Libraries

If you have content from different sources:

1. Create separate video sources in Kodi
2. Set each source to use a different profile (if needed)
3. Unfortunately, you can only use one scraper configuration at a time
4. Alternative: Use Stash as a central metadata hub and use only the Stash scraper

## Getting Help

If you need assistance:

1. Check [Troubleshooting section](#troubleshooting)
2. Review scraper-specific documentation
3. Check Kodi log files for error messages
4. Run validation scripts
5. Report issues on [GitHub](https://github.com/CIRCERO/repo.circero/issues)

## Next Steps

- [Learn about each scraper](SCRAPERS.md)
- [Read scraper-specific documentation](README.md#scraper-specific-documentation)
- [Development guide](DEVELOPMENT.md) for contributing
