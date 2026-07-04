"""
Bài 16: Streamlit Chat App — Stock Research Assistant
Chạy: streamlit run phase4/app.py
"""
import os
import uuid
from operator import add
from typing import Annotated, TypedDict

import chromadb
import streamlit as st
import yfinance as yf
from dotenv import load_dotenv
from google import genai
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from sentence_transformers import SentenceTransformer

# ── Setup ──────────────────────────────────────────────────────────────────────
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

CHROMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")


# ── State ──────────────────────────────────────────────────────────────────────
class AppState(TypedDict):
    messages: Annotated[list[dict], add]   # lịch sử hội thoại, cộng dồn qua turns
    symbols: list[str]                     # ["NVDA", "AMD"]
    company_data: dict                     # {"NVDA": "...", "AMD": "..."}


# ── Resources (khởi tạo 1 lần, cache lại) ─────────────────────────────────────
# FIX 1: tách riêng get_resources() để collect_for_symbol() dùng được
@st.cache_resource
def get_resources():
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)  # FIX 2: đúng API
    collection = chroma_client.get_collection("multi_company_reports")
    return embed_model, collection


# ── Agent functions ────────────────────────────────────────────────────────────
def get_financial_snapshot(symbol: str) -> str:
    ticker = yf.Ticker(symbol)
    info = ticker.info
    return (
        f"Symbol: {symbol}\n"
        f"  Giá hiện tại : ${info.get('currentPrice', 'N/A')}\n"
        f"  Market Cap   : ${info.get('marketCap', 'N/A'):,}\n"
        f"  P/E ratio    : {info.get('trailingPE', 'N/A')}\n"
        f"  Revenue (TTM): ${info.get('totalRevenue', 'N/A'):,}"
    )


def collect_for_symbol(symbol: str, question: str) -> str:
    financial_snapshot = get_financial_snapshot(symbol)

    # FIX 3: lấy embed_model + collection từ get_resources(), dùng query_embeddings
    embed_model, collection = get_resources()
    query_embedding = embed_model.encode(question).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        where={"symbol": symbol}
    )

    report_chunks = results["documents"][0] if results["documents"] else []
    report_text = "\n".join(report_chunks) if report_chunks else "Không có báo cáo liên quan."

    return (
        f"=== {symbol} ===\n"
        f"[Tài chính]\n{financial_snapshot}\n"
        f"[Báo cáo]\n{report_text}"
    )


def data_collection_node(state: AppState) -> dict:
    question = state["messages"][-1]["content"]
    company_data = {}
    for symbol in state["symbols"]:
        company_data[symbol] = collect_for_symbol(symbol, question)
    return {"company_data": company_data}


def analysis_node(state: AppState) -> dict:
    context = "\n\n".join(state["company_data"].values())

    history = ""
    for msg in state["messages"][:-1]:
        role = "Người dùng" if msg["role"] == "user" else "Assistant"
        history += f"{role}: {msg['content']}\n"

    question = state["messages"][-1]["content"]

    prompt = (
        f"Lịch sử hội thoại:\n{history}\n"
        f"Thông tin tài chính:\n{context}\n\n"
        f"Câu hỏi hiện tại: {question}\n"
        f"Trả lời dựa trên dữ liệu trên, có so sánh nếu được hỏi."
    )
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return {"messages": [{"role": "assistant", "content": response.text}]}


# ── Graph ──────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_graph():
    builder = StateGraph(AppState)
    # FIX 4: add_node(tên, hàm) — tên phải là tham số đầu tiên
    builder.add_node("data_collection", data_collection_node)
    builder.add_node("analysis", analysis_node)
    builder.add_edge(START, "data_collection")
    builder.add_edge("data_collection", "analysis")
    builder.add_edge("analysis", END)

    memory = MemorySaver()
    # FIX 5: compile() trả về compiled graph — phải return cái này
    return builder.compile(checkpointer=memory)


# ── Streamlit UI ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Stock Research Assistant", page_icon="📊")
st.title("📊 Stock Research Assistant")

with st.sidebar:
    st.header("Cài đặt")
    symbols_input = st.text_input(
        "Mã cổ phiếu (phân cách bằng dấu phẩy)",
        value="NVDA,AMD",
        help="Ví dụ: NVDA,AMD hoặc AAPL,MSFT,GOOGL"
    )
    symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]

    if st.button("🗑️ Xoá lịch sử"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    st.markdown("---")
    st.caption(f"Session: `{st.session_state.get('thread_id', '')[:8]}...`")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"].replace("$", r"\$"))

if question := st.chat_input("Hỏi về cổ phiếu... (ví dụ: So sánh doanh thu NVDA và AMD)"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    graph = get_graph()
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    with st.spinner("Đang phân tích..."):
        initial_state: AppState = {
            "symbols": symbols,
            "messages": [{"role": "user", "content": question}],
            "company_data": {},
        }
        # FIX 6: invoke(state, config=...) — không dùng initial_state= làm keyword
        result = graph.invoke(initial_state, config=config)
        answer = result["messages"][-1]["content"]

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer.replace("$", r"\$"))
