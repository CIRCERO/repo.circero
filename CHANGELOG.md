# Changelog - Stash Metadata Scraper

## Version 2.0.0 - January 15, 2026

### ?? Major Improvements

#### Enhanced Error Handling & Reliability
- **Automatic Retry Logic**: Added intelligent retry mechanism for transient network failures
  - Retries on HTTP 5xx server errors
  - Retries on connection timeouts and network issues
  - Configurable retry attempts (default: 3)
  - Exponential backoff with 2-second delay

#### Performance & Configuration
- **Configurable Timeouts**: User-adjustable connection timeout settings (default: 30s)
- **Result Caching**: Optional caching system to reduce API calls
  - Configurable cache duration (default: 24 hours)
  - Improves performance for frequently accessed content

#### Better Logging & Debugging
- **Enhanced Logging**: Improved log messages with clear prefixes
  - Request attempt tracking (1/3, 2/3, 3/3)
  - Detailed error context and stack traces
  - Success/failure status logging
  - Connection parameter logging

#### Stability Improvements
- **Graceful Degradation**: Better handling of partial failures
- **Connection Validation**: Validates Stash instance connectivity
- **SSL Certificate Handling**: Improved support for self-signed certificates
- **Error Recovery**: More robust error recovery mechanisms

### ?? Technical Changes

#### Modified Files
1. **python/lib/stashscraper/stash.py**
   - Added `time` module for retry delays
   - Implemented `_make_request()` retry logic with exponential backoff
   - Added configurable timeout and max_retries from settings
   - Enhanced error messages with detailed context

2. **resources/settings.xml**
   - Added "Connection Timeout (seconds)" setting
   - Added "Max Retry Attempts" setting
   - Added "Enable Result Caching" option
   - Added "Cache Duration (hours)" setting

3. **addon.xml**
   - Version bumped to 2.0.0
   - Updated changelog reference

### ?? Bug Fixes
- Fixed connection timeout issues with slow Stash instances
- Improved handling of HTTP 5xx server errors
- Better error reporting for network failures
- Fixed SSL certificate validation issues

### ?? Notes
- All existing scrapers (Stash, AEBN, Brazzers, FakeHub, CzechHunter, GayWire, PrimalFetish) benefit from improvements
- Backward compatible with existing configurations
- No breaking changes to API or user workflows

### ?? Settings Migration
Users can now configure:
- **Connection Timeout**: Adjust for slower networks (Settings ? General)
- **Max Retries**: Control retry attempts for failed requests
- **Cache Settings**: Enable caching for better performance

### ?? Future Improvements
- [ ] Add request queue management
- [ ] Implement connection pooling
- [ ] Add metrics/statistics tracking
- [ ] Enhanced cache invalidation strategies
- [ ] Support for proxy configurations

---

## Version 1.1.0 - December 30, 2025
- Added Primal Fetish Network scraper support
- Initial multi-scraper architecture

## Version 1.0.0 - Initial Release
- Basic Stash scraper functionality
- AEBN scraper support
