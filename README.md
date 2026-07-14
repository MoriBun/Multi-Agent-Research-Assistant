# Multi-Agent Stock Research Assistant

A conversational AI assistant that answers financial questions about publicly-traded companies by combining **real-time market data** with **analysis of official SEC filings**. Ask in plain language — the system figures out which companies you mean, gathers the data, and answers with **cited sources**.

**[🔗 Live Demo](https://multi-agent-research-assistant-5mpyveuq2jyucxs8hajxyy.streamlit.app/)** · Built with LangGraph · Google Gemini · ChromaDB RAG · Streamlit

> Try it: type a ticker (e.g. `TSLA`) to pull its latest 10-Q from SEC EDGAR, or upload your own PDF report, then ask questions about it.

---

## Features

- **Ask in natural language** — "Compare Nvidia and Tesla's latest quarter" → the system extracts the tickers itself (no dropdowns, no manual entry).
- **User-built knowledge base** — starts empty; you populate it two ways:
  - **Upload PDFs** — ticker is auto-detected from the document (you confirm before adding).
  - **SEC EDGAR auto-fetch** — type a ticker and the latest 10-Q is pulled straight from SEC, no download needed.
- **Grounded answers with citations** — every response shows which report chunks it used, so you can verify.
- **Real-time financials** — live price, market cap, P/E, and revenue via yfinance, merged with the filing analysis.
- **Multi-company comparison** in a single question.
- **Conversation memory** — follow-up questions keep context within a session.
- **Manage your data** — delete any document from the knowledge base in one click.
- **Idempotent ingestion** — re-adding the same report replaces it instead of creating duplicates.
- **Flexible API key** — runs on the app's key by default; users can supply their own.

---

## Architecture

The request pipeline is a **LangGraph** state machine, run once per user question with per-session memory:

```
User question
     │
     ▼
[symbol_extraction]   Gemini reads the question → ["NVDA", "TSLA"]
     │
     ▼
[data_collection]     for each ticker:
                        • yfinance  → price, market cap, P/E, revenue (TTM)
                        • ChromaDB  → most relevant report chunks (+ source metadata)
     │
     ▼
[analysis]            Gemini synthesizes an answer grounded in the gathered data
     │
     ▼
Answer + citations    rendered in Streamlit; conversation remembered per session
```

Conversation state is persisted with LangGraph's `MemorySaver`, keyed by a per-session `thread_id`.

The **knowledge base** (ChromaDB) is built by the user and shared across the three ingestion paths, which all funnel through one core:

```
 upload PDF ─┐
 SEC EDGAR ──┤──→ ingest_text()  →  chunk → embed → store (idempotent)
 (future)  ──┘
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Google Gemini (`gemini-flash-latest` via `google-genai`) |
| Agent orchestration | LangGraph |
| Vector database | ChromaDB |
| Embeddings | `sentence-transformers` (all-MiniLM-L6-v2) |
| Financial data | yfinance |
| PDF parsing | PyMuPDF |
| SEC filings | SEC EDGAR API + BeautifulSoup |
| UI | Streamlit |
| Deployment | Streamlit Community Cloud · Docker |

---

## Project Structure

```
app/                         # ← the product (production code)
├── main.py                  #   Streamlit UI (entry point)
├── config.py                #   Gemini client, model name, paths
├── logging_setup.py         #   structured logger
├── core/
│   ├── state.py             #   AppState (shared graph state)
│   └── graph.py             #   LangGraph wiring + checkpointer
├── agents/                  # the "thinking" — graph nodes
│   ├── symbol_extraction.py #   question → tickers
│   ├── data_collection.py   #   gather financials + report chunks
│   └── analysis.py          #   synthesize the answer
└── services/                # the "doing" — where data comes from
    ├── financial.py         #   yfinance
    ├── rag.py               #   ChromaDB (query, KB status, delete)
    ├── ingest.py            #   PDF/text → chunks → embeddings (+ ticker detection)
    └── edgar.py             #   fetch 10-Q filings from SEC

data/                        # runtime vector store (gitignored)

phase1/ … phase5/            # the learning journey (see below)
Dockerfile · requirements.txt · README.md
```

**Layering:** `main.py` (UI) → `core` + `agents` (orchestration) → `services` (data access). Dependencies only point downward.

---

## Getting Started (local)

```bash
git clone <repo-url>
cd "Multi-Agent Research Assistant project"

python -m venv .venv
.venv\Scripts\activate            # Windows  (use: source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt

echo GOOGLE_API_KEY=your_key_here > .env   # get a free key at aistudio.google.com

streamlit run app/main.py
```

Open http://localhost:8501. The knowledge base starts empty — upload a PDF or fetch a 10-Q from SEC to begin asking document-grounded questions.

---

## Run with Docker

```bash
docker build -t stock-assistant .

docker run -p 8501:8501 \
  -e GOOGLE_API_KEY=your_key_here \
  -v "$(pwd)/data:/app/data" \
  stock-assistant
```

The `-v` mount keeps the ChromaDB knowledge base on your host so it survives container restarts.

---

## Deployment

Deployed on **Streamlit Community Cloud** (free):

1. Push to a public GitHub repo.
2. At [share.streamlit.io](https://share.streamlit.io): **Create app** → select the repo → **main file path: `app/main.py`**.
3. Under **Advanced settings → Secrets**, add:
   ```toml
   GOOGLE_API_KEY = "your_key_here"
   ```
4. Deploy.

> Note: the cloud filesystem is ephemeral, so the knowledge base resets when the app reboots — by design, users rebuild it per session via upload / EDGAR. For persistent storage, swap ChromaDB for a hosted vector database.

---

## Extending

The layered `app/` structure is built to grow:

- **New data source** (news, earnings transcripts, alternative data)? Add a module in `services/` and call it from an agent — the RAG/embedding logic never changes because everything ingests through `ingest_text()`.
- **New reasoning step** (sentiment, risk scoring, valuation)? Add a node in `agents/` and wire it into `core/graph.py`. The other nodes are untouched.
- **Swap the model or embeddings**? One change in `config.py`.

---

## Learning Path

Built lesson-by-lesson across five phases — from zero LLM experience to a deployed product:

| Phase | Focus |
|-------|-------|
| 1 | Gemini API, function calling, yfinance |
| 2 | PDF parsing, embeddings, RAG pipeline |
| 3 | LangGraph agents, orchestrator pattern |
| 4 | Multi-doc RAG, LLM routing, Streamlit UI, Docker, logging |
| 5 | **From project to product** — modular refactor, document upload, citations, natural-language ticker extraction, PDF ticker auto-detection, SEC EDGAR auto-fetch, flexible API keys, deployment |

The `phaseN/` folders contain the notebooks documenting each step. The runnable product lives entirely in `app/`.
