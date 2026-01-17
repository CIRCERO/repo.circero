"""
File Structure Validation - Verify all files exist
This validation works outside of Kodi
"""

import os

print("=" * 60)
print("Metadata Stash Addon - File Structure Validation")
print("=" * 60)

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
addon_path = os.path.join(base_path, 'metadata.stash.python')
python_path = os.path.join(addon_path, 'python')
lib_path = os.path.join(python_path, 'lib')

print("\nBase path: {}".format(base_path))
print("Addon path: {}".format(addon_path))

required_files = {
    'Core Files': [
        ('python/scraper.py', 'Main scraper entry point'),
        ('python/scraper_config.py', 'Configuration helper'),
        ('python/scraper_datahelper.py', 'Data helper'),
        ('resources/settings.xml', 'Settings configuration'),
    ],
    'py_common Package': [
        ('python/lib/py_common/__init__.py', 'Logger module'),
        ('python/lib/py_common/util.py', 'Utility functions'),
    ],
    'AyloAPI Package': [
        ('python/lib/AyloAPI/__init__.py', 'Core API client'),
        ('python/lib/AyloAPI/scrape.py', 'Scraping interface'),
    ],
    'Scraper Adapters': [
        ('python/lib/stashscraper/brazzers_adapter.py', 'Brazzers adapter'),
        ('python/lib/stashscraper/fakehub_adapter.py', 'FakeHub adapter'),
        ('python/lib/stashscraper/czechhunter_adapter.py', 'Czech Hunter adapter'),
        ('python/lib/stashscraper/gaywire_adapter.py', 'Gay Wire adapter'),
    ],
    'Original Scrapers': [
        ('python/lib/stashscraper/stash.py', 'Stash scraper'),
        ('python/lib/stashscraper/aebn.py', 'AEBN scraper'),
        ('python/lib/stashscraper/Brazzers.py', 'Brazzers scraper'),
        ('python/lib/stashscraper/FakeHub.py', 'FakeHub scraper'),
        ('python/lib/stashscraper/CzechHunter.py', 'Czech Hunter scraper'),
        ('python/lib/stashscraper/GayWire.py', 'Gay Wire scraper'),
    ],
    'Documentation': [
        ('README.md', 'Addon README'),
        ('python/lib/stashscraper/README_SCRAPERS.md', 'Scraper documentation'),
    ]
}

total_files = 0
found_files = 0
missing_files = []

for category, files in required_files.items():
    print("\n[{}]".format(category))
    for rel_path, description in files:
        total_files += 1
        full_path = os.path.join(addon_path, rel_path)
        exists = os.path.isfile(full_path)
        
        if exists:
            found_files += 1
            size = os.path.getsize(full_path)
            print("  ? {} ({} bytes)".format(description, size))
        else:
            missing_files.append((rel_path, description))
            print("  ? {} - MISSING!".format(description))

# Results
print("\n" + "=" * 60)
print("VALIDATION RESULTS")
print("=" * 60)

print("\nFiles found: {}/{}".format(found_files, total_files))

if missing_files:
    print("\n? MISSING FILES:")
    for path, desc in missing_files:
        print("  - {} ({})".format(path, desc))
    print("\n?? Some files are missing. Installation incomplete.")
else:
    print("\n? ALL FILES PRESENT")
    print("\n?? Installation is complete and self-contained!")
    print("\nNext steps:")
    print("1. Restart Kodi to load the updated addon")
    print("2. Go to Settings ? Add-ons ? Metadata.Stash")
    print("3. Select your preferred scraper from the dropdown")
    print("4. Configure any required settings (URL, credentials)")
    print("5. Start scraping!")
    
    print("\n?? Available scrapers:")
    print("  1. Stash - StashApp API (requires URL + API key)")
    print("  2. AEBN - AEBN.com (requires credentials)")
    print("  3. Brazzers - Brazzers.com (no config needed)")
    print("  4. FakeHub - FakeHub network (no config needed)")
    print("  5. Czech Hunter - Czech Hunter network (no config needed)")
    print("  6. Gay Wire - Gay Wire network (no config needed)")

print("\n" + "=" * 60)
