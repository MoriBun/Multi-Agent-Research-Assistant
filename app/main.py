import streamlit as st
from core.state import AppState
import uuid
from core.graph import get_graph

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
        result = graph.invoke(initial_state, config=config)
        answer = result["messages"][-1]["content"]

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer.replace("$", r"\$"))
