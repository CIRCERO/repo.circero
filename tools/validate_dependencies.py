"""
Validation Script - Test Self-Contained Dependencies
Run this to verify all dependencies are properly installed and importable
"""

import sys
import os

# Add lib path - adjust for new repository structure
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
lib_path = os.path.join(repo_root, 'metadata.stash.python', 'python', 'lib')
python_path = os.path.join(repo_root, 'metadata.stash.python', 'python')
mock_kodi_path = os.path.join(repo_root, 'metadata.stash.python', 'python', 'mock_kodi')
sys.path.insert(0, mock_kodi_path)
sys.path.insert(0, python_path)
sys.path.insert(0, lib_path)

print("=" * 60)
print("Metadata Stash Addon - Dependency Validation")
print("=" * 60)

errors = []
success = []

# Test 1: py_common
print("\n[TEST 1] py_common package...")
try:
    from py_common import log
    from py_common.util import dig, replace_all, replace_at
    success.append("? py_common: Logger and utilities imported")
    
    # Test dig function
    test_data = {'a': {'b': {'c': 123}}}
    result = dig(test_data, 'a', 'b', 'c')
    if result == 123:
        success.append("? py_common: dig() function works")
    else:
        errors.append("? py_common: dig() returned wrong value")
        
except Exception as e:
    errors.append("? py_common import failed: {}".format(str(e)))

# Test 2: AyloAPI
print("[TEST 2] AyloAPI package...")
try:
    from AyloAPI import (
        scraper_args,
        scene_search,
        scene_from_url,
        performer_search
    )
    success.append("? AyloAPI: Core functions imported")
    
except Exception as e:
    errors.append("? AyloAPI import failed: {}".format(str(e)))

# Test 3: Scrapers
print("[TEST 3] Scraper modules...")

scrapers_to_test = [
    ('stash', 'stashscraper.stash', 'StashScraper'),
    ('aebn', 'stashscraper.aebn', 'AEBNScraper'),
    ('brazzers_adapter', 'stashscraper.brazzers_adapter', 'BrazzersScraper'),
    ('fakehub_adapter', 'stashscraper.fakehub_adapter', 'FakeHubScraper'),
    ('czechhunter_adapter', 'stashscraper.czechhunter_adapter', 'CzechHunterScraper'),
    ('gaywire_adapter', 'stashscraper.gaywire_adapter', 'GayWireScraper'),
]

for name, module_path, class_name in scrapers_to_test:
    try:
        parts = module_path.split('.')
        module = __import__(module_path, fromlist=[parts[-1]])
        scraper_class = getattr(module, class_name)
        success.append("? Scraper: {} ({})".format(name, class_name))
    except Exception as e:
        errors.append("? Scraper {} import failed: {}".format(name, str(e)))

# Test 4: Original scrapers
print("[TEST 4] Original scraper files...")

original_scrapers = ['Brazzers', 'FakeHub', 'CzechHunter', 'GayWire']

for scraper in original_scrapers:
    try:
        module = __import__('stashscraper.{}'.format(scraper), fromlist=['stashscraper'])
        success.append("? Original: {}.py".format(scraper))
    except Exception as e:
        errors.append("? Original {} import failed: {}".format(scraper, str(e)))

# Results
print("\n" + "=" * 60)
print("VALIDATION RESULTS")
print("=" * 60)

if success:
    print("\n? PASSED ({}):\n".format(len(success)))
    for item in success:
        print("  " + item)

if errors:
    print("\n? FAILED ({}):\n".format(len(errors)))
    for item in errors:
        print("  " + item)
else:
    print("\n?? All tests passed! Dependencies are properly installed.")

print("\n" + "=" * 60)
print("Total: {} passed, {} failed".format(len(success), len(errors)))
print("=" * 60)

# Summary
if not errors:
    print("\n? READY TO USE")
    print("All dependencies are self-contained and working!")
    print("\nYou can now:")
    print("1. Restart Kodi")
    print("2. Go to Settings ? Add-ons ? Metadata.Stash")
    print("3. Choose your scraper and start using!")
else:
    print("\n?? ISSUES FOUND")
    print("Please check the errors above and ensure all files are present.")
    print("See README_FINAL.md for file structure.")

sys.exit(0 if not errors else 1)
