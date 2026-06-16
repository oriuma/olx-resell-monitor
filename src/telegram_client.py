"""
Telegram sender — adapted from oriuma/otmt telegram_client.py.
Supports sendPhoto with caption fallback to sendMessage.
"""

import logging
import time
import requests

from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_SLEEP_SECONDS
from src.formatter import build_caption

logger = logging.getLogger(__name__)
TG_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def send_message(text: str, parse_mode: str = "HTML") -> bool:
    try:
        resp = requests.post(
            f"{TG_API}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": False,
            },
            timeout=15,
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.error("[Telegram] sendMessage error: %s", e)
        return False


def send_photo(photo_url: str, caption: str, parse_mode: str = "HTML") -> bool:
    try:
        resp = requests.post(
            f"{TG_API}/sendPhoto",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "photo": photo_url,
                "caption": caption,
                "parse_mode": parse_mode,
            },
            timeout=15,
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.error("[Telegram] sendPhoto error: %s", e)
        return False


def send_listing(listing: dict) -> bool:
    """
    Send one OLX listing to Telegram channel.
    Tries photo first, falls back to text message.
    """
    caption   = build_caption(listing)
    photo_url = listing.get("image_url")

    success = False
    if photo_url:
        success = send_photo(photo_url, caption)
    if not success:
        success = send_message(caption)

    time.sleep(TELEGRAM_SLEEP_SECONDS)
    return success
