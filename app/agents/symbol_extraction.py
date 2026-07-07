import json
from config import client, MODEL_NAME
from logging_setup import logger
from core.state import AppState

EXTRACT_PROMPT = """Bạn là bộ trích xuất mã cổ phiếu (ticker).
Từ câu hỏi (và lịch sử nếu cần), xác định mã ticker chuẩn sàn Mỹ.
- Trả về DUY NHẤT JSON: {{"symbols": ["NVDA", "TSLA"]}}
- Ánh xạ tên → ticker: Nvidia→NVDA, Tesla→TSLA, Apple→AAPL...
- Không nhắc công ty nào → {{"symbols": []}}

Lịch sử hội thoại:
{history}

Câu hỏi hiện tại: {question}
"""

def symbol_extraction_node(state: AppState) -> dict:
    question = state["messages"][-1]["content"]

    # TODO: dựng history từ state["messages"][:-1] (giống analysis_node)
    #   mỗi dòng: "Người dùng: ..." / "Assistant: ..."
    history = ""
    for msg in state["messages"][:-1]:
        role = "Người dùng" if msg["role"] == "user" else "Assistant"
        history += f"{role}: {msg['content']}\n"

    prompt = EXTRACT_PROMPT.format(history=history, question=question)

    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = "\n".join(text.split("\n")[1:-1])
        # TODO: parse JSON → lấy list symbols
        symbols = json.loads(text).get("symbols", [])
    except Exception as e:
        logger.error(f"[symbol_extraction] lỗi parse: {e} → fallback []")
        symbols = []

    logger.info(f"[symbol_extraction] rút được: {symbols}")
    return {"symbols": symbols}