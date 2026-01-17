# AEBN Integration

Integration with Adult Entertainment Broadcast Network (AEBN) metadata database.

## Overview

**Scraper ID**: `aebn`  
**Type**: Commercial Database API  
**Authentication**: Username/Password  
**Status**: ✅ Fully Functional

## What is AEBN?

AEBN (Adult Entertainment Broadcast Network) is a major commercial database and distribution platform for adult entertainment content. It provides professional metadata for movies and scenes.

## Features

✅ Scene/movie search by title and year  
✅ Detailed scene metadata  
✅ Performer information  
✅ Studio information  
✅ Multiple image support  
✅ DVD/Blu-ray release information  
✅ Professional metadata quality  

## Configuration

### Required Settings

#### AEBN URL
The base URL for your AEBN API access.

**Example**: `https://aebn.com` (or your specific AEBN instance)

#### Username
Your AEBN account username.

#### Password
Your AEBN account password.

**Security Note**: Password is stored in Kodi settings, not in plain text.

## Usage

1. Configure addon with AEBN credentials
2. Select `aebn` as Scraper Type
3. Add video sources to Kodi library
4. Kodi will search AEBN database for metadata

### Search by Title
The addon searches AEBN by title and optional year, returning professional metadata for matching content.

## Metadata Fields

- Title
- Plot/Description
- Studio
- Release Date
- Duration
- Performers (cast)
- Director
- Images (poster, fanart)
- DVD/Blu-ray information

## Troubleshooting

### Authentication Failed
- Verify username and password are correct
- Check AEBN account is active
- Verify AEBN URL is correct

### No Results Found
- Verify content exists in AEBN database
- Try different search terms
- Check if content is commercial release

## Requirements

- Active AEBN account with API access
- Valid username and password
- Internet connection

## Resources

- **AEBN Website**: https://aebn.com
- **Support**: Contact AEBN for API access questions
