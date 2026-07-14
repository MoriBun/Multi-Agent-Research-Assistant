from functools import lru_cache

import requests
from bs4 import BeautifulSoup
from logging_setup import logger

SEC_HEADERS = {"User-Agent": "StockResearchAssistant hhoang181004@gmail.com"}

@lru_cache(maxsize=1)
def _load_tickers() -> dict:
    """Tải bảng ticker→CIK từ SEC. Cache cả tiến trình → chỉ tải 1 lần."""
    return requests.get("https://www.sec.gov/files/company_tickers.json", headers=SEC_HEADERS).json()


def get_cik(ticker: str) -> str | None:
    """ticker → CIK (10 chữ số). None nếu không tìm thấy."""
    tickers = _load_tickers()
    ticker = ticker.upper()
    for entry in tickers.values():
        if entry["ticker"] == ticker:
            return str(entry["cik_str"]).zfill(10)
    return None

def html_to_text(html: str) -> str:
    """Bóc text sạch từ HTML 10-Q — loại metadata iXBRL và phần tử ẩn."""
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style"]):
        t.decompose()
    # ix:header = khối chứa toàn bộ context/hidden facts XBRL (rác)
    for t in soup.find_all(lambda tag: tag.name and tag.name.startswith("ix:header")):
        t.decompose()
    # các fact ẩn display:none
    for t in soup.find_all(style=lambda s: s and "display:none" in s.replace(" ", "").lower()):
        t.decompose()
    return soup.get_text(separator=" ", strip=True)

def fetch_latest_10q(ticker: str) -> tuple[str, str] | None:
    """Trả về (text, source_name) của 10-Q mới nhất. None nếu không có."""
    cik = get_cik(ticker)
    if not cik:
        logger.warning(f"[edgar] Không tìm thấy CIK cho {ticker}")
        return None

    subs = requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json", headers=SEC_HEADERS).json()
    recent = subs["filings"]["recent"]

    for form, acc, doc, date in zip(
        recent["form"], recent["accessionNumber"], recent["primaryDocument"], recent["filingDate"]
    ):
        if form == "10-Q":
            acc_nodash = acc.replace("-", "")
            # TODO: dựng doc_url (xem Phần 2), tải html, bóc text bằng BeautifulSoup
            doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_nodash}/{doc}"
            html = requests.get(doc_url, headers=SEC_HEADERS).text
            text = html_to_text(html)
            source_name = f"{ticker.upper()}-10Q-{date}-SEC"
            logger.info(f"[edgar] Lấy 10-Q {ticker} ({date})")
            # TODO: return (text, source_name)
            return text, source_name

    logger.warning(f"[edgar] {ticker} không có 10-Q")
    return None