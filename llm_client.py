# llm_client.py

import os
from typing import List, Dict
from dotenv import load_dotenv

from openai import OpenAI

# Load environment variables
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# -----------------------------
# Configure OpenAI client
# -----------------------------
# Make sure you set:
# export OPENAI_API_KEY="your-key"
#
# Or on Windows PowerShell:
# setx OPENAI_API_KEY "your-key"
# llm_client.py

import os
from openai import OpenAI


# ---------------------------------------------------------
# Load API key from environment
# ---------------------------------------------------------
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError(
        "OPENAI_API_KEY environment variable not set. "
        "Set it before running the app."
    )

client = OpenAI(api_key=API_KEY)


# ---------------------------------------------------------
# Generic LLM call
# ---------------------------------------------------------
def call_llm(system_prompt: str, messages: list, model: str = "gpt-4.1") -> str:
    """
    Call the LLM with a system prompt + list of messages.
    messages = [ { "role": "user", "content": "..." }, ... ]
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system_prompt}, *messages],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"LLM error: {e}"


# ---------------------------------------------------------
# Optional: Convert natural language → SQL
# ---------------------------------------------------------
def generate_sql_from_question(question: str, medication: str | None) -> str:
    """
    Convert a natural-language question into a safe SQLite SELECT query.
    Always include the medication name if provided.
    """

    med_clause = ""
    if medication:
        med_clause = f"The medication name is '{medication}'. Always include a WHERE clause that filters medication using LIKE '%{medication.lower()}%'." 

    system_prompt = f"""
    You are a SQL generator. Convert the user's natural-language question
    into a safe SQLite SELECT query against a table named side_effects
    with columns:
        medication, side_effect, drug_manufacturer, drug_suspicion,Outcome.

    Rules:
    - ALWAYS use: SELECT * FROM side_effects
    - NEVER select individual columns.
    - Never modify, insert, update, or delete data.
    - Use LIKE for fuzzy matching.
    - If a medication name is provided, ALWAYS filter using:
        WHERE LOWER(medication) LIKE '%<medication>%'
    - Return only SQL, no explanation.

    {med_clause}
    """

    messages = [
        {"role": "user", "content": question}
    ]
    print ( " .................................")
    print ( question)

    sql = call_llm(system_prompt, messages)

    # Safety guard
    sql_clean = sql.strip().lower()
    if not sql_clean.startswith("select"):
        raise ValueError(f"Unsafe SQL generated: {sql}")
    print ( " ...........rpint sql ......................")
    print ( sql)
    return sql.strip()  

