from fastapi import APIRouter
from backend.services.signal_cache import get_cached_signals

router = APIRouter()

_signals_store: list[dict] = []

async def _ensure_loaded():
    global _signals_store
    if not _signals_store:
        _signals_store = await get_cached_signals()

@router.get("/signals")
async def get_signals():
    await _ensure_loaded()
    return _signals_store

@router.post("/signals/refresh")
async def refresh_signals():
    """Force regenerate — deletes cache and rebuilds via Tavily + Groq."""
    global _signals_store
    from backend.services.signal_cache import CACHE_PATH
    if CACHE_PATH.exists():
        CACHE_PATH.unlink()
    _signals_store = await get_cached_signals()
    return {"status": "refreshed", "count": len(_signals_store)}