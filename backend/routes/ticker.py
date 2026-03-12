from fastapi import APIRouter
from backend.services.ticker_cache import get_cached_ticker

router = APIRouter()

_ticker_store: list[dict] = []

async def _ensure_loaded():
    global _ticker_store
    if not _ticker_store:
        _ticker_store = await get_cached_ticker()

@router.get("/ticker")
async def get_ticker():
    await _ensure_loaded()
    return _ticker_store

@router.post("/ticker/refresh")
async def refresh_ticker():
    global _ticker_store
    from backend.services.ticker_cache import CACHE_PATH
    if CACHE_PATH.exists():
        CACHE_PATH.unlink()
    _ticker_store = await get_cached_ticker()
    return {"status": "refreshed", "count": len(_ticker_store)}