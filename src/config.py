import os

# ── Telegram ──────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]   # e.g. @olx_resell_gdansk

# ── Scraper ───────────────────────────────────────────────────
# Comma-separated niche keys to run (default = all)
# Available: electronics, clothing, bikes, furniture, sport
ACTIVE_NICHES = os.getenv("ACTIVE_NICHES", "electronics,clothing,bikes,furniture,sport")

MAX_PAGES          = int(os.getenv("MAX_PAGES", "3"))        # pages per niche
REQUEST_TIMEOUT    = int(os.getenv("REQUEST_TIMEOUT", "15")) # seconds
DELAY_BETWEEN_PAGES = float(os.getenv("DELAY_BETWEEN_PAGES", "2"))  # seconds

# ── Telegram pacing ───────────────────────────────────────────
TELEGRAM_SLEEP_SECONDS = float(os.getenv("TELEGRAM_SLEEP_SECONDS", "0.8"))

# ── State ─────────────────────────────────────────────────────
STATE_FILE        = os.getenv("STATE_FILE", "data/sent_ids.json")
GITHUB_REPO       = os.getenv("GITHUB_REPOSITORY", "oriuma/olx-resell-monitor")
REMOTE_STATE_PATH = os.getenv("REMOTE_STATE_PATH", "data/sent_ids.json")
