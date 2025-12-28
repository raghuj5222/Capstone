# extractor.py

import re
from urllib.parse import urlparse
from typing import List

from bs4 import BeautifulSoup

from domain_extractors import (
    extract_fda,
    extract_mayo,
    extract_drugs_com,
    extract_medlineplus,
)


def extract_general(html: str) -> List[str]:
    """
    General-purpose extractor for side effects when no domain-specific
    rules are defined. Uses headings + regex heuristics.
    """
    soup = BeautifulSoup(html, "html.parser")
    results = set()

    for h in soup.find_all(["h1", "h2", "h3", "h4"]):
        text = h.get_text(" ", strip=True).lower()
        if "side effects" in text or "adverse reactions" in text or "side-effects" in text:
            sib = h.find_next_sibling()
            while sib and sib.name in ["p", "ul", "ol"]:
                if sib.name in ["ul", "ol"]:
                    for li in sib.find_all("li"):
                        results.add(li.get_text(" ", strip=True))
                elif sib.name == "p":
                    paragraph = sib.get_text(" ", strip=True)
                    results.update(_extract_short_phrases(paragraph))
                sib = sib.find_next_sibling()

    patterns = [
        r"common side effects include[:\-]?\s*(.*?)(?:\.|\n)",
        r"side effects may include[:\-]?\s*(.*?)(?:\.|\n)",
        r"may cause[:\-]?\s*(.*?)(?:\.|\n)",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, html, flags=re.IGNORECASE | re.DOTALL)
        for m in matches:
            for item in re.split(r"[;,]", m):
                cleaned = item.strip()
                if cleaned:
                    results.add(cleaned)

    return sorted(results)


def _extract_short_phrases(text: str) -> List[str]:
    items: List[str] = []
    for part in re.split(r"[;,]", text):
        part = part.strip()
        if 0 < len(part.split()) <= 6:
            items.append(part)
    return items


def extract_side_effects(url: str, html: str) -> List[str]:
    """
    Domain router: chooses the best extractor for the URL.
    Falls back to general extraction if no domain match.
    """
    domain = urlparse(url).netloc.lower()

    if "fda.gov" in domain:
        return extract_fda(html)

    if "mayoclinic.org" in domain:
        return extract_mayo(html)

    if "drugs.com" in domain:
        return extract_drugs_com(html)

    if "medlineplus.gov" in domain:
        return extract_medlineplus(html)

    return extract_general(html)
