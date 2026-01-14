"""
Quick validation script for Primal Fetish Network scraper integration
Run this to verify the scraper is properly integrated
"""

import sys
import os

# Add the python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

def test_imports():
    """Test that all imports work correctly"""
    print("Testing imports...")
    try:
        from lib.stashscraper.primalfetish_adapter import PrimalFetishScraper
        print("? PrimalFetishScraper imported successfully")
        
        from lib.stashscraper.PrimalFetish import primalfetish
        print("? PrimalFetish module imported successfully")
        
        from lib.AyloAPI import AyloAPI
        print("? AyloAPI imported successfully")
        
        return True
    except Exception as e:
        print("? Import failed: {}".format(str(e)))
        return False

def test_scraper_creation():
    """Test that scraper can be instantiated"""
    print("\nTesting scraper creation...")
    try:
        from lib.stashscraper.primalfetish_adapter import PrimalFetishScraper
        scraper = PrimalFetishScraper()
        print("? PrimalFetishScraper created successfully")
        print("  Domains: {}".format(scraper.domains))
        return True
    except Exception as e:
        print("? Scraper creation failed: {}".format(str(e)))
        return False

def test_aylo_api_domain():
    """Test that AyloAPI recognizes primalfetish domain"""
    print("\nTesting AyloAPI domain mapping...")
    try:
        from lib.AyloAPI import AyloAPI
        api = AyloAPI()
        
        if 'primalfetish' in api.DOMAIN_MAP:
            print("? 'primalfetish' found in domain map")
            print("  Maps to: {}".format(api.DOMAIN_MAP['primalfetish']))
        else:
            print("? 'primalfetish' not found in domain map")
            return False
            
        if 'primalfetishnetwork' in api.DOMAIN_MAP:
            print("? 'primalfetishnetwork' found in domain map")
            print("  Maps to: {}".format(api.DOMAIN_MAP['primalfetishnetwork']))
        else:
            print("? 'primalfetishnetwork' not found in domain map")
            return False
        
        return True
    except Exception as e:
        print("? AyloAPI domain test failed: {}".format(str(e)))
        return False

def test_scraper_registration():
    """Test that scraper is registered in main scraper.py"""
    print("\nTesting scraper registration...")
    try:
        # Read scraper.py and check for primalfetish references
        with open(os.path.join(os.path.dirname(__file__), 'python', 'scraper.py'), 'r') as f:
            content = f.read()
        
        checks = [
            ('PrimalFetishScraper import', 'from lib.stashscraper.primalfetish_adapter import PrimalFetishScraper'),
            ('get_active_scraper registration', "scraper_type == 'primalfetish'"),
            ('get_details registration', "'primalfetish' in input_uniqueids")
        ]
        
        all_passed = True
        for check_name, check_string in checks:
            if check_string in content:
                print("? {} found".format(check_name))
            else:
                print("? {} not found".format(check_name))
                all_passed = False
        
        return all_passed
    except Exception as e:
        print("? Registration test failed: {}".format(str(e)))
        return False

def test_settings_xml():
    """Test that settings.xml includes primalfetish option"""
    print("\nTesting settings.xml...")
    try:
        with open(os.path.join(os.path.dirname(__file__), 'resources', 'settings.xml'), 'r') as f:
            content = f.read()
        
        if 'primalfetish' in content:
            print("? 'primalfetish' found in settings.xml")
            return True
        else:
            print("? 'primalfetish' not found in settings.xml")
            return False
    except Exception as e:
        print("? settings.xml test failed: {}".format(str(e)))
        return False

def main():
    """Run all validation tests"""
    print("=" * 60)
    print("Primal Fetish Network Scraper Validation")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Scraper Creation", test_scraper_creation()))
    results.append(("AyloAPI Domain", test_aylo_api_domain()))
    results.append(("Scraper Registration", test_scraper_registration()))
    results.append(("Settings Configuration", test_settings_xml()))
    
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print("{}: {}".format(test_name, status))
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("? All validation tests PASSED!")
        print("Primal Fetish Network scraper is ready to use.")
    else:
        print("? Some validation tests FAILED!")
        print("Please review the errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
