"# CapStone" 
"# CapStone" 

Goal: User asks about medication side effects → app retrieves relevant info from your CSV + scraped content → LLM + agent synthesize a readable answer (with strong disclaimers, no medical advice).

v

User → Streamlit → Agent → CSV Search + Async Scraper → LLM → Streamlit


Main components
•	Data sources
o	CSV files: medication names, side effects, maybe severity, frequency, notes.
o	Web scraped pages: public, allowed sources with general info (not scraped against ToS).
•	Data pipeline
o	Ingestion: load CSVs and scraped text into DataFrames.
o	Preprocessing: normalize drug names, clean text, maybe generate embeddings.
o	Storage: in memory (for small project) or a simple local DB / vector store.
•	LLM + agent
o	LLM: a model (e.g., Gemini API) you call from Python.
o	Tools for the agent:
	search_csv_tool(query) – finds relevant rows.
	search_docs_tool(query) – searches scraped pages (keyword or vector search).
o	Agent loop: decides when to call which tool, then uses results to answer.
•	Streamlit app
o	Input box for question.
o	Radio/checkbox for medication name (optional).
o	Show retrieved sources + final answer + disclaimer.
•	Dev environment
o	Google Antigravity is just your agentic IDE: you use it to manage this repo, run the app, and leverage its AI agents to refactor, add tests, and prototype code faster.
"# CapStone" 
"# CapStone" 
"# CapStone" 
"# CapStone" 
