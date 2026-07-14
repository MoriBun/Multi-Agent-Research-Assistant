import streamlit as st
from services.edgar import fetch_latest_10q
from services.ingest import detect_symbol_from_pdf, ingest_pdf, ingest_text
from core.state import AppState
import uuid
from core.graph import get_graph
from services.rag import get_kb_status, delete_document

# ── Streamlit UI ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Stock Research Assistant", page_icon="📊")
st.title("📊 Stock Research Assistant")

with st.sidebar:
    st.header("Cài đặt")

    if st.button("🗑️ Xoá lịch sử"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    st.markdown("---")
    st.subheader("📎 Tải lên báo cáo")

    uploaded_files = st.file_uploader(
        "Chọn PDF", type="pdf", accept_multiple_files=True
    )

    confirmed = {}   # {tên_file: mã user xác nhận}
    if uploaded_files:
        st.caption("Mã nhận diện tự động — sửa nếu sai:")
        for file in uploaded_files:
            # TODO: đoán 1 lần cho mỗi file, lưu vào session_state
            key = f"detected::{file.name}"
            if key not in st.session_state:
                with st.spinner(f"Đang nhận diện {file.name}..."):
                    st.session_state[key] = detect_symbol_from_pdf(file.getvalue())

            # TODO: ô nhập mã cho file này, value = mã đã đoán, key riêng theo tên file
            confirmed[file.name] = st.text_input(
                f"Mã cho `{file.name}`",
                value=st.session_state[key],
                key=f"confirm::{file.name}",
            )

    if st.button("➕ Thêm vào hệ thống"):
        if not uploaded_files:
            st.warning("Vui lòng chọn ít nhất một file PDF.")
        else:
            for file in uploaded_files:
                symbol = confirmed[file.name].upper().strip()
                # TODO: nếu symbol rỗng hoặc == "UNKNOWN" → st.warning + bỏ qua (continue)
                # Nếu hợp lệ → ingest_pdf(file.getvalue(), symbol, file.name)
                #   rồi st.success(f"Đã thêm {n} chunks từ {file.name} ({symbol})")
                if not symbol or symbol == "UNKNOWN":
                    st.warning(f"File `{file.name}` bị bỏ qua vì mã ticker không hợp lệ.")
                    continue
                n = ingest_pdf(file.getvalue(), symbol, file.name)
                st.success(f"Đã thêm {n} chunks từ `{file.name}` ({symbol})")

    
    st.markdown("---")
    st.subheader("🏛️ Kéo báo cáo từ SEC")
    edgar_ticker = st.text_input("Mã cổ phiếu (Mỹ)", key="edgar_ticker", placeholder="VD: TSLA")
    if st.button("⬇️ Kéo 10-Q mới nhất"):
        ticker = edgar_ticker.upper().strip()
        if not ticker:
            st.warning("Nhập mã cổ phiếu trước.")
        else:
            with st.spinner(f"Đang lấy 10-Q của {ticker} từ SEC..."):
                result = fetch_latest_10q(ticker)
            if result is None:
                st.error("Không tìm thấy 10-Q")
            else:
                text, source = result
                n = ingest_text(text, ticker, source)
                st.success(f"Đã thêm {n} chunks từ {source}")
                st.rerun()   # cập nhật mục Kho tài liệu

    st.markdown("---")
    st.subheader("📚 Kho tài liệu")
    kb = get_kb_status()
    if not kb:
        st.caption("Kho đang trống. Hãy tải lên báo cáo để hỏi đáp dựa trên tài liệu.")
    else:
        for sym, files in kb.items():
            st.markdown(f"**{sym}** — {len(files)} tài liệu")
            for f in files:
                col1, col2 = st.columns([5, 1])
                col1.caption(f"• {f}")
                if col2.button("🗑️", key=f"del::{sym}::{f}"):
                    delete_document(sym, f)
                    st.success(f"Đã xóa tài liệu `{f}` của {sym}.")
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
        if msg.get("sources"):                                          # ← chỉ khi có nguồn
            with st.expander(f"📎 Nguồn tham khảo ({len(msg['sources'])} đoạn)"):
                for s in msg["sources"]:
                    st.markdown(f"**[{s['symbol']}]** `{s['source']}`")
                    st.caption(s["snippet"].replace("$", r"\$") + "...")

if question := st.chat_input("Hỏi về cổ phiếu... (ví dụ: So sánh doanh thu NVDA và AMD)"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    graph = get_graph()
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    with st.spinner("Đang phân tích..."):
        initial_state: AppState = {
            "symbols": [],  # ← khởi tạo danh sách symbols rỗng
            "messages": [{"role": "user", "content": question}],
            "company_data": {},
            "sources": [],  # ← khởi tạo danh sách sources rỗng
        }
        result = graph.invoke(initial_state, config=config)
        answer = result["messages"][-1]["content"]


    st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": result.get("sources", []),     # ← đính kèm
        })
    st.rerun() # ← chạy lại để vòng lặp lịch sử render câu trả lời kèm citations
