# agent.py

import sqlite3
import pandas as pd
from typing import List, Dict, Tuple

from llm_client import call_llm, generate_sql_from_question


# ---------------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------------
SYSTEM_PROMPT = """
You are a medical side‑effects assistant.

Your job:
- Summarize side‑effect information from structured SQLite based FDA data and scraped web documents.
- Annotate each side effect with its source(s) using the SOURCE MAP.
- Never invent side effects or sources.
- If information is missing, say so.
- Keep explanations clear and patient‑friendly.

Format example:
- nausea (FDA Data from SQLite)
- dizziness (drugs.com)
- rash (fda.gov, mayoclinic.org)
"""


# ---------------------------------------------------------
# Build source map: side_effect → [sources]
# ---------------------------------------------------------
def build_source_map(csv_rows: pd.DataFrame, docs: List[Dict]) -> Dict[str, List[str]]:
    source_map = {}

    # SQLite rows
    for _, row in csv_rows.iterrows():
        se = row["side_effect"].strip().lower()
        source_map.setdefault(se, []).append("FDA Data from SQLite")

    # Scraped docs
    for d in docs:
        url = d.get("url", "")
        domain = url.split("/")[2] if "://" in url else url
        for se in d.get("side_effects", []):
            se_norm = se.strip().lower()
            source_map.setdefault(se_norm, []).append(domain)

    return source_map


# ---------------------------------------------------------
# Build LLM context
# ---------------------------------------------------------
def build_context(
    csv_rows: pd.DataFrame,
    docs: List[Dict],
    source_map: Dict[str, List[str]]
) -> str:

    parts = []

    # ---- SOURCE MAP ----
    parts.append("SOURCE MAP:")
    for se, sources in source_map.items():
        parts.append(f"- {se}: {', '.join(sources)}")

    # ---- STRUCTURED DATA ----
    parts.append("\nSTRUCTURED DATA (FDA Data from SQLite):")

    if csv_rows.empty:
        parts.append("No structured data found for this medication.")
    else:
        for _, row in csv_rows.iterrows():
            # Add all columns dynamically
            cols = []
            for col in row.index:
                val = row[col]
                if pd.notna(val) and str(val).strip():
                    cols.append(f"{col}: {val}")

            parts.append("- " + " | ".join(cols))


    # ---- SCRAPED DOCUMENTS ----
    parts.append("\nSCRAPED WEB DOCUMENTS:")
    if not docs:
        parts.append("No scraped documents available.")
    else:
        for d in docs:
            url = d.get("url", "")
            se_list = d.get("side_effects", [])
            excerpt = (d.get("text") or "")[:600].replace("\n", " ")

            parts.append(f"\nSource: {url}")
            if se_list:
                parts.append("Extracted side effects: " + ", ".join(se_list))
            parts.append("Excerpt: " + excerpt)

    return "\n".join(parts)


# ---------------------------------------------------------
# Main agent entry point
# ---------------------------------------------------------
def answer_question(
    df: pd.DataFrame,
    docs: List[Dict],
    question: str,
    med_filter: str | None = None
) -> Tuple[str, pd.DataFrame, List[Dict]]:
    """
    Returns:
        answer_text: str
        csv_rows_subset: pd.DataFrame
        docs_used_subset: list[dict]
    """

    # -----------------------------------------------------
    # 1. Try LLM‑generated SQL first
    # -----------------------------------------------------
    df_sql = pd.DataFrame()

    try:
        sql = generate_sql_from_question(question, med_filter)
        conn = sqlite3.connect("DrugData/CapstoneRJ.db")
        sql = sql 

        df_sql1 = pd.read_sql_query(sql, conn)
        df_sql = df_sql1.head(200)

        # print ( " .......................")
        # print ( df_sql)   
        conn.close()
    except Exception as e:
        # SQL failed — fallback to keyword filtering
        df_sql = pd.DataFrame() 

    # -----------------------------------------------------
    # 2. Fallback: keyword + medication filtering
    # -----------------------------------------------------
    if df_sql.empty:
        if med_filter:
            df_filtered = df[df["medication"].str.contains(med_filter, case=False, na=False)]
        else:
            df_filtered = df

        # Keyword match inside side_effect or notes
        q = question.lower()
        mask = (
            df_filtered["side_effect"].str.lower().str.contains(q) |
            df_filtered.get("outcome", pd.Series([""] * len(df_filtered))).str.lower().str.contains(q)
        )
        df_final = df_filtered[mask].head(1000)
    else:
        df_final = df_sql

    # -----------------------------------------------------
    # 3. Scraped docs already filtered by app.py
    # -----------------------------------------------------
    doc_hits = docs

    # -----------------------------------------------------
    # 4. Build source map
    # -----------------------------------------------------
    source_map = build_source_map(df_final, doc_hits)

    # -----------------------------------------------------
    # 5. Build LLM context
    # -----------------------------------------------------
    
    # print ( " .......................")
    # print ( df_final)

    # print ( " .......................")
    # print ( doc_hits)

    # print ( " .......................")
    # print ( source_map)

    context = build_context(df_final, doc_hits, source_map)

    messages = [
        {
            "role": "user",
            "content": f"Question: {question}\n\nContext:\n{context}"
        }
    ]

    # -----------------------------------------------------
    # 6. Call LLM
    # -----------------------------------------------------
    answer = call_llm(
        system_prompt=SYSTEM_PROMPT,
        messages=messages,
    )

    # -----------------------------------------------------
    # 7. Return everything to app.py
    # -----------------------------------------------------
    print ( " ......===========.................")
    print ( messages)
    print ( " ......===========.................")
    print ( answer)

    return answer, df_final, doc_hits
