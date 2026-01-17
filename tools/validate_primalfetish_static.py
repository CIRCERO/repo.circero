"""
Static validation for Primal Fetish Network scraper integration
This checks file presence and content without requiring Kodi to be running
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print("? {} exists".format(description))
        return True
    else:
        print("? {} NOT FOUND: {}".format(description, filepath))
        return False

def check_file_contains(filepath, search_terms, description):
    """Check if file contains specific terms"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        all_found = True
        for term in search_terms:
            if term in content:
                print("  ? Contains: {}".format(term))
            else:
                print("  ? Missing: {}".format(term))
                all_found = False
        
        if all_found:
            print("? {} validation passed".format(description))
        else:
            print("? {} validation failed".format(description))
        
        return all_found
    except Exception as e:
        print("? Error reading {}: {}".format(description, str(e)))
        return False

def main():
    """Run static validation"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 70)
    print("Primal Fetish Network Scraper - Static Validation")
    print("Base directory: {}".format(base_dir))
    print("=" * 70)
    
    results = []
    
    # Check file existence
    print("\n[1] Checking file existence...")
    files_to_check = [
        (os.path.join(base_dir, 'python', 'lib', 'stashscraper', 'PrimalFetish.py'), 
         'PrimalFetish.py'),
        (os.path.join(base_dir, 'python', 'lib', 'stashscraper', 'primalfetish_adapter.py'),
         'primalfetish_adapter.py'),
    ]
    
    for filepath, desc in files_to_check:
        results.append(check_file_exists(filepath, desc))
    
    # Check PrimalFetish.py content
    print("\n[2] Checking PrimalFetish.py content...")
    pf_path = os.path.join(base_dir, 'python', 'lib', 'stashscraper', 'PrimalFetish.py')
    results.append(check_file_contains(
        pf_path,
        ['def primalfetish(obj, _):', 'primalfetish', 'primalfetishnetwork', 'scene_search'],
        'PrimalFetish.py'
    ))
    
    # Check primalfetish_adapter.py content
    print("\n[3] Checking primalfetish_adapter.py content...")
    adapter_path = os.path.join(base_dir, 'python', 'lib', 'stashscraper', 'primalfetish_adapter.py')
    results.append(check_file_contains(
        adapter_path,
        ['class PrimalFetishScraper:', 'def search(self, title', 'def get_details(self, scene_id'],
        'primalfetish_adapter.py'
    ))
    
    # Check AyloAPI integration
    print("\n[4] Checking AyloAPI domain mapping...")
    aylo_path = os.path.join(base_dir, 'python', 'lib', 'AyloAPI', '__init__.py')
    results.append(check_file_contains(
        aylo_path,
        ["'primalfetish'", "'primalfetishnetwork'", "primalfetishnetwork.com"],
        'AyloAPI/__init__.py'
    ))
    
    # Check main scraper.py integration
    print("\n[5] Checking scraper.py integration...")
    scraper_path = os.path.join(base_dir, 'python', 'scraper.py')
    results.append(check_file_contains(
        scraper_path,
        [
            'from lib.stashscraper.primalfetish_adapter import PrimalFetishScraper',
            "scraper_type == 'primalfetish'",
            "'primalfetish' in input_uniqueids"
        ],
        'scraper.py'
    ))
    
    # Check settings.xml
    print("\n[6] Checking settings.xml configuration...")
    settings_path = os.path.join(base_dir, 'resources', 'settings.xml')
    results.append(check_file_contains(
        settings_path,
        ['primalfetish'],
        'settings.xml'
    ))
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    total_checks = len(results)
    passed_checks = sum(results)
    failed_checks = total_checks - passed_checks
    
    print("Total checks: {}".format(total_checks))
    print("Passed: {}".format(passed_checks))
    print("Failed: {}".format(failed_checks))
    
    if all(results):
        print("\n??? ALL CHECKS PASSED! ???")
        print("\nThe Primal Fetish Network scraper is properly integrated!")
        print("\nTo use it:")
        print("1. Open Kodi")
        print("2. Go to Add-on Settings for 'Stash Scraper'")
        print("3. Select 'Primal Fetish Network' from Scraper Type dropdown")
        print("4. Start scraping!")
        return 0
    else:
        print("\n??? SOME CHECKS FAILED ???")
        print("\nPlease review the errors above and fix any issues.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
