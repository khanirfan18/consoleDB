import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests
from django.utils.text import slugify

BASE_DIR = Path(__file__).resolve().parent.parent
SEED_DIR = BASE_DIR / "seed_data"
IMG_DIR = SEED_DIR / "images"

HEADERS = {"User-Agent": "consoleDB-fetcher/4.0 (https://irfandev.me)"}
SPARQL_URL = "https://query.wikidata.org/sparql"

# Purani broad query jisne successfully 250+ data laaya tha
QUERY = """
SELECT DISTINCT ?consoleLabel ?year ?manufLabel ?countryLabel ?website ?logo ?image WHERE {
  { ?console wdt:P31/wdt:P279* wd:Q8076. }
  UNION
  { ?console wdt:P31/wdt:P279* wd:Q17589470. }
  UNION
  { ?console wdt:P31/wdt:P279* wd:Q941818. }

  ?console wdt:P18 ?image.
  { ?console wdt:P176 ?manuf. } UNION { ?console wdt:P1716 ?manuf. }

  OPTIONAL { ?console wdt:P577 ?pubDate. }
  OPTIONAL { ?console wdt:P571 ?incDate. }
  BIND(COALESCE(YEAR(?pubDate), YEAR(?incDate), 2000) AS ?year)
  FILTER(?year >= 1972 && ?year <= 2026)

  OPTIONAL { ?manuf wdt:P17 ?country. }
  OPTIONAL { ?manuf wdt:P856 ?website. }
  OPTIONAL { ?manuf wdt:P154 ?logo. }

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 400
"""

def download_file(url, dest_path):
    if dest_path.exists():
        return True
    try:
        sep = "&" if "?" in url else "?"
        r = requests.get(f"{url}{sep}width=600", headers=HEADERS, timeout=15)
        if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
            dest_path.write_bytes(r.content)
            return True
    except:
        pass
    return False

def guess_generation(year):
    if year <= 1979: return 1
    elif year <= 1982: return 2
    elif year <= 1986: return 3
    elif year <= 1992: return 4
    elif year <= 1997: return 5
    elif year <= 2004: return 6
    elif year <= 2011: return 7
    elif year <= 2019: return 8
    return 9

def main():
    (IMG_DIR / "manufacturers").mkdir(parents=True, exist_ok=True)
    (IMG_DIR / "consoles").mkdir(parents=True, exist_ok=True)

    print("Fetching raw data from Wikidata...")
    res = requests.get(SPARQL_URL, params={"query": QUERY, "format": "json"}, headers=HEADERS, timeout=60)
    rows = res.json()["results"]["bindings"]
    
    manufacturers = {}
    consoles = {}
    download_tasks = []

    # BLOCKLIST: Yeh words agar console ke naam mein hue toh usko reject kar denge
    bad_words = ["calculator", "rocket", "missile", "watch", "arcade", "register", "synthesizer", "toy", "dictionary", "system"]

    for row in rows:
        c_name = row["consoleLabel"]["value"].strip()
        m_name = row["manufLabel"]["value"].strip()

        if re.match(r"^Q\d+$", c_name) or re.match(r"^Q\d+$", m_name):
            continue
            
        # PYTHON FILTERING: Kachra hatao!
        c_lower = c_name.lower()
        if any(bad in c_lower for bad in bad_words):
            continue

        m_slug = slugify(m_name)[:50]
        c_slug = slugify(c_name)[:50]
        if not m_slug or not c_slug:
            continue

        if m_slug not in manufacturers:
            manuf_obj = {
                "name": m_name[:50],
                "slug": m_slug,
                "country": row.get("countryLabel", {}).get("value", "Unknown")[:50],
                "website": row.get("website", {}).get("value", "")[:200],
                "description": f"{m_name} is a gaming hardware manufacturer.",
                "founded_in": 1980,
                "logo_file": "",
            }
            manufacturers[m_slug] = manuf_obj
            if "logo" in row:
                fname = f"{m_slug}.png"
                download_tasks.append((row["logo"]["value"], IMG_DIR / "manufacturers" / fname, manuf_obj, "logo_file", f"manufacturers/{fname}"))

        if c_slug not in consoles:
            year = int(row["year"]["value"])
            fname = f"{c_slug}.jpg"
            console_obj = {
                "name": c_name[:50],
                "slug": c_slug,
                "manufacturer_slug": m_slug,
                "release_year": year,
                "console_type": "Home Console" if year < 1990 else "Handheld",
                "generation": guess_generation(year),
                "description": f"The {c_name} was released in {year} by {m_name}.",
                "is_active": year >= 2017,
                "image_file": "",
            }
            consoles[c_slug] = console_obj
            download_tasks.append((row["image"]["value"], IMG_DIR / "consoles" / fname, console_obj, "image_file", f"consoles/{fname}"))

    # File save karo (Images se pehle)
    out_path = SEED_DIR / "console.json"
    
    print(f"Filtered! Clean data mila: {len(manufacturers)} manufacturers aur {len(consoles)} consoles.")
    print(f"Ab inki {len(download_tasks)} images parallel download ho rahi hain (wait 15-20s)...")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [(executor.submit(download_file, u, p), obj, key, rel) for u, p, obj, key, rel in download_tasks]
        for fut, obj, key, rel in futures:
            if fut.result(): obj[key] = rel

    out_path.write_text(json.dumps({"manufacturers": list(manufacturers.values()), "consoles": list(consoles.values())}, indent=2), encoding="utf-8")
    print(f"✅ BINGO! Sab save ho gaya: {out_path}")

if __name__ == "__main__":
    main()
