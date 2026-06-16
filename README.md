# OLX Resell Monitor 🛒

Automatically scrapes OLX.pl for resell deals across 5 niches and posts new listings to a Telegram channel. Runs every 30 minutes via GitHub Actions — no server needed.

## Niches

| Key | Category | Default price range |
|---|---|---|
| `electronics` | Elektronika | 50–800 zł |
| `clothing` | Odzież / Moda | 10–200 zł |
| `bikes` | Rowery | 100–1500 zł |
| `furniture` | Meble | 30–600 zł |
| `sport` | Sport & Hobby | 20–500 zł |

## Setup

### 1. Add GitHub Secrets

Go to **Settings → Secrets and variables → Actions → New repository secret**:

| Secret name | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Token from @BotFather (e.g. `123456:ABC-DEF...`) |
| `TELEGRAM_CHAT_ID` | Channel username or numeric ID (e.g. `@my_channel` or `-1001234567890`) |

> `GITHUB_TOKEN` is automatically provided by Actions — no need to add it.

### 2. Enable GitHub Actions

Go to the **Actions** tab and enable workflows if prompted.

### 3. Adjust niches / price ranges

Edit `src/niches.py` to change cities, price ranges, or add new categories.

### 4. Run manually to test

Actions tab → **OLX Resell Monitor** → **Run workflow**

## Project Structure

```
main.py                  — entry point
src/
  config.py              — env vars
  niches.py              — niche definitions (edit this)
  scraper.py             — OLX HTML scraper
  formatter.py           — Telegram caption builder
  telegram_client.py     — Telegram Bot API sender
  state.py               — seen-IDs persistence (local + GitHub)
data/
  sent_ids.json          — auto-generated, tracks sent listings
.github/workflows/
  monitor.yml            — cron schedule (every 30 min)
```
