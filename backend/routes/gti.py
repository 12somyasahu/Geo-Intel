from fastapi import APIRouter, HTTPException
from backend.services.gti_cache import get_cached_gti

router = APIRouter()

_gti_store: list[dict] = []

async def _ensure_loaded():
    global _gti_store
    if not _gti_store:
        _gti_store = await get_cached_gti()

@router.get("/gti")
async def get_gti():
    await _ensure_loaded()
    return _gti_store

@router.get("/gti/{iso}")
async def get_gti_country(iso: str):
    await _ensure_loaded()
    entry = next((c for c in _gti_store if c["iso"] == iso.upper()), None)
    if not entry:
        raise HTTPException(status_code=404, detail="Country not found")
    return entry

@router.post("/gti/refresh")
async def refresh_gti():
    global _gti_store
    from backend.services.gti_cache import CACHE_PATH
    if CACHE_PATH.exists():
        CACHE_PATH.unlink()
    _gti_store = await get_cached_gti()
    return {"status": "refreshed", "count": len(_gti_store)}