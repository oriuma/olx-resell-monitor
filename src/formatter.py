"""
Telegram message formatter for OLX resell listings.
Adapted from oriuma/otmt formatter.py.
"""

NICHE_EMOJI: dict[str, str] = {
    "electronics": "📱",
    "clothing":    "👗",
    "bikes":       "🚲",
    "furniture":   "🛋",
    "sport":       "🏋",
}


def build_caption(listing: dict) -> str:
    """
    Build HTML-formatted Telegram caption for one OLX listing.

    Expected listing keys:
        title, price, location, date, url, niche, niche_label
    """
    title       = listing.get("title", "Brak tytułu")
    price       = listing.get("price")
    location    = listing.get("location", "?")
    date        = listing.get("date", "")
    url         = listing.get("url", "")
    niche       = listing.get("niche", "")
    niche_label = listing.get("niche_label", niche)

    emoji = NICHE_EMOJI.get(niche, "🔖")
    price_str = f"{price:,} zł".replace(",", " ") if price else "brak ceny"

    lines = [
        f"{emoji} <b>{title}</b>",
        f"💰 <b>{price_str}</b>",
        f"📍 {location}",
    ]
    if date:
        lines.append(f"🗓 {date}")
    lines.append(f"🏷 #{niche_label.replace(' ', '_').replace('&', 'i')}")
    if url:
        lines.append(f'🔗 <a href="{url}">OLX →</a>')

    return "\n".join(lines)
