#!/usr/bin/env python3
"""
Repository Generator for Kodi Addons

This script generates the necessary files for a Kodi repository:
- addons.xml: Index of all available addons
- addons.xml.md5: MD5 checksum of addons.xml
- Zipped addon packages for distribution

Usage:
    python generate_repo.py

The script will:
1. Scan for addon directories (containing addon.xml)
2. Generate addons.xml from all found addons
3. Create MD5 checksum
4. Create ZIP files for each addon
5. Place all files in the repo/ directory
"""

import os
import sys
import hashlib
import zipfile
import shutil
from xml.etree import ElementTree as ET
from pathlib import Path

# Directories to scan for addons
ADDON_DIRS = ['metadata.stash.python', 'repository.circero']

# Output directory
REPO_DIR = 'repo'

# Directories to exclude from ZIP files
EXCLUDE_DIRS = ['.git', '__pycache__', '.vscode', '.idea']
EXCLUDE_FILES = ['.gitignore', '.DS_Store']


def get_addon_info(addon_path):
    """Extract addon information from addon.xml"""
    addon_xml_path = os.path.join(addon_path, 'addon.xml')
    
    if not os.path.exists(addon_xml_path):
        return None
    
    try:
        tree = ET.parse(addon_xml_path)
        root = tree.getroot()
        
        addon_id = root.get('id')
        version = root.get('version')
        
        return {
            'id': addon_id,
            'version': version,
            'path': addon_path,
            'xml': root
        }
    except Exception as e:
        print(f"Error parsing {addon_xml_path}: {e}")
        return None


def generate_addons_xml(addons):
    """Generate addons.xml from list of addon info"""
    root = ET.Element('addons')
    
    for addon in addons:
        root.append(addon['xml'])
    
    tree = ET.ElementTree(root)
    ET.indent(tree, space='    ')
    
    return tree


def generate_md5(filepath):
    """Generate MD5 checksum for a file"""
    md5_hash = hashlib.md5()
    
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5_hash.update(chunk)
    
    return md5_hash.hexdigest()


def create_addon_zip(addon_info, output_dir):
    """Create a ZIP file for an addon"""
    addon_id = addon_info['id']
    version = addon_info['version']
    addon_path = addon_info['path']
    
    zip_name = f"{addon_id}-{version}.zip"
    zip_path = os.path.join(output_dir, zip_name)
    
    print(f"Creating {zip_name}...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(addon_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file in EXCLUDE_FILES:
                    continue
                
                file_path = os.path.join(root, file)
                arcname = os.path.join(addon_id, os.path.relpath(file_path, addon_path))
                zipf.write(file_path, arcname)
    
    print(f"Created {zip_name} ({os.path.getsize(zip_path)} bytes)")
    return zip_path


def main():
    """Main function to generate repository files"""
    print("=" * 60)
    print("CIRCERO Repository Generator")
    print("=" * 60)
    
    # Get script directory (should be tools/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    
    print(f"\nRepository root: {repo_root}")
    print(f"Output directory: {os.path.join(repo_root, REPO_DIR)}\n")
    
    # Change to repository root
    os.chdir(repo_root)
    
    # Create output directory
    os.makedirs(REPO_DIR, exist_ok=True)
    
    # Find all addons
    addons = []
    print("Scanning for addons...")
    
    for addon_dir in ADDON_DIRS:
        if os.path.isdir(addon_dir):
            addon_info = get_addon_info(addon_dir)
            if addon_info:
                print(f"  Found: {addon_info['id']} v{addon_info['version']}")
                addons.append(addon_info)
    
    if not addons:
        print("\nNo addons found!")
        return 1
    
    print(f"\nFound {len(addons)} addon(s)")
    
    # Generate addons.xml
    print("\nGenerating addons.xml...")
    addons_tree = generate_addons_xml(addons)
    addons_xml_path = os.path.join(REPO_DIR, 'addons.xml')
    
    with open(addons_xml_path, 'wb') as f:
        addons_tree.write(f, encoding='UTF-8', xml_declaration=True)
    
    print(f"Created addons.xml ({os.path.getsize(addons_xml_path)} bytes)")
    
    # Generate MD5 checksum
    print("\nGenerating MD5 checksum...")
    md5_value = generate_md5(addons_xml_path)
    md5_path = os.path.join(REPO_DIR, 'addons.xml.md5')
    
    with open(md5_path, 'w') as f:
        f.write(md5_value)
    
    print(f"Created addons.xml.md5: {md5_value}")
    
    # Create ZIP files for each addon
    print("\nCreating addon ZIP files...")
    for addon in addons:
        create_addon_zip(addon, REPO_DIR)
    
    print("\n" + "=" * 60)
    print("Repository generation complete!")
    print("=" * 60)
    print(f"\nGenerated files in {REPO_DIR}/:")
    print(f"  - addons.xml")
    print(f"  - addons.xml.md5")
    for addon in addons:
        print(f"  - {addon['id']}-{addon['version']}.zip")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
