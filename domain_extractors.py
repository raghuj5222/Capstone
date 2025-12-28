# domain_extractors.py

from typing import List
from bs4 import BeautifulSoup


def extract_fda(html: str) -> List[str]:
    """
    FDA drug label pages:
    - 'Adverse Reactions' sections with lists/paragraphs.
    """
    soup = BeautifulSoup(html, "html.parser")
    results = set()

    for h in soup.find_all(["h2", "h3"]):
        if "adverse reactions" in h.get_text(" ", strip=True).lower():
            sib = h.find_next_sibling()
            while sib and sib.name in ["p", "ul", "ol"]:
                if sib.name in ["ul", "ol"]:
                    for li in sib.find_all("li"):
                        results.add(li.get_text(" ", strip=True))
                elif sib.name == "p":
                    results.add(sib.get_text(" ", strip=True))
                sib = sib.find_next_sibling()

    return sorted(results)


def extract_mayo(html: str) -> List[str]:
    """
    Mayo Clinic:
    - 'Side effects' sections with lists under nearby divs.
    """
    soup = BeautifulSoup(html, "html.parser")
    results = set()

    for h in soup.find_all("h2"):
        if "side effects" in h.get_text(" ", strip=True).lower():
            container = h.find_next("div")
            if container:
                for li in container.find_all("li"):
                    results.add(li.get_text(" ", strip=True))

    return sorted(results)


def extract_drugs_com(html: str) -> List[str]:
    """
    Drugs.com:
    - 'Side Effects' section with lists (often class-based).
    """
    soup = BeautifulSoup(html, "html.parser")
    results = set()

    for h in soup.find_all("h2"):
        if "side effects" in h.get_text(" ", strip=True).lower():
            for ul in h.find_all_next("ul"):
                for li in ul.find_all("li"):
                    results.add(li.get_text(" ", strip=True))
                break

    return sorted(results)


def extract_medlineplus(html: str) -> List[str]:
    """
    MedlinePlus:
    - 'Side Effects' sections inside 'section-body' divs.
    """
    soup = BeautifulSoup(html, "html.parser")
    results = set()

    for h in soup.find_all("h2"):
        if "side effects" in h.get_text(" ", strip=True).lower():
            section = h.find_next("div", class_="section-body")
            if section:
                for li in section.find_all("li"):
                    results.add(li.get_text(" ", strip=True))

    return sorted(results)
