#!/usr/bin/env python3
"""
OLX Resell Monitor — entry point.

Flow:
  1. Load seen listing IDs from GitHub (or local fallback)
  2. For each active niche: scrape pages, find new listings
  3. Send new listings to Telegram channel
  4. Save updated state back to GitHub

Usage:
  python main.py

Environment variables (set as GitHub Actions secrets):
  TELEGRAM_BOT_TOKEN   — bot token from @BotFather
  TELEGRAM_CHAT_ID     — channel username or numeric ID
  GITHUB_TOKEN         — auto-provided by Actions (read/write contents)
  GITHUB_REPOSITORY    — auto-provided by Actions (e.g. oriuma/olx-resell-monitor)
  ACTIVE_NICHES        — comma-separated subset, e.g. "electronics,bikes"
  MAX_PAGES            — pages to scrape per niche (default 3)
"""

import logging
import sys

from src.config import (
    ACTIVE_NICHES,
    STATE_FILE,
    GITHUB_REPO,
    REMOTE_STATE_PATH,
)
from src.niches import NICHES
from src.scraper import scrape_niche
from src.state import load_sent_ids, save_sent_ids, push_state_to_github
from src.telegram_client import send_listing

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("main")


def run() -> None:
    # 1. Parse active niches
    requested = [k.strip() for k in ACTIVE_NICHES.split(",") if k.strip()]
    active    = {k: NICHES[k] for k in requested if k in NICHES}
    if not active:
        logger.error("No valid niches in ACTIVE_NICHES=%r. Choices: %s",
                     ACTIVE_NICHES, ", ".join(NICHES))
        sys.exit(1)
    logger.info("Active niches: %s", ", ".join(active))

    # 2. Load state
    sent_ids = load_sent_ids(STATE_FILE, GITHUB_REPO, REMOTE_STATE_PATH)
    new_count = 0

    # 3. Scrape and send
    for niche_key, niche_cfg in active.items():
        listings = scrape_niche(niche_key, niche_cfg)
        logger.info("[%s] Total scraped: %d", niche_cfg['label'], len(listings))

        for listing in listings:
            lid = listing["id"]
            if lid in sent_ids:
                continue
            ok = send_listing(listing)
            if ok:
                sent_ids.add(lid)
                new_count += 1
                logger.info("  ✓ sent [%s] %s", niche_key, listing.get("title", "")[:60])
            else:
                logger.warning("  ✗ failed to send %s", lid)

    logger.info("Done. New listings sent: %d", new_count)

    # 4. Persist state
    save_sent_ids(STATE_FILE, sent_ids)
    push_state_to_github(STATE_FILE, GITHUB_REPO, REMOTE_STATE_PATH)


if __name__ == "__main__":
    run()
