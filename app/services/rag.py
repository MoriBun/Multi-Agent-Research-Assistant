import chromadb
import streamlit as st
from sentence_transformers import SentenceTransformer
from config import CHROMA_PATH, COLLECTION_NAME

# ── Resources (khởi tạo 1 lần, cache lại) ─────────────────────────────────────
@st.cache_resource
def get_resources():
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    # get_or_create: kho bắt đầu RỖNG, không crash khi chưa có tài liệu nào
    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    return embed_model, collection


def get_kb_status() -> dict[str, list[str]]:
    """Trả về {symbol: [danh sách file]} hiện có trong kho tài liệu."""
    _, collection = get_resources()
    data = collection.get(include=["metadatas"])
    status: dict[str, set] = {}
    for meta in data["metadatas"]:
        symbol = meta.get("symbol", "?")
        source = meta.get("source", "?")
        status.setdefault(symbol, set()).add(source)
    return {sym: sorted(files) for sym, files in status.items()}
