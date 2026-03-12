from fastapi import APIRouter
from backend.services.narrative_cache import get_cached_narratives

router = APIRouter()

_narratives_store: list[dict] = []

async def _ensure_loaded():
    global _narratives_store
    if not _narratives_store:
        _narratives_store = await get_cached_narratives()

@router.get("/narratives")
async def get_narratives():
    await _ensure_loaded()
    return _narratives_store

@router.post("/narratives/refresh")
async def refresh_narratives():
    global _narratives_store
    from backend.services.narrative_cache import CACHE_PATH
    if CACHE_PATH.exists():
        CACHE_PATH.unlink()
    _narratives_store = await get_cached_narratives()
    return {"status": "refreshed", "count": len(_narratives_store)}