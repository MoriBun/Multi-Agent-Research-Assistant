import fitz
from logging_setup import logger
from services.rag import get_resources


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