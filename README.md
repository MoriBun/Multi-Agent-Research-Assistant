# Multi-Agent Stock Research Assistant

A conversational AI system that answers financial questions about stocks by combining real-time market data and SEC report analysis. Built with LangGraph multi-agent orchestration, RAG (Retrieval-Augmented Generation), and a Streamlit chat interface.

## Architecture

```
User Question
      ↓
LLM Router (Gemini) ── decides which agents to run
      ↓
┌─────────────────────────────────────────┐
│         Data Collection (per symbol)    │
│  ├── yfinance      → real-time price,   │
│  │                   market cap, P/E    │
│  └── ChromaDB RAG  → SEC 10-Q / slides  │
│                      (PDF embeddings)   │
└─────────────────────────────────────────┘
      ↓
Analysis Agent (Gemini) ── synthesizes answer
      ↓
Streamlit UI  (conversation memory via MemorySaver)
```

Multi-turn conversations are preserved per session using LangGraph's `MemorySaver` checkpointer. Each session is identified by a unique `thread_id`.

## Features

- **Multi-company comparison** — analyze and compare multiple stocks in a single query (e.g. NVDA vs AMD)
- **RAG over SEC reports** — answers grounded in 10-Q filings and earnings slides ingested into ChromaDB
- **LLM-based routing** — Gemini selects the appropriate agents based on query semantics, not keyword matching
- **Conversation memory** — follow-up questions retain full context from earlier in the session
- **Structured logging** — every agent step is logged with timestamps and duration for observability
- **Dockerized** — runs in a container with volume-mounted data and env-var secrets

## Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Google Gemini 2.5 Flash (`google-genai`) |
| Agent Orchestration | LangGraph |
| Vector Database | ChromaDB |
| Embeddings | `sentence-transformers` (all-MiniLM-L6-v2) |
| Financial Data | yfinance |
| PDF Parsing | PyMuPDF |
| UI | Streamlit |
| Containerization | Docker |

## Prerequisites

- Python 3.11+
- Google Gemini API key — get one free at [aistudio.google.com](https://aistudio.google.com)
- Docker (optional, for containerized run)

## Setup

```bash
# 1. Clone and install dependencies
git clone <repo-url>
cd "Multi-Agent Research Assistant project"
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt

# 2. Create .env file
echo GOOGLE_API_KEY=your_key_here > .env

# 3. Ingest PDF reports into ChromaDB (run once)
python phase4/ingest_reports.py   # builds phase4/chroma_db/

# 4. Run the app
streamlit run phase4/app.py
```

Open http://localhost:8501 in your browser.

## Run with Docker

```bash
# Build image
docker build -t stock-assistant .

# Run container (mount chroma_db so data persists)
docker run -p 8501:8501 \
  -e GOOGLE_API_KEY=your_key_here \
  -v "$(pwd)/phase4/chroma_db:/app/phase4/chroma_db" \
  stock-assistant
```

## Project Structure

```
├── phase1/                  # LLM basics — Gemini API, tool use, yfinance
├── phase2/                  # RAG — PDF parsing, embeddings, ChromaDB
├── phase3/                  # Multi-agent — LangGraph orchestrator
├── phase4/
│   ├── app.py               # Streamlit chat app (main entry point)
│   ├── chroma_db/           # Vector store (gitignored)
│   ├── data/                # Source PDF reports (gitignored)
│   ├── lesson13_multi_doc_rag.ipynb
│   ├── lesson14_llm_router.ipynb
│   ├── lesson15_multi_company.ipynb
│   ├── lesson16_memory_streamlit.ipynb
│   ├── lesson17_docker.ipynb
│   └── lesson18_logging.ipynb
├── Dockerfile
├── .dockerignore
└── requirements.txt
```

## Learning Path

This project was built lesson-by-lesson across 4 phases:

| Phase | Topics |
|-------|--------|
| 1 | Gemini API, function calling, yfinance integration |
| 2 | PDF parsing, vector embeddings, RAG pipeline |
| 3 | LangGraph agents, orchestrator pattern, report generation |
| 4 | Multi-doc RAG, LLM router, Streamlit UI, Docker, logging |
