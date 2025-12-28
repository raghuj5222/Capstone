# scraper.py

import requests


def fetch_html(url: str) -> str:
    """
    Fetch raw HTML from a URL.
    You may want to integrate robots.txt checks separately if needed.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MedSideEffectsBot/1.0)"
    }

    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.text
