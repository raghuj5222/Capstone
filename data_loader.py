# data_loader.py

import sqlite3
import pandas as pd
from typing import List, Dict

from scraper import fetch_html
from extractor import extract_side_effects


# ---------------------------------------------------------
# Load SQLite table
# ---------------------------------------------------------
def load_sqlite_side_effects(
    db_path: str,
    table_name: str = "side_effects"
) -> pd.DataFrame:
    """
    Load medication side‑effect data from a SQLite database table.
    Expected columns:
        medication, side_effect, severity, frequency, notes
    """

    try:
        conn = sqlite3.connect(db_path)
    except Exception as e:
        raise RuntimeError(f"Failed to connect to SQLite database: {e}")

    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name} where 1=2 ", conn)
    except Exception as e:
        raise RuntimeError(f"Failed to load table '{table_name}': {e}")
    finally:
        conn.close()

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    # Required columns
    required = {"medication", "side_effect"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing required columns in SQLite table: {missing}. "
            "Ensure your table contains at least 'medication' and 'side_effect'."
        )

    # Clean values
    df["medication"] = df["medication"].astype(str).str.strip().str.lower()
    df["side_effect"] = df["side_effect"].astype(str).str.strip()

    for col in ["drug_manufacturer", "drug_suspicion", "outcome"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df = df.dropna(subset=["medication", "side_effect"])

    return df


# ---------------------------------------------------------
# Scrape URLs dynamically
# ---------------------------------------------------------
def load_scraped_side_effects(urls: List[str]) -> List[Dict]:
    """
    Fetch and extract side effect info from a list of URLs.
    Returns a list of documents:
        {
          "url": str,
          "text": str,
          "side_effects": list[str],
          "error": str | None
        }
    """

    docs: List[Dict] = []

    for url in urls:
        try:
            html = fetch_html(url)
        except Exception as e:
            docs.append({
                "url": url,
                "text": "",
                "side_effects": [],
                "error": str(e),
            })
            continue

        # Extract side effects using domain-specific rules
        side_effects = extract_side_effects(url, html)

        # Clean text for context (limit size)
        clean_text = html.replace("\r", " ").replace("\n", " ")
        if len(clean_text) > 4000:
            clean_text = clean_text[:4000]

        docs.append({
            "url": url,
            "text": clean_text,
            "side_effects": side_effects,
            "error": None,
        })

    return docs
