# Installation Guide

This guide covers installing the CIRCERO repository and the metadata.stash.python addon in Kodi.

## Prerequisites

- **Kodi Version**: 19.x (Matrix) or newer
- **Python Version**: 3.x (included with Kodi)
- **Internet Connection**: Required for downloading addon and fetching metadata

## Method 1: Install from Repository (Recommended)

Installing from the repository ensures you receive automatic updates.

### Step 1: Download Repository Addon

1. Download the latest `repository.circero-{version}.zip` from:
   - [GitHub Releases](https://github.com/CIRCERO/repo.circero/releases)
   - Or direct link: `https://raw.githubusercontent.com/CIRCERO/repo.circero/main/repo/repository.circero-1.0.0.zip`

### Step 2: Install Repository in Kodi

1. Open **Kodi**
2. Navigate to **Settings** (gear icon)
3. Select **Add-ons**
4. Click **Install from zip file**
   - If this is your first time, you may need to enable "Unknown sources" in Settings > System > Add-ons
5. Browse to the downloaded `repository.circero-{version}.zip`
6. Wait for the "Repository enabled" notification

### Step 3: Install Metadata Addon

1. In Kodi, go to **Add-ons** > **Install from repository**
2. Select **CIRCERO Repository**
3. Navigate to **Information providers** > **Movie information**
4. Select **Stash** (metadata.stash.python)
5. Click **Install**
6. Wait for installation to complete

### Step 4: Configure Scraper

See [Configuration Guide](CONFIGURATION.md) for detailed setup instructions for each scraper.

## Method 2: Manual Installation

For advanced users or when repository installation is not possible.

### Step 1: Download Addon

Download the latest `metadata.stash.python-{version}.zip` from:
- [GitHub Releases](https://github.com/CIRCERO/repo.circero/releases)
- Or generate it using: `python tools/generate_repo.py`

### Step 2: Install in Kodi

1. Open **Kodi**
2. Navigate to **Settings** > **Add-ons**
3. Click **Install from zip file**
4. Browse to the downloaded ZIP file
5. Wait for installation confirmation

**Note**: Manual installations do not receive automatic updates.

## Method 3: Development Installation

For developers who want to modify the addon.

### Step 1: Clone Repository

```bash
git clone https://github.com/CIRCERO/repo.circero.git
cd repo.circero
```

### Step 2: Create Symlink

Create a symbolic link from Kodi's addon directory to your local repository:

**Linux/macOS**:
```bash
ln -s $(pwd)/metadata.stash.python ~/.kodi/addons/metadata.stash.python
```

**Windows** (Command Prompt as Administrator):
```cmd
mklink /D "%APPDATA%\Kodi\addons\metadata.stash.python" "C:\path\to\repo.circero\metadata.stash.python"
```

### Step 3: Restart Kodi

Restart Kodi to load the addon.

## Post-Installation

### Verify Installation

1. Go to **Settings** > **Add-ons** > **My add-ons**
2. Navigate to **Information providers** > **Movie information**
3. You should see **Stash** listed
4. Click on it to see version and description

### Troubleshooting

#### Addon Doesn't Appear

- Ensure you're looking in **Information providers** > **Movie information**
- Try restarting Kodi
- Check Kodi log file for errors: `~/.kodi/temp/kodi.log`

#### Installation Fails

- Verify the ZIP file is not corrupted (re-download if needed)
- Ensure "Unknown sources" is enabled
- Check available disk space

#### Dependencies Missing

The addon should have no external dependencies. If you see dependency errors:

1. Try reinstalling the addon
2. Check the [validation scripts](../tools/README.md) in the tools directory
3. Report the issue on [GitHub Issues](https://github.com/CIRCERO/repo.circero/issues)

### Running Validation Scripts

After installation, you can validate your setup:

```bash
cd repo.circero
python tools/validate_installation.py
python tools/validate_dependencies.py
```

## Next Steps

- [Configure your preferred scraper](CONFIGURATION.md)
- [Learn about available scrapers](SCRAPERS.md)
- [Read scraper-specific documentation](README.md#scraper-specific-documentation)

## Uninstallation

To remove the addon:

1. Go to **Settings** > **Add-ons** > **My add-ons**
2. Navigate to **Information providers** > **Movie information**
3. Select **Stash**
4. Click **Uninstall**

To remove the repository:

1. Go to **Settings** > **Add-ons** > **My add-ons**
2. Navigate to **Install from repository**
3. Right-click on **CIRCERO Repository**
4. Select **Uninstall** or **Information** > **Uninstall**
