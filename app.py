# app.py

import streamlit as st
import pandas as pd

from data_loader import load_sqlite_side_effects, load_scraped_side_effects
from agent import answer_question


# ---------------------------------------------------------
# Streamlit page config
# ---------------------------------------------------------
st.set_page_config(
    page_title="Medication Side Effects Explorer - This is a LLM based medical question‑answering assistant",
    page_icon="💊",
    layout="wide",
)


# ---------------------------------------------------------
# Load SQLite ONLY (no scraping yet)
# ---------------------------------------------------------
@st.cache_data(show_spinner=True)
def init_sqlite():
    db_path = "Drugdata/CapstoneRJ.db"
    df = load_sqlite_side_effects(db_path)
    return df


df = init_sqlite()


# ---------------------------------------------------------
# Helper: Build URLs dynamically from medication name
# ---------------------------------------------------------
def build_medication_urls(med_name: str):
    """
    Convert a medication name into URL slugs for scraping.
    """
    med_slug = med_name.lower().replace(" ", "-")

    urls = [
        f"https://www.drugs.com/sfx/{med_slug}-side-effects.html",
        f"https://www.mayoclinic.org/drugs-supplements/{med_slug}/side-effects",
        f"https://medlineplus.gov/druginfo/meds/{med_slug}.html",
    ]

    return urls


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
st.sidebar.title("Medication Side Effects Explorer")

med_filter = st.sidebar.text_input(
    "Medication name (required)",
    placeholder="e.g., ondansetron",
)


# ---------------------------------------------------------
# Main UI
# ---------------------------------------------------------
st.title("💊 Medication Side Effects Explorer")

question = st.text_input(
    "Your question",
    placeholder="e.g., What are the common side effects of ondansetron?",
)

ask_button = st.button("Ask", type="primary")


# ---------------------------------------------------------
# Handle user query
# ---------------------------------------------------------
if ask_button:

    if not med_filter.strip():
        st.error("Please enter a medication name in the sidebar before asking a question.")
        st.stop()

    med_name = med_filter.strip()

    # ---- 1. Query SQLite for this medication only ----
    df_filtered = df[df["medication"].str.contains(med_name, case=False, na=False)]

    # ---- 2. Scrape URLs dynamically for this medication ----
    with st.spinner(f"Scraping data for {med_name}..."):
        urls = build_medication_urls(med_name)
        docs = load_scraped_side_effects(urls)

    # ---- 3. Ask the agent ----
    with st.spinner("Thinking..."):
        answer, csv_rows, docs_used = answer_question(
            df=df_filtered,
            docs=docs,
            question=question,
            med_filter=med_name,
        )

    # ---- 4. Display answer ----
    ##st.subheader("Answer")
    #st.write(answer)

    # ---- 4. Display results in tabs ----
    tab1, tab2, tab3 = st.tabs([ "Answer", "FDA Data", "Web Sources"])

    # -------------------------
    # TAB 1 — LLM Answer
    # -------------------------
    with tab1:
        st.subheader("LLM Answer Sideeffects")
        st.write(answer)

    # -------------------------
    # TAB 2 — FDA  Data from SQLite
    # -------------------------
    with tab2:
        st.subheader("Supporting FDA Data from SQLite ")
        if not csv_rows.empty:
            st.dataframe(csv_rows.reset_index(drop=True))

            col2, col3 = st.columns(2)
        
            with col2:
                st.subheader( "meaning of Outcome column in fda data ")

                str = """ 
                DE Death \n 
                LT Life-Threatening \n
                HO Hospitalization - Initial or Prolonged \n
                DS Disability \n
                CA Congenital Anomaly \n
                RI Required Intervention to Prevent Permanent \n
                Impairment/Damage n
                OT Other Serious (Important Medical Event) n
            """
            st.write(str)

            with col3:
                st.subheader( "meaning of Drug Suspect")

                str = """                  
                    PS Primary Suspect Drug \n
                    SS Secondary Suspect Drug \n
                    C Concomitant \n
                    I Interacting \n
                    DN       Drug Not Administered \n
                """
                st.write(str)           
        else:
            st.write("No matching rows found in fda database (sqlite).")
    
   
    # -------------------------
    # TAB 3 — Side Effects from Web Sources
    # -------------------------
    with tab3:
        st.subheader("Side Effects from Web Sources")
        if not docs_used:
            st.write("No scraped documents available.")
        else:
            for d in docs_used:
                st.markdown(f"**URL:** {d.get('url')}")
                if d.get("side_effects"):
                    st.markdown("**Extracted side effects:** " + ", ".join(d["side_effects"]))
                excerpt = (d.get("text") or "")[:500]
            if excerpt:
                st.markdown("**Excerpt:**")
                st.write(excerpt + "...")
            st.markdown("---")


    # ---- 5. Sources toggle ----
    show_sources = st.toggle("Show sources")

    if show_sources:
        st.subheader("FDA Results from SQLLite database")
        if not csv_rows.empty:
            st.dataframe(csv_rows)
        else:
            st.write("No matching rows in SQLite.")

        st.subheader("Scraped Web Sources")
        for d in docs_used:
            st.markdown(f"**URL:** {d.get('url')}")

            if d.get("side_effects"):
                st.markdown("**Extracted side effects:**")
                st.write(", ".join(d["side_effects"]))

            excerpt = (d.get("text") or "")[:600]
            if excerpt:
                st.markdown("**Excerpt:**")
                st.write(excerpt + "...")
            st.markdown("---")

else:
    st.info("Enter a medication name and a question, then click **Ask**.")
