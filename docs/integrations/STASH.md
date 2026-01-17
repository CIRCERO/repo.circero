# Stash Integration

The Stash scraper provides integration with [StashApp](https://stashapp.cc), a self-hosted media library management system.

## Overview

**Scraper ID**: `stash`  
**Type**: Self-hosted GraphQL API  
**Authentication**: API Key  
**Status**: ✅ Fully Functional

## What is Stash?

Stash is an organizer and manager for your adult media collection. It provides:
- Web-based interface
- Scene/movie management
- Performer management
- Tag and studio organization
- Image gallery support
- Custom metadata
- GraphQL API for programmatic access

## Features

The Stash scraper supports:

✅ Scene/movie search by title  
✅ Scene details by ID or URL  
✅ Performer information  
✅ Studio information  
✅ Tags and categories  
✅ Multiple images (poster, fanart, etc.)  
✅ Release dates and duration  
✅ Custom metadata fields  
✅ Reliable retry logic with exponential backoff  
✅ Configurable timeouts  
✅ Optional result caching  

## Configuration

### Required Settings

#### Stash URL
The URL where your Stash instance is running.

**Examples**:
- `http://localhost:9999` (local instance)
- `http://192.168.1.100:9999` (LAN instance)
- `https://stash.example.com` (remote instance with SSL)

**Important**: 
- Include the protocol (`http://` or `https://`)
- Include the port if not using defaults (80/443)
- Do NOT include a trailing slash

#### API Key
Your Stash API key for authentication.

**How to get your API Key**:
1. Open Stash web interface
2. Navigate to **Settings** > **Security**
3. Scroll to **API Key** section
4. Click **Generate API Key** if you don't have one
5. Copy the key (it looks like: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

**Security Notes**:
- Keep your API key secret
- Don't share it publicly
- Regenerate if compromised
- The key is stored in Kodi settings (not in plain text in your file system)

### Advanced Settings

#### Connection Timeout (seconds)
- **Default**: 30 seconds
- **Range**: 10-300 seconds
- **Description**: Maximum time to wait for Stash to respond
- **When to adjust**: 
  - Increase if you have a slow network or large library
  - Decrease if you want faster failures on connection issues

#### Max Retry Attempts
- **Default**: 3 attempts
- **Range**: 1-10 attempts
- **Description**: Number of times to retry failed requests
- **Behavior**: Uses exponential backoff (2 seconds base delay)
- **When to adjust**:
  - Increase for unreliable networks
  - Decrease to fail faster

#### Enable Result Caching
- **Default**: Disabled
- **Description**: Cache search results to reduce API calls to Stash
- **When to enable**:
  - Large library with frequent searches
  - Slow Stash instance
  - Limited bandwidth to Stash
- **Trade-off**: May show stale data if Stash is updated

#### Cache Duration (hours)
- **Default**: 24 hours
- **Range**: 1-168 hours (1 week)
- **Description**: How long to keep cached results
- **Only applies if caching is enabled**

## Usage

### Initial Setup

1. Install and configure Stash (see [Stash documentation](https://github.com/stashapp/stash))
2. Add content to your Stash library
3. Configure the Kodi addon with your Stash URL and API key
4. Add video sources to Kodi library
5. Kodi will automatically fetch metadata from Stash

### Searching by Title

When Kodi scans your library, it searches Stash by filename or title:

1. Kodi extracts the title from filename
2. Sends search query to Stash GraphQL API
3. Stash returns matching scenes
4. Kodi presents matches for you to select
5. Selected scene metadata is saved to Kodi library

### Direct Scene Lookup

If you know the Stash scene ID:

1. Right-click video in Kodi
2. Select "Information"
3. Click "Refresh" or "Choose"
4. Enter the scene ID (number from Stash URL)

### Metadata Fields

The scraper fetches these fields from Stash:

- **Title**: Scene title
- **Plot**: Scene description/details
- **Studio**: Studio name
- **Release Date**: Scene release date
- **Duration**: Video duration
- **Tags**: Scene tags/categories
- **Performers**: Cast members with:
  - Name
  - Role
  - Profile image
- **Images**:
  - Poster (primary scene image)
  - Fanart (background art)
  - Additional scene images

## Architecture

### GraphQL Queries

The scraper uses Stash's GraphQL API:

**Scene Search**:
```graphql
query FindScenes($filter: FindFilterType) {
  findScenes(scene_filter: {}, filter: $filter) {
    count
    scenes {
      id
      title
      details
      url
      date
      rating
      studio { name }
      tags { name }
      performers { name }
      paths { screenshot }
    }
  }
}
```

**Scene Details**:
```graphql
query FindScene($id: ID!) {
  findScene(id: $id) {
    id
    title
    details
    url
    date
    rating
    studio { name }
    tags { name }
    performers {
      name
      image_path
    }
    paths {
      screenshot
      preview
      stream
    }
  }
}
```

### Error Handling

The scraper implements robust error handling:

1. **Connection Errors**: Retries with exponential backoff
2. **Timeout Errors**: Respects configured timeout setting
3. **Authentication Errors**: Clear error messages about API key
4. **Invalid Responses**: Graceful degradation with partial data
5. **Network Errors**: Retry logic with meaningful logging

### Performance

**Typical Response Times**:
- Local network: 100-500ms
- Remote network: 500-2000ms
- Large libraries: May be slower for searches

**Optimization Tips**:
- Use local network connection when possible
- Enable result caching for frequently accessed content
- Keep Stash database optimized
- Use direct scene ID lookup when possible

## Troubleshooting

### Cannot Connect to Stash

**Symptom**: "Unable to connect to Stash" error

**Solutions**:
1. Verify Stash is running (open web interface in browser)
2. Check Stash URL format (include `http://` or `https://`)
3. Verify port number is correct
4. Check firewall settings (allow Kodi to access Stash)
5. Try accessing Stash URL from Kodi's device
6. Check Kodi log for detailed error messages

### Authentication Failed

**Symptom**: "Authentication failed" or "Invalid API key"

**Solutions**:
1. Verify API key is correct (copy-paste from Stash settings)
2. Check for extra spaces in API key field
3. Regenerate API key in Stash and update in Kodi
4. Ensure API key hasn't been revoked in Stash

### No Results Found

**Symptom**: Search returns no results

**Solutions**:
1. Verify content exists in Stash (check Stash web interface)
2. Try different search terms
3. Check that scene has a title in Stash
4. Verify Stash API is responding (test with GraphQL playground)
5. Check Kodi log for API response

### Slow Performance

**Symptom**: Searches take a long time

**Solutions**:
1. Enable result caching in addon settings
2. Optimize Stash database (Stash Settings > Tasks > Optimize Database)
3. Use SSD for Stash database
4. Reduce connection timeout for faster failures
5. Use direct scene ID lookup instead of search

### SSL Certificate Errors

**Symptom**: SSL certificate verification errors

**Solutions**:
1. Ensure Stash SSL certificate is valid
2. For self-signed certificates, you may need to configure Kodi to accept them
3. Consider using HTTP for local network (if security allows)

## Best Practices

### For Best Performance

1. **Use Local Network**: Install Stash on the same network as Kodi
2. **Enable Caching**: For large libraries or slow networks
3. **Direct Lookups**: Use scene IDs when possible
4. **Keep Updated**: Keep both Stash and addon updated

### For Best Metadata Quality

1. **Organize in Stash**: Add metadata in Stash first
2. **Use Scrapers**: Use Stash's built-in scrapers to populate metadata
3. **Add Images**: Ensure scenes have good quality images
4. **Tag Appropriately**: Use relevant tags for better organization
5. **Complete Performer Info**: Add performer details in Stash

### Security

1. **Use HTTPS**: For remote access, use HTTPS with valid certificate
2. **Secure API Key**: Don't share or commit API key
3. **Network Security**: Use VPN or secure network for remote access
4. **Regular Backups**: Backup Stash database regularly

## Advanced Usage

### Using with Stash Scrapers

Stash has many community scrapers. Use this workflow:

1. Add content to Stash
2. Use Stash's scrapers to fetch metadata from various sources
3. Organize and edit metadata in Stash
4. Use Kodi addon to fetch the curated metadata

**Benefits**:
- Centralized metadata management
- Multiple source aggregation
- Manual curation capability
- Single source of truth

### Integration with Other Tools

Stash can integrate with:
- StashDB (community database)
- Third-party scrapers
- Custom scripts via API
- Other media management tools

The Kodi addon fetches whatever metadata you've collected in Stash.

## Version History

### Version 2.0.0 (January 2026)
- ✅ Enhanced error handling with retry logic
- ✅ Configurable timeouts
- ✅ Optional result caching
- ✅ Improved logging
- ✅ Better connection validation

### Version 1.x
- Initial Stash integration
- Basic search and metadata fetch
- GraphQL API support

## Resources

- **Stash Project**: https://github.com/stashapp/stash
- **Stash Documentation**: https://docs.stashapp.cc
- **Stash Discord**: https://discord.gg/2TsNFKt
- **StashDB**: https://stashdb.org

## Support

For issues specific to the Stash scraper:
1. Check this documentation
2. Review Kodi logs
3. Test Stash API directly (GraphQL playground)
4. Report issues: https://github.com/CIRCERO/repo.circero/issues
