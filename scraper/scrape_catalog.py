

import requests
from bs4 import BeautifulSoup
import json
import time
import os

BASE_URL = "https://www.shl.com"

# Individual Test Solutions catalog URL (type=1 filter)
CATALOG_URL = (
    "https://www.shl.com/solutions/products/product-catalog/"
    "?start={start}&type=1&type=1"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def scrape_catalog_page(start: int) -> list[dict]:
    """Ek page se saare assessments nikalta hai."""
    url = CATALOG_URL.format(start=start)
    print(f"  Fetching: {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ERROR fetching page at start={start}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    # SHL catalog table rows
    rows = soup.select("table.custom-table tbody tr")
    if not rows:
        # Try alternate selector
        rows = soup.select("tr[data-entity-id]")

    items = []
    for row in rows:
        # Name + URL
        link_tag = row.select_one("td a")
        if not link_tag:
            continue

        name = link_tag.get_text(strip=True)
        href = link_tag.get("href", "")
        url_full = BASE_URL + href if href.startswith("/") else href

        # Test types (A=Ability, P=Personality, B=Biodata, S=Situational, K=Knowledge/Skills)
        type_tags = row.select("td span.badge, td .product-catalogue__key")
        test_types = [t.get_text(strip=True) for t in type_tags if t.get_text(strip=True)]

        # Remote / adaptive flags (icons in columns)
        cols = row.select("td")
        remote_testing = False
        adaptive_irt = False
        if len(cols) >= 3:
            # Column 2 = Remote Testing, Column 3 = Adaptive/IRT (check for checkmark)
            remote_testing = bool(cols[1].select_one("svg, img, span.yes, .checkmark"))
            adaptive_irt = bool(cols[2].select_one("svg, img, span.yes, .checkmark"))

        if name:
            items.append({
                "name": name,
                "url": url_full,
                "test_type": ", ".join(test_types) if test_types else "Unknown",
                "remote_testing": remote_testing,
                "adaptive_irt": adaptive_irt,
                "description": "",   
                "job_levels": [],
                "languages": [],
            })

    return items


def scrape_detail_page(item: dict) -> dict:
    """
    Ek assessment ki detail page se description, job_levels, languages fill karta hai.
    """
    if not item["url"] or "shl.com" not in item["url"]:
        return item

    try:
        resp = requests.get(item["url"], headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"    ERROR detail page {item['url']}: {e}")
        return item

    soup = BeautifulSoup(resp.text, "html.parser")

    # Description — usually first paragraph in main content
    desc_tag = soup.select_one(".product-catalogue-detail__description p, .product-hero__description, main p")
    if desc_tag:
        item["description"] = desc_tag.get_text(separator=" ", strip=True)

    # Job levels
    level_section = soup.find(string=lambda t: t and "job level" in t.lower())
    if level_section:
        parent = level_section.find_parent()
        if parent:
            sibling = parent.find_next_sibling()
            if sibling:
                item["job_levels"] = [s.strip() for s in sibling.get_text(",").split(",") if s.strip()]

    # Languages
    lang_section = soup.find(string=lambda t: t and "language" in t.lower())
    if lang_section:
        parent = lang_section.find_parent()
        if parent:
            sibling = parent.find_next_sibling()
            if sibling:
                item["languages"] = [s.strip() for s in sibling.get_text(",").split(",") if s.strip()]

    return item


def scrape_all(max_pages: int = 20) -> list[dict]:
    """Saare pages scrape karta hai (12 items per page)."""
    all_items = []
    seen_names = set()

    for page_num in range(max_pages):
        start = page_num * 12
        print(f"\nPage {page_num + 1} (start={start})...")
        items = scrape_catalog_page(start)

        if not items:
            print(f"  No items found — stopping at page {page_num + 1}.")
            break

        new_items = []
        for item in items:
            if item["name"] not in seen_names:
                seen_names.add(item["name"])
                new_items.append(item)

        if not new_items:
            print("  All items already seen — catalog exhausted.")
            break

        # Detail pages scrape 
        print(f"  Scraping {len(new_items)} detail pages...")
        for i, item in enumerate(new_items):
            print(f"    [{i+1}/{len(new_items)}] {item['name']}")
            item = scrape_detail_page(item)
            time.sleep(0.5)   # polite crawling

        all_items.extend(new_items)
        time.sleep(1)

    return all_items


def save_catalog(items: list[dict], path: str = "data/shl_catalog.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(items)} items to {path}")


if __name__ == "__main__":
    print("=== SHL Catalog Scraper ===")
    print("Scraping Individual Test Solutions...\n")
    catalog = scrape_all(max_pages=25)

    if not catalog:
        print("\nWARNING: Scraper ne kuch nahi nikala!")
        print("SHL ne block kiya hoga. Fallback catalog use karein.")
        print("scraper/fallback_catalog.py run karein.\n")
    else:
        save_catalog(catalog)
        print(f"\nDone! {len(catalog)} assessments scraped.")
