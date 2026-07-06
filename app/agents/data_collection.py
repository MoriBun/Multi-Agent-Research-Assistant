import time
from logging_setup import logger
from services.financial import get_financial_snapshot
from services.rag import get_resources
from core.state import AppState


def collect_for_symbol(symbol: str, question: str) -> str:
    logger.info(f"Bắt đầu xử lý {symbol}")
    start = time.time()
    financial_snapshot = get_financial_snapshot(symbol)

    embed_model, collection = get_resources()
    query_embedding = embed_model.encode(question).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=8,
        where={"symbol": symbol}
    )

    report_chunks = results["documents"][0] if results["documents"] else []
    logger.debug(f"[collect] {symbol}: tìm thấy {len(report_chunks)} chunks từ ChromaDB")
    if not report_chunks:
        logger.warning(f"[collect] {symbol}: Không tìm thấy báo cáo liên quan trong ChromaDB")

    report_text = "\n".join(report_chunks) if report_chunks else "Không có báo cáo liên quan."

    end = time.time()
    logger.info(f"Kết thúc xử lý {symbol} trong {end - start:.2f} giây")

    return (
        f"=== {symbol} ===\n"
        f"[Tài chính]\n{financial_snapshot}\n"
        f"[Báo cáo]\n{report_text}"
    )


def data_collection_node(state: AppState) -> dict:
    logger.info(f"[data_collection] Bắt đầu thu thập cho {len(state['symbols'])} symbols: {state['symbols']}")
    question = state["messages"][-1]["content"]
    company_data = {}
    for symbol in state["symbols"]:
        company_data[symbol] = collect_for_symbol(symbol, question)
    return {"company_data": company_data}