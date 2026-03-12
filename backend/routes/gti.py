from fastapi import APIRouter, HTTPException
from backend.models import GTIScore

router = APIRouter()

MOCK_GTI = {
    # CRITICAL
    "RU": {"score": 94, "level": "CRITICAL", "label": "Russia"},
    "UA": {"score": 91, "level": "CRITICAL", "label": "Ukraine"},
    "SD": {"score": 88, "level": "CRITICAL", "label": "Sudan"},
    "MM": {"score": 85, "level": "CRITICAL", "label": "Myanmar"},
    "YE": {"score": 83, "level": "CRITICAL", "label": "Yemen"},
    "SY": {"score": 82, "level": "CRITICAL", "label": "Syria"},
    "SS": {"score": 80, "level": "CRITICAL", "label": "South Sudan"},
    "AF": {"score": 79, "level": "CRITICAL", "label": "Afghanistan"},
    "IL": {"score": 78, "level": "CRITICAL", "label": "Israel"},
    "PS": {"score": 78, "level": "CRITICAL", "label": "Palestine"},
    "IQ": {"score": 76, "level": "CRITICAL", "label": "Iraq"},
    # HIGH
    "CN": {"score": 72, "level": "HIGH", "label": "China"},
    "IR": {"score": 70, "level": "HIGH", "label": "Iran"},
    "KP": {"score": 68, "level": "HIGH", "label": "North Korea"},
    "PK": {"score": 65, "level": "HIGH", "label": "Pakistan"},
    "ET": {"score": 63, "level": "HIGH", "label": "Ethiopia"},
    "LY": {"score": 61, "level": "HIGH", "label": "Libya"},
    "SO": {"score": 60, "level": "HIGH", "label": "Somalia"},
    "ML": {"score": 58, "level": "HIGH", "label": "Mali"},
    "CF": {"score": 57, "level": "HIGH", "label": "Central African Republic"},
    "MX": {"score": 54, "level": "HIGH", "label": "Mexico"},
    "VE": {"score": 52, "level": "HIGH", "label": "Venezuela"},
    "TW": {"score": 51, "level": "HIGH", "label": "Taiwan"},
    "KZ": {"score": 50, "level": "HIGH", "label": "Kazakhstan"},
    # MEDIUM
    "TR": {"score": 48, "level": "MEDIUM", "label": "Turkey"},
    "IN": {"score": 46, "level": "MEDIUM", "label": "India"},
    "SA": {"score": 44, "level": "MEDIUM", "label": "Saudi Arabia"},
    "EG": {"score": 42, "level": "MEDIUM", "label": "Egypt"},
    "NG": {"score": 41, "level": "MEDIUM", "label": "Nigeria"},
    "ZA": {"score": 39, "level": "MEDIUM", "label": "South Africa"},
    "AR": {"score": 38, "level": "MEDIUM", "label": "Argentina"},
    "BD": {"score": 36, "level": "MEDIUM", "label": "Bangladesh"},
    "KE": {"score": 34, "level": "MEDIUM", "label": "Kenya"},
    "TH": {"score": 33, "level": "MEDIUM", "label": "Thailand"},
    "PH": {"score": 32, "level": "MEDIUM", "label": "Philippines"},
    "BR": {"score": 30, "level": "MEDIUM", "label": "Brazil"},
    "CO": {"score": 29, "level": "MEDIUM", "label": "Colombia"},
    "ID": {"score": 27, "level": "MEDIUM", "label": "Indonesia"},
    # LOW
    "US": {"score": 22, "level": "LOW", "label": "United States"},
    "GB": {"score": 18, "level": "LOW", "label": "United Kingdom"},
    "FR": {"score": 16, "level": "LOW", "label": "France"},
    "DE": {"score": 14, "level": "LOW", "label": "Germany"},
    "JP": {"score": 12, "level": "LOW", "label": "Japan"},
    "CA": {"score": 10, "level": "LOW", "label": "Canada"},
    "AU": {"score":  9, "level": "LOW", "label": "Australia"},
    "SE": {"score":  8, "level": "LOW", "label": "Sweden"},
    "NO": {"score":  7, "level": "LOW", "label": "Norway"},
    "CH": {"score":  6, "level": "LOW", "label": "Switzerland"},
    "NZ": {"score":  5, "level": "LOW", "label": "New Zealand"},
    "KR": {"score": 38, "level": "LOW", "label": "South Korea"},
    "ES": {"score": 12, "level": "LOW", "label": "Spain"},
    "IT": {"score": 13, "level": "LOW", "label": "Italy"},
    "PL": {"score": 20, "level": "LOW", "label": "Poland"},
}

@router.get("/gti", response_model=list[GTIScore])
def get_gti():
    return [GTIScore(iso=iso, **data) for iso, data in MOCK_GTI.items()]

@router.get("/gti/{iso}", response_model=GTIScore)
def get_gti_country(iso: str):
    data = MOCK_GTI.get(iso.upper())
    if not data:
        raise HTTPException(status_code=404, detail="Country not found")
    return GTIScore(iso=iso.upper(), **data)