# retrieval.py

from typing import List, Dict, Tuple
import pandas as pd


def filter_df_by_medication(
    df: pd.DataFrame,
    med_filter: str | None = None
) -> pd.DataFrame:
    """
    Optionally filter the SQLite side_effects DataFrame by medication name.
    """
    if not med_filter:
        return df

    med_filter = med_filter.strip().lower()
    if not med_filter:
        return df

    mask = df["medication"].str.contains(med_filter, case=False, na=False)
    return df[mask]


def search_side_effects_in_df(
    df: pd.DataFrame,
    query: str,
    top_k: int = 50
) -> pd.DataFrame:
    """
    Very simple keyword search over 'side_effect' and 'notes' columns.
    Returns a subset of df with rows that match query terms.
    """
    if df.empty:
        return df

    q = query.lower().strip()
    if not q:
        return df.head(top_k)

    cols_to_search = ["side_effect", "notes"]
    mask = False

    for col in cols_to_search:
        if col in df.columns:
            mask = mask | df[col].astype(str).str.lower().str.contains(q, na=False)

    hits = df[mask]
    if hits.empty:
        return df.head(top_k)

    return hits.head(top_k)


def search_docs(
    docs: List[Dict],
    query: str,
    top_k: int = 5
) -> List[Dict]:
    """
    Simple keyword search over scraped web documents.
    Scores docs based on query term frequency in 'text' and 'side_effects'.
    """
    if not docs:
        return []

    q = query.lower().strip()
    if not q:
        return docs[:top_k]

    def score_doc(doc: Dict) -> int:
        text = (doc.get("text") or "").lower()
        se_list = [s.lower() for s in doc.get("side_effects", [])]

        score = text.count(q)
        for se in se_list:
            if q in se:
                score += 2
        return score

    scored = [(score_doc(d), d) for d in docs]
    scored = [pair for pair in scored if pair[0] > 0]

    if not scored:
        return docs[:top_k]

    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:top_k]]
