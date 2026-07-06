import yfinance as yf

# ── Agent functions ────────────────────────────────────────────────────────────
def get_financial_snapshot(symbol: str) -> str:
    ticker = yf.Ticker(symbol)
    info = ticker.info
    return (
        f"Symbol: {symbol}\n"
        f"  Giá hiện tại : ${info.get('currentPrice', 'N/A')}\n"
        f"  Market Cap   : ${info.get('marketCap', 'N/A'):,}\n"
        f"  P/E ratio    : {info.get('trailingPE', 'N/A')}\n"
        f"  Revenue (TTM): ${info.get('totalRevenue', 'N/A'):,}"
    )