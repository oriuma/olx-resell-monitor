"""
OLX scraper — adapted from mar0ls/olx-monitor.
Parses listing cards from OLX category pages.
"""

import logging
import re
import time
from typing import TypedDict

import requests
from bs4 import BeautifulSoup

from src.config import REQUEST_TIMEOUT, DELAY_BETWEEN_PAGES, MAX_PAGES

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pl-PL,pl;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


class Listing(TypedDict, total=False):
    id: str
    title: str
    price: int | None
    location: str
    date: str
    url: str
    image_url: str | None
    niche: str
    niche_label: str


# ── URL builder ───────────────────────────────────────────────

def build_url(niche: dict, page: int = 1) -> str:
    """
    Build OLX search URL for a given niche config and page number.

    Example output:
      https://www.olx.pl/elektronika/gdansk/
      ?search[filter_float_price:from]=50
      &search[filter_float_price:to]=800
      &page=2
    """
    url_path = niche["url_path"].strip("/")
    city     = niche.get("city") or ""

    if city:
        base = f"https://www.olx.pl/{url_path}/{city}/"
    else:
        base = f"https://www.olx.pl/{url_path}/"

    params = (
        f"?search%5Bfilter_float_price%3Afrom%5D={niche.get('price_min', 0)}"
        f"&search%5Bfilter_float_price%3Ato%5D={niche.get('price_max', 99999)}"
        f"&search%5Border%5D=created_at%3Adesc"  # newest first
    )
    if page > 1:
        params += f"&page={page}"
    return base + params


# ── HTTP helpers ──────────────────────────────────────────────

def fetch_page(url: str) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.HTTPError as e:
        logger.error("HTTP %s for %s", e.response.status_code if e.response else "?", url)
        return None
    except requests.RequestException as e:
        logger.error("Request failed %s: %s", url, e)
        return None


# ── Parsers ───────────────────────────────────────────────────

def extract_id(url: str) -> str:
    """Extract listing ID from OLX URL."""
    m = re.search(r"-(ID[A-Za-z0-9]+)\.html", url)
    if m:
        return m.group(1)
    # fallback: last segment
    return url.strip("/").split("/")[-1][-16:]


def parse_price(text: str) -> int | None:
    """Parse price string to integer PLN."""
    t = text.lower().replace("\xa0", " ")
    unit = re.search(r"(\d[\d\s]*)(?:z[łl]|pln|z?[łl]otych)", t)
    if unit:
        digits = re.sub(r"[^\d]", "", unit.group(1))
        return int(digits) if digits else None
    digits = re.sub(r"[^\d]", "", t)
    if digits:
        v = int(digits)
        return v if v <= 999_999 else None
    return None


def parse_listings(soup: BeautifulSoup, niche_key: str, niche_label: str) -> list[Listing]:
    """
    Parse listing cards from an OLX results page.
    Selector: div[data-cy="l-card"]
    """
    listings: list[Listing] = []
    cards = soup.find_all(attrs={"data-cy": "l-card"})

    for card in cards:
        try:
            # Link + ID
            link_tag = card.find("a", href=True)
            if not link_tag:
                continue
            url = link_tag["href"]
            if not url.startswith("http"):
                url = "https://www.olx.pl" + url
            ad_id = extract_id(url)

            # Skip promoted/sponsored duplicates that share same ID
            if any(lst["id"] == ad_id for lst in listings):
                continue

            # Title
            title_tag = card.find(["h4", "h6", "h3"])
            title = title_tag.get_text(strip=True) if title_tag else link_tag.get_text(strip=True)
            if not title:
                continue

            # Price
            price_tag = card.find(attrs={"data-testid": "ad-price"})
            price = None
            if price_tag:
                price = parse_price(price_tag.get_text(strip=True))
            if price is None:
                for s in card.strings:
                    if "zł" in s and re.search(r"\d", s):
                        price = parse_price(s)
                        break

            # Location + date
            loc_tag = card.find(attrs={"data-testid": "location-date"})
            location_text = loc_tag.get_text(strip=True) if loc_tag else ""
            parts = location_text.split(" - ", 1)
            location = parts[0].strip()
            date     = parts[1].strip() if len(parts) > 1 else ""

            # Image
            img_tag = card.find("img")
            image_url = None
            if img_tag:
                image_url = img_tag.get("src") or img_tag.get("data-src")

            listings.append({
                "id":          ad_id,
                "title":       title,
                "price":       price,
                "location":    location,
                "date":        date,
                "url":         url,
                "image_url":   image_url,
                "niche":       niche_key,
                "niche_label": niche_label,
            })

        except Exception as e:
            logger.debug("Skipped card: %s", e, exc_info=True)
            continue

    return listings


# ── Main scrape function ───────────────────────────────────────

def scrape_niche(niche_key: str, niche: dict) -> list[Listing]:
    """
    Scrape all pages for a single niche and return raw listings.
    """
    all_listings: list[Listing] = []
    label = niche.get("label", niche_key)

    for page in range(1, MAX_PAGES + 1):
        url = build_url(niche, page)
        logger.info("[%s] Fetching page %d: %s", label, page, url)

        soup = fetch_page(url)
        if soup is None:
            logger.warning("[%s] Page %d returned None, stopping.", label, page)
            break

        page_listings = parse_listings(soup, niche_key, label)
        if not page_listings:
            logger.info("[%s] No listings on page %d, stopping.", label, page)
            break

        all_listings.extend(page_listings)
        logger.info("[%s] Page %d → %d listings (total so far: %d)",
                    label, page, len(page_listings), len(all_listings))

        if page < MAX_PAGES:
            time.sleep(DELAY_BETWEEN_PAGES)

    return all_listings
