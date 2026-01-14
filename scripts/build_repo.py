import hashlib, os, xml.etree.ElementTree as ET, zipfile, json, sys
from pathlib import Path

ADDONS_SRC_DIR = Path("addons-src")
REPO_DIR = Path("repo")
ZIPS_DIR = REPO_DIR / "zips"
ADDONS_JSON = REPO_DIR / "addons.json"

def read_addon_xml(path: Path) -> bytes:
    with open(path, "rb") as f:
        return f.read()

def zip_addon(addon_dir: Path, addon_id: str, version: str) -> Path:
    dest_dir = ZIPS_DIR / addon_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dest_dir / f"{addon_id}-{version}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(addon_dir):
            for file in files:
                full = Path(root) / file
                rel = full.relative_to(addon_dir)
                z.write(full, rel)
    return zip_path

def collect_from_sources():
    addons = []
    for addon_dir in ADDONS_SRC_DIR.glob("*/"):
        addon_xml_path = addon_dir / "addon.xml"
        if not addon_xml_path.is_file():
            continue
        xml_bytes = read_addon_xml(addon_xml_path)
        addon_el = ET.fromstring(xml_bytes)
        addon_id = addon_el.get("id")
        version = addon_el.get("version")
        if not addon_id or not version:
            print(f"Skipping {addon_dir}: missing id/version", file=sys.stderr)
            continue
        zip_path = zip_addon(addon_dir, addon_id, version)
        addons.append((zip_path, xml_bytes))
    if not addons:
        print("No addons found in addons-src/", file=sys.stderr)
    return addons

def build_addons_xml(addons):
    root = ET.Element("addons")
    for _, xml_bytes in addons:
        addon_el = ET.fromstring(xml_bytes)
        root.append(addon_el)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)

def write_md5(path: Path):
    with open(path, "rb") as f:
        md5 = hashlib.md5(f.read()).hexdigest()
    with open(path.with_suffix(path.suffix + ".md5"), "w", encoding="utf-8") as f:
        f.write(md5)

def write_json_feed(addons):
    data = []
    for zip_path, xml_bytes in addons:
        addon_el = ET.fromstring(xml_bytes)
        data.append({
            "id": addon_el.get("id"),
            "name": addon_el.get("name"),
            "version": addon_el.get("version"),
            "provider": addon_el.get("provider-name"),
            "zip": str(zip_path.relative_to(REPO_DIR)).replace("\\", "/"),
            "summary": addon_el.findtext("./extension/summary") or "",
            "description": addon_el.findtext("./extension/description") or ""
        })
    ADDONS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(ADDONS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main():
    REPO_DIR.mkdir(exist_ok=True)
    addons = collect_from_sources()
    addons_xml = build_addons_xml(addons)
    addons_xml_path = REPO_DIR / "addons.xml"
    with open(addons_xml_path, "wb") as f:
        f.write(addons_xml)
    write_md5(addons_xml_path)
    write_json_feed(addons)
    print("Built repo artifacts in ./repo (addons.xml, addons.xml.md5, addons.json) and zips in ./repo/zips")

if __name__ == "__main__":
    main()