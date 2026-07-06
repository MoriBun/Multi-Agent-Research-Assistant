import chromadb
import streamlit as st
from sentence_transformers import SentenceTransformer
from config import CHROMA_PATH, COLLECTION_NAME

# ── Resources (khởi tạo 1 lần, cache lại) ─────────────────────────────────────
@st.cache_resource
def get_resources():
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_collection(COLLECTION_NAME)
    return embed_model, collection