import fitz
from logging_setup import logger
from services.rag import get_resources
from config import get_client, MODEL_NAME


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


def ingest_text(full_text: str, symbol: str, source_name: str) -> int:
    """Lõi chung: text → chunk → embed → lưu ChromaDB (idempotent).
    Dùng cho MỌI nguồn: PDF upload, HTML từ EDGAR..."""
    logger.info(f"[ingest] Bắt đầu ingest '{source_name}' cho symbol {symbol}")
    chunks = split_into_chunks(full_text)
    if not chunks:
        logger.warning(f"[ingest] '{source_name}' không có text — bỏ qua")
        return 0
    embed_model, collection = get_resources()
    collection.delete(where={"$and": [{"symbol": symbol}, {"source": source_name}]})
    embeddings = embed_model.encode(chunks).tolist()
    metadatas = [{"symbol": symbol, "source": source_name} for _ in chunks]
    ids = [f"{symbol}::{source_name}::{i}" for i in range(len(chunks))]
    collection.add(documents=chunks, embeddings=embeddings, metadatas=metadatas, ids=ids)
    logger.info(f"[ingest] Đã thêm {len(chunks)} chunks từ '{source_name}'")
    return len(chunks)


def ingest_pdf(file_bytes: bytes, symbol: str, source_name: str) -> int:
    """PDF bytes → text → ingest_text."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = ""
    for page_num in range(doc.page_count):
        full_text += doc[page_num].get_text()
    doc.close()
    # TODO: gọi ingest_text(...) và return kết quả
    return ingest_text(full_text, symbol, source_name)

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
        response = get_client().models.generate_content(model=MODEL_NAME, contents=prompt)
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