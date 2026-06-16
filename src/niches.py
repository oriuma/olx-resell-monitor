"""
Niche definitions for OLX resell monitor.
Each niche maps to an OLX category URL slug and optional filters.

структура одного ниша:
  url_path  — часть URL после olx.pl/  (категория)
  label     — читаемое название для логов
  price_min — минимальная цена PLN (0 = без фильтра)
  price_max — максимальная цена PLN
  city      — город (slug OLX, напр. "gdansk", "warszawa")
              None = вся Польша

Чтобы добавить новую нишу — просто добавь запись в NICHES.
"""

NICHES: dict[str, dict] = {
    "electronics": {
        "label": "Elektronika",
        "url_path": "elektronika",
        "price_min": 50,
        "price_max": 800,
        "city": "gdansk",
    },
    "clothing": {
        "label": "Odzież",
        "url_path": "moda",
        "price_min": 10,
        "price_max": 200,
        "city": "gdansk",
    },
    "bikes": {
        "label": "Rowery",
        "url_path": "sport-hobby/rowery",
        "price_min": 100,
        "price_max": 1500,
        "city": "gdansk",
    },
    "furniture": {
        "label": "Meble",
        "url_path": "dom-i-ogrod/meble",
        "price_min": 30,
        "price_max": 600,
        "city": "gdansk",
    },
    "sport": {
        "label": "Sport & Hobby",
        "url_path": "sport-hobby",
        "price_min": 20,
        "price_max": 500,
        "city": "gdansk",
    },
}
