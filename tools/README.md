# Development Tools

This directory contains development and maintenance tools for the CIRCERO repository.

## Repository Generation

### generate_repo.py
Generates the Kodi repository files needed for distribution.

**Usage:**
```bash
python tools/generate_repo.py
```

**What it does:**
- Scans addon directories for addon.xml files
- Generates `repo/addons.xml` index file
- Creates MD5 checksum file
- Creates ZIP packages for each addon
- Places all files in `repo/` directory

**Output:**
- `repo/addons.xml` - Repository index
- `repo/addons.xml.md5` - MD5 checksum
- `repo/metadata.stash.python-{version}.zip` - Addon package
- `repo/repository.circero-{version}.zip` - Repository addon package

## Validation Scripts

### validate_installation.py
Validates the Kodi addon installation and dependencies.

**Usage:**
```bash
python tools/validate_installation.py
```

### validate_dependencies.py
Checks Python dependencies for the addon.

**Usage:**
```bash
python tools/validate_dependencies.py
```

### validate_primalfetish.py
Validates PrimalFetish scraper integration.

**Usage:**
```bash
python tools/validate_primalfetish.py
```

### validate_primalfetish_static.py
Performs static validation of PrimalFetish files and configuration.

**Usage:**
```bash
python tools/validate_primalfetish_static.py
```

## Development Workflow

1. **Make changes** to addon code in `metadata.stash.python/`
2. **Test locally** using validation scripts
3. **Update version** in `metadata.stash.python/addon.xml`
4. **Generate repository** using `generate_repo.py`
5. **Commit and push** changes
6. **Create release** on GitHub (triggers automatic repository generation)

## Notes

- Validation scripts may need to be run from the repository root
- Some scripts may require the Kodi environment to function properly
- See individual script files for more detailed usage information
