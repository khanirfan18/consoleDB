import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import requests
from django.utils.text import slugify

BASE_DIR = Path(__file__).resolve().parent.parent
SEED_DIR = BASE_DIR / "seed_data"
IMG_DIR = SEED_DIR / "images"

HEADERS = {"User-Agent": "consoleDB-fetcher/3.0 (https://irfandev.me)"}
SPARQL_URL = "https://query.wikidata.org/sparql"

QUERY = """
SELECT DISTINCT ?consoleName ?type ?year ?manufName ?countryName ?website ?logo ?image WHERE {
  VALUES ?type {
    wd:Q17589470 wd:Q941818 wd:Q27931326 wd:Q8076 wd:Q17058694 wd:Q13402434 wd:Q12280247
  }
  ?console wdt:P31 ?type ;
           wdt:P18 ?image ;
           rdfs:label ?consoleName .
  FILTER(LANG(?consoleName) = "en")

  ?console (wdt:P176|wdt:P1716) ?manuf .
  ?manuf rdfs:label ?manufName .
  FILTER(LANG(?manufName) = "en")

  OPTIONAL { ?console wdt:P577 ?pubDate . }
  OPTIONAL { ?console wdt:P571 ?incDate . }
  BIND(COALESCE(YEAR(?pubDate), YEAR(?incDate), 2000) AS ?year)
  FILTER(?year >= 1972 && ?year <= 2026)

  OPTIONAL {
    ?manuf wdt:P17 ?country .
    ?country rdfs:label ?countryName .
    FILTER(LANG(?countryName) = "en")
  }
  OPTIONAL { ?manuf wdt:P856 ?website . }
  OPTIONAL { ?manuf wdt:P154 ?logo . }
}
LIMIT 300
"""

def download_file(url, dest_path):
    if dest_path.exists():
        return True
    try:
        sep = "&" if "?" in url else "?"
        resized_url = f"{url}{sep}width=600"
        r = requests.get(resized_url, headers=HEADERS, timeout=15)
        if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
            dest_path.write_bytes(r.content)
            return True
    except Exception:
        pass
    return False

def guess_generation(year):
    if year <= 1979: return 1
    if year <= 1982: return 2
    if year <= 1986: return 3
    if year <= 1992: return 4
    if year <= 1997: return 5
    if year <= 2004: return 6
    if year <= 2011: return 7
    if year <= 2019: return 8
    return 9

def save_json(manufacturers, consoles):
    """Helper to save the current state of dictionaries to console.json"""
    output = {
        "manufacturers": list(manufacturers.values()),
        "consoles": list(consoles.values()),
    }
    out_path = SEED_DIR / "console.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path

def main():
    (IMG_DIR / "manufacturers").mkdir(parents=True, exist_ok=True)
    (IMG_DIR / "consoles").mkdir(parents=True, exist_ok=True)

    print("Fetching premium video game consoles only...")
    res = requests.get(SPARQL_URL, params={"query": QUERY, "format": "json"}, headers=HEADERS, timeout=60)
    res.raise_for_status()
    rows = res.json()["results"]["bindings"]
    print(f"Success! {len(rows)} raw entries mili.\n")

    manufacturers = {}
    consoles = {}
    download_tasks = []

    # 1. BUILD THE TEXT DATABASE FIRST
    for row in rows:
        c_name = row["consoleName"]["value"].strip()
        m_name = row["manufName"]["value"].strip()

        if re.match(r"^Q\d+$", c_name) or re.match(r"^Q\d+$", m_name):
            continue

        m_slug = slugify(m_name)[:50]
        c_slug = slugify(c_name)[:50]
        if not m_slug or not c_slug:
            continue

        if m_slug not in manufacturers:
            manuf_obj = {
                "name": m_name[:50],
                "slug": m_slug,
                "country": row.get("countryName", {}).get("value", "Unknown")[:50],
                "website": row.get("website", {}).get("value", "")[:200],
                "description": f"{m_name} is a leading video game hardware manufacturer.",
                "founded_in": 1980,
                "logo_file": "", # Starts empty
            }
            manufacturers[m_slug] = manuf_obj

            if "logo" in row:
                logo_url = row["logo"]["value"]
                fname = f"{m_slug}.png"
                download_tasks.append(
                    (logo_url, IMG_DIR / "manufacturers" / fname, manuf_obj, "logo_file", f"manufacturers/{fname}")
                )

        if c_slug not in consoles:
            year = int(row["year"]["value"])
            type_uri = row["type"]["value"]
            
            if type_uri.endswith("Q941818"): c_type = "Handheld"
            elif type_uri.endswith("Q27931326"): c_type = "Hybrid Console"
            else: c_type = "Home Console"

            img_url = row["image"]["value"]
            fname = f"{c_slug}.jpg"
            console_obj = {
                "name": c_name[:50],
                "slug": c_slug,
                "manufacturer_slug": m_slug,
                "release_year": year,
                "console_type": c_type,
                "generation": guess_generation(year),
                "description": f"The {c_name} is a {c_type.lower()} released in {year} by {m_name}.",
                "is_active": year >= 2017,
                "image_file": "", # Starts empty
            }
            consoles[c_slug] = console_obj
            download_tasks.append(
                (img_url, IMG_DIR / "consoles" / fname, console_obj, "image_file", f"consoles/{fname}")
            )

    # 2. SAVE TEXT DATA IMMEDIATELY (Before any downloads start)
    out_path = save_json(manufacturers, consoles)
    print(f"✅ Text data saved immediately to {out_path} ({len(manufacturers)} manufacturers, {len(consoles)} consoles)")

    # 3. DOWNLOAD IMAGES IN BACKGROUND AND UPDATE JSON AS THEY FINISH
    print(f"Downloading {len(download_tasks)} images parallelly...")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(download_file, url, path): (target_dict, key, rel)
            for url, path, target_dict, key, rel in download_tasks
        }
        
        for future in as_completed(futures):
            target_dict, key, rel = futures[future]
            if future.result():
                # If download succeeds, attach the path to the dictionary
                target_dict[key] = rel

    # 4. FINAL SAVE (Now includes all the image paths)
    save_json(manufacturers, consoles)
    print("✅ Image paths attached! Fully complete.")

if __name__ == "__main__":
    main()