# Frame Extraction Feature

## Overview
Added a new feature that allows users to extract frames from video files and use them as poster, fanart, or thumb artwork in Kodi.

## Features

### Manual Mode
- User selects specific time position (HH:MM:SS format)
- Extracts single frame at chosen timestamp
- Interactive time input dialog

### Auto Mode
- Automatically extracts multiple frames at even intervals
- Configurable frame count (default: 5 frames)
- Evenly distributed throughout video duration

## Settings Added

### Frame Extraction Category (ID: 32041)
Located in: `resources/settings.xml`

1. **Enable frame extraction** (ID: `enable_frame_extraction`)
   - Type: Boolean
   - Default: false
   - Enables/disables the entire feature

2. **Extraction method** (ID: `frame_extraction_method`)
   - Type: Select (manual|auto)
   - Default: manual
   - Choose between manual time selection or automatic extraction

3. **Number of frames** (ID: `auto_frame_count`)
   - Type: Number
   - Default: 5
   - Only visible/enabled in auto mode
   - Controls how many frames to extract

4. **Frame storage path** (ID: `frame_storage_path`)
   - Type: Folder
   - Default: empty (uses temp directory)
   - Where extracted frames are saved

5. **Prompt on scrape** (ID: `frame_prompt_on_scrape`)
   - Type: Boolean
   - Default: true
   - Ask to extract frames when scraping metadata

## Localization Strings Added

Added to: `resources/language/resource.language.en_gb/strings.po`

- `#32041` - "Frame Extraction" (category title)
- `#32042` - "Enable frame extraction from video files"
- `#32043` - "Extraction method"
- `#32044` - "Number of frames to extract (auto mode)"
- `#32045` - "Frame storage path"
- `#32046` - "Prompt to extract frames when scraping"
- `#32047` - "Info"
- `#32048` - "Extract frames from video files to use as poster, fanart, or thumb artwork"
- `#32049` - "Extract Frame"
- `#32050` - "Select time position for frame extraction"
- `#32051` - "Use as Poster"
- `#32052` - "Use as Fanart"
- `#32053` - "Use as Thumb"
- `#32054` - "Frame extracted successfully"
- `#32055` - "Failed to extract frame"
- `#32056` - "Extract frames from video?"
- `#32057` - "Would you like to extract frames from the video file to use as artwork?"

## Functions Added

Located in: `python/scraper.py`

### 1. `extract_video_frame(video_path, time_seconds, output_path)`
Core function that extracts a frame from video using Kodi's Player API.

**Parameters:**
- `video_path`: Full path to video file
- `time_seconds`: Time position in seconds
- `output_path`: Where to save the extracted frame

**Returns:** `True` if successful, `False` otherwise

**How it works:**
1. Validates video path
2. Starts Kodi Player with video
3. Seeks to specified time
4. Uses `TakeScreenshot()` to capture frame
5. Stops playback if it wasn't already playing
6. Verifies frame was saved

### 2. `get_video_file_path(details, settings)`
Attempts to find the video file path for a scene.

**Parameters:**
- `details`: Scene details dictionary
- `settings`: Addon settings

**Returns:** Video file path or `None`

**How it works:**
1. Checks for Stash uniqueid in details
2. Queries Stash API for scene files (if StashScraper supports it)
3. Returns first file path found

### 3. `prompt_frame_extraction(details, settings, handle)`
Main user-facing function that prompts for frame extraction.

**Parameters:**
- `details`: Scene details dictionary
- `settings`: Addon settings
- `handle`: Kodi handle

**Returns:** Updated details dictionary with extracted frames

**Workflow:**
1. Asks user if they want to extract frames (yes/no dialog)
2. Attempts to get video path automatically
3. If automatic fails, opens file browser for manual selection
4. Based on extraction method:
   - **Manual**: Shows time input dialog (HH:MM:SS)
   - **Auto**: Extracts multiple frames at even intervals
5. Adds all extracted frames to `available_art` lists
6. Shows notification with result

### 4. `extract_single_frame(video_path, time_seconds, settings)`
Helper function to extract one frame with proper naming.

**Parameters:**
- `video_path`: Path to video file
- `time_seconds`: Time position
- `settings`: Addon settings

**Returns:** Path to extracted frame or `None`

**How it works:**
1. Gets storage path from settings (or temp dir)
2. Creates safe filename from video name + timestamp
3. Calls `extract_video_frame()`
4. Returns path to saved frame

## Integration

The feature integrates into the scraping workflow:

```python
# In get_details() function
details = configure_scraped_details(details, settings)

# Add web image search if enabled
if settings.getSettingBool('enable_web_image_search'):
    details = add_web_images(details, settings)

# NEW: Offer frame extraction if enabled
if settings.getSettingBool('enable_frame_extraction') and settings.getSettingBool('frame_prompt_on_scrape'):
    details = prompt_frame_extraction(details, settings, handle)

listitem = xbmcgui.ListItem(details['info']['title'], offscreen=True)
```

## Usage Instructions

### For Users:

1. **Enable the Feature:**
   - Go to Add-on Settings ? Frame Extraction
   - Enable "Enable frame extraction from video files"

2. **Configure Settings:**
   - Choose extraction method (Manual or Auto)
   - If Auto, set number of frames to extract
   - Optionally set custom storage path
   - Leave "Prompt on scrape" enabled to be asked each time

3. **Extract Frames:**
   - When scraping metadata, you'll be prompted
   - Select your video file (if not auto-detected)
   - Choose time position (Manual) or let it auto-extract (Auto)
   - Extracted frames appear in "Choose Art" dialog

4. **Apply Frames:**
   - In Kodi's "Choose Art" dialog
   - Select the extracted frame
   - Choose art type (poster/fanart/thumb)

## Technical Notes

- **Kodi Player API**: Uses `xbmc.Player()` to play video and seek
- **Screenshot Method**: Uses `xbmc.executebuiltin('TakeScreenshot')`
- **File Naming**: Format: `{video_name}_{timestamp}.jpg`
- **Safe Filenames**: Special characters replaced with underscores
- **Multiple Art Types**: Frames added to poster, fanart, and thumb lists
- **Error Handling**: Comprehensive try/catch with logging
- **Timeout Protection**: 30-second timeout for video playback start

## Limitations

1. Requires video file to be accessible to Kodi
2. Screenshot quality depends on Kodi's rendering
3. Manual mode requires user to know video duration
4. Auto mode requires video to be playable for duration detection
5. Frame extraction happens during scraping (may add delay)

## Future Enhancements

Potential improvements:
- Video timeline scrubber UI for precise frame selection
- Thumbnail preview before saving
- Batch extraction without playback (direct FFmpeg integration)
- Frame quality/format settings (JPEG quality, PNG support)
- Crop/resize options
- Multiple frame selection in one session
- Integration with Stash's sprite generation

## Files Modified

1. `resources/settings.xml` - Added Frame Extraction category
2. `resources/language/resource.language.en_gb/strings.po` - Added localized strings
3. `python/scraper.py` - Added extraction functions and integration

## Testing Recommendations

1. Test manual extraction with various time formats
2. Test auto extraction with different frame counts
3. Test with videos of various lengths
4. Test storage path with custom and default locations
5. Test error handling (missing video, invalid paths)
6. Test integration with existing artwork
7. Verify frames appear in "Choose Art" dialog
8. Test with different video formats/codecs

---

**Date Added:** January 1, 2026
**Version:** 1.2.0 (suggested)
