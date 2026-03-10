from fastapi import APIRouter
from backend.models import GTIScore

router = APIRouter()

MOCK_GTI = {
    "RU": {"score": 89, "level": "CRITICAL", "label": "Russia-Ukraine War"},
    "UA": {"score": 92, "level": "CRITICAL", "label": "Active Conflict Zone"},
    "IL": {"score": 78, "level": "HIGH",     "label": "Gaza Conflict"},
    "IR": {"score": 71, "level": "HIGH",     "label": "Nuclear Tensions"},
    "CN": {"score": 65, "level": "HIGH",     "label": "Taiwan Strait"},
    "TW": {"score": 68, "level": "HIGH",     "label": "Cross-Strait Tensions"},
    "KP": {"score": 74, "level": "HIGH",     "label": "ICBM Program"},
    "SY": {"score": 61, "level": "MEDIUM",   "label": "Ongoing Instability"},
    "YE": {"score": 58, "level": "MEDIUM",   "label": "Houthi Activity"},
    "MM": {"score": 55, "level": "MEDIUM",   "label": "Military Junta"},
}

@router.get("/gti", response_model=list[GTIScore])
def get_gti():
    return [
        GTIScore(iso=iso, **data)
        for iso, data in MOCK_GTI.items()
    ]

@router.get("/gti/{iso}", response_model=GTIScore)
def get_gti_country(iso: str):
    data = MOCK_GTI.get(iso.upper())
    if not data:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Country not found")
    return GTIScore(iso=iso.upper(), **data)