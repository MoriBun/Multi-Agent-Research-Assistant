import fitz
from logging_setup import logger
from services.rag import get_resources
from config import client, MODEL_NAME


def split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    # copy nguyên từ bài 13
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks


def ingest_pdf(file_bytes: bytes, symbol: str, source_name: str) -> int:
    """Đọc PDF từ bytes, chunk, embed, lưu vào ChromaDB (idempotent).
    Ingest lại cùng 1 file = thay thế bản cũ, KHÔNG tạo trùng.
    Trả về số chunks đã thêm."""
    logger.info(f"[ingest] Bắt đầu ingest '{source_name}' cho symbol {symbol}")

    # 1. Mở PDF từ bytes và lấy toàn bộ text
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = ""
    for page_num in range(doc.page_count):
        full_text += doc[page_num].get_text()
    doc.close()

    # 2. Chunk
    chunks = split_into_chunks(full_text)
    if not chunks:
        logger.warning(f"[ingest] '{source_name}' không có text để ingest — bỏ qua")
        return 0

    # 3. Lấy embed_model + collection dùng chung (KHÔNG tạo mới)
    embed_model, collection = get_resources()

    # 4. Idempotent: xoá sạch bản cũ của ĐÚNG file này (khớp cả symbol lẫn source)
    #    trước khi thêm → upload lại nhiều lần vẫn chỉ có 1 bản duy nhất
    collection.delete(where={"$and": [{"symbol": symbol}, {"source": source_name}]})

    # 5. Embed + metadata + id xác định
    embeddings = embed_model.encode(chunks).tolist()
    metadatas = [{"symbol": symbol, "source": source_name} for _ in chunks]
    ids = [f"{symbol}::{source_name}::{i}" for i in range(len(chunks))]

    collection.add(documents=chunks, embeddings=embeddings, metadatas=metadatas, ids=ids)

    logger.info(f"[ingest] Đã thêm {len(chunks)} chunks từ '{source_name}'")
    return len(chunks)

DETECT_PROMPT = """Đây là trang đầu của một báo cáo tài chính.
Xác định MÃ TICKER cổ phiếu (sàn Mỹ) của công ty phát hành báo cáo.
- Trả về DUY NHẤT mã ticker in hoa, ví dụ: NVDA
- Không xác định được → trả về: UNKNOWN

Nội dung trang đầu:
{page_text}
"""

def detect_symbol_from_pdf(file_bytes: bytes) -> str:
    """Đọc trang đầu PDF, dùng LLM đoán mã ticker. Trả 'UNKNOWN' nếu không chắc."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    first_page = doc[0].get_text()[:3000] if doc.page_count else ""
    doc.close()

    if not first_page.strip():
        return "UNKNOWN"

    try:
        prompt = DETECT_PROMPT.format(page_text=first_page)
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        symbol = response.text.strip().upper()
        # TODO: sanity check — ticker hợp lệ thường ngắn & chỉ chữ/số.
        #   Nếu symbol rỗng, hoặc dài hơn 6 ký tự, hoặc không phải chữ-số
        #   → coi như không chắc, return "UNKNOWN"
        if not symbol or len(symbol) > 6 or not symbol.isalnum():
            return "UNKNOWN"
        return symbol
    except Exception as e:
        logger.error(f"[detect] lỗi: {e}")
        return "UNKNOWN"