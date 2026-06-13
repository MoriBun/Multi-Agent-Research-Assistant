import yfinance as yf

for ticker in ["AAPL", "TSLA"]:
    ticker_obj = yf.Ticker(ticker)
    info = ticker_obj.info
    history = ticker_obj.history(period="3d")

    print(f"--- {info['shortName']} ({ticker}) ---")
    print(f"  Giá hiện tại : {info['currentPrice']}")
    print(f"  Vốn hóa      : {info['marketCap']}")
    print(f"  Đóng cửa 3 ngày gần nhất:")
    for date, price in history["Close"].items():
        print(f"    {date.date()} : {price:.2f}")
    print()
