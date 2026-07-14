import time
from logging_setup import logger
from config import get_client, MODEL_NAME
from core.state import AppState

def analysis_node(state: AppState) -> dict:
    logger.info(f"[analysis] Bắt đầu phân tích, context dài {sum(len(v) for v in state['company_data'].values())} ký tự")
    start = time.time()
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
    response = get_client().models.generate_content(model=MODEL_NAME, contents=prompt)
    logger.info(f"[analysis] Hoàn thành sau {time.time() - start:.2f}s")
    return {"messages": [{"role": "assistant", "content": response.text}]}