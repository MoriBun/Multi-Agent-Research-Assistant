from operator import add
from typing import Annotated, TypedDict

# ── State ──────────────────────────────────────────────────────────────────────
class AppState(TypedDict):
    messages: Annotated[list[dict], add]   # lịch sử hội thoại, cộng dồn qua turns
    symbols: list[str]                     # ["NVDA", "AMD"]
    company_data: dict                     # {"NVDA": "...", "AMD": "..."}