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
    """Đọc PDF từ bytes, chunk, embed, lưu vào ChromaDB.
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

    # 3. Lấy embed_model + collection dùng chung (KHÔNG tạo mới)
    embed_model, collection = get_resources()

    # 4. TODO: embed chunks → list
    embeddings = embed_model.encode(chunks).tolist()

    # 5. TODO: tạo metadatas — mỗi chunk 1 dict, gồm CẢ symbol VÀ source
    metadatas = [{"symbol": symbol, "source": source_name} for _ in chunks]

    # 6. TODO: tạo ids unique — format gợi ý: f"{symbol}-{source_name}_chunk_{i}"
    #    (giống bài 13, dùng source_name để không trùng giữa các file)
    ids = [f"{symbol}-{source_name}_chunk_{i}" for i in range(len(chunks))]

    # 7. TODO: upsert vào collection (dùng upsert, KHÔNG add — để upload
    #    lại cùng file không bị lỗi 'ID already exists')
    collection.upsert(documents=chunks, embeddings=embeddings, metadatas=metadatas, ids=ids)

    logger.info(f"[ingest] Đã thêm {len(chunks)} chunks từ '{source_name}'")
    return len(chunks)