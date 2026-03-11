from fastapi import APIRouter
from backend.models import GTIScore

router = APIRouter()

MOCK_GTI = {
    "RU": {"score": 89, "level": "CRITICAL", "label": "Russia-Ukraine War"},
    "UA": {"score": 92, "level": "CRITICAL", "label": "Active Conflict Zone"},
    "IL": {"score": 78, "level": "HIGH",     "label": "Gaza Conflict"},
    "IR": {"score": 71, "level": "HIGH",     "label": "Regional Tensions"},
    "CN": {"score": 65, "level": "HIGH",     "label": "Taiwan Strait"},
    "TW": {"score": 68, "level": "HIGH",     "label": "Cross-Strait Tensions"},
    "KP": {"score": 74, "level": "HIGH",     "label": "ICBM Program"},
    "SY": {"score": 61, "level": "MEDIUM",   "label": "Ongoing Instability"},
    "YE": {"score": 58, "level": "MEDIUM",   "label": "Houthi Activity"},
    "MM": {"score": 55, "level": "MEDIUM",   "label": "Military Junta"},
    "IN": {"score": 45, "level": "MEDIUM",   "label": "Regional Tensions"},
    "PK": {"score": 62, "level": "HIGH",     "label": "Political Instability"},
    "SA": {"score": 48, "level": "MEDIUM",   "label": "Regional Power"},
    "US": {"score": 35, "level": "LOW",      "label": "Domestic Tensions"},
    "GB": {"score": 25, "level": "LOW",      "label": "Stable"},
    "DE": {"score": 22, "level": "LOW",      "label": "Stable"},
    "FR": {"score": 24, "level": "LOW",      "label": "Stable"},
    "JP": {"score": 38, "level": "LOW",      "label": "Regional Watch"},
    "KR": {"score": 42, "level": "MEDIUM",   "label": "Peninsula Tensions"},
    "BR": {"score": 30, "level": "LOW",      "label": "Political Uncertainty"},
    "AF": {"score": 85, "level": "CRITICAL", "label": "Taliban Control"},
    "IQ": {"score": 67, "level": "HIGH",     "label": "Ongoing Instability"},
    "SD": {"score": 72, "level": "HIGH",     "label": "Civil War"},
    "ET": {"score": 60, "level": "MEDIUM",   "label": "Regional Conflict"},
    "VE": {"score": 52, "level": "MEDIUM",   "label": "Political Crisis"},
    "LY": {"score": 63, "level": "HIGH",     "label": "Factional Conflict"},
    "SO": {"score": 70, "level": "HIGH",     "label": "Al-Shabaab Activity"},
    "ML": {"score": 65, "level": "HIGH",     "label": "Sahel Instability"},
    "CD": {"score": 68, "level": "HIGH",     "label": "Eastern Congo War"},
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