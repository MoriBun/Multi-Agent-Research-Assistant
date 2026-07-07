import streamlit as st
from services.ingest import ingest_pdf
from services.rag import get_kb_status
from core.state import AppState
import uuid
from core.graph import get_graph

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

    upload_symbol = st.text_input(
        "Mã công ty cho tài liệu",
        help="Tài liệu sẽ được gắn nhãn công ty này để hỏi đáp"
    )
    uploaded_files = st.file_uploader(
        "Chọn PDF", type="pdf", accept_multiple_files=True
    )

    if st.button("➕ Thêm vào hệ thống"):
        # TODO: kiểm tra điều kiện trước khi ingest:
        #   - upload_symbol không được rỗng
        #   - uploaded_files phải có file
        # Nếu thiếu → st.warning(...) và không làm gì
        #
        # Nếu đủ → lặp qua từng file, gọi ingest_pdf(...) với:
        #   file.getvalue(), upload_symbol.upper().strip(), file.name
        # Rồi báo st.success(f"Đã thêm {n} chunks từ {file.name}")
        if not upload_symbol.strip():
            st.warning("Vui lòng nhập mã công ty trước khi thêm tài liệu.")
        elif not uploaded_files:
            st.warning("Vui lòng chọn ít nhất một file PDF để thêm.")
        else:
            total_chunks_added = 0
            for file in uploaded_files:
                try:
                    chunks_added = ingest_pdf(file.getvalue(), upload_symbol.upper().strip(), file.name)
                    total_chunks_added += chunks_added
                    st.success(f"Đã thêm {chunks_added} chunks từ {file.name}")
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi khi thêm {file.name}: {str(e)}")
            st.success(f"Đã thêm tổng cộng {total_chunks_added} chunks từ các file đã chọn.")

    st.markdown("---")
    st.subheader("📚 Kho tài liệu")
    kb = get_kb_status()
    if not kb:
        st.caption("Kho đang trống. Hãy tải lên báo cáo để hỏi đáp dựa trên tài liệu.")
    else:
        for sym, files in kb.items():
            st.markdown(f"**{sym}** — {len(files)} tài liệu")
            for f in files:
                st.caption(f"• {f}")

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
    with st.chat_message("assistant"):
        st.markdown(answer.replace("$", r"\$"))
