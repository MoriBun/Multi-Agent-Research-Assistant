import os
from functools import lru_cache
from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL_NAME = "gemini-flash-latest"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(PROJECT_ROOT, "data", "chroma_db")
COLLECTION_NAME = "multi_company_reports"


def _default_key() -> str | None:
    """Key mặc định: .env (local) hoặc st.secrets (cloud)."""
    key = os.getenv("GOOGLE_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        pass
    return None


@lru_cache(maxsize=4)
def _make_client(api_key: str):
    return genai.Client(api_key=api_key)


def get_client():
    """Gemini client. Ưu tiên key user nhập, không thì dùng key mặc định."""
    api_key = None
    try:
        import streamlit as st
        api_key = st.session_state.get("user_api_key")   # key user nhập ở sidebar
    except Exception:
        pass
    # TODO: nếu api_key rỗng/None → dùng _default_key()
    if not api_key:
        api_key = _default_key()
    return _make_client(api_key)