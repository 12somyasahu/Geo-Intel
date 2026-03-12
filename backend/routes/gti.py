from fastapi import APIRouter, HTTPException
from backend.models import GTIScore

router = APIRouter()

# GTI scores reflect geopolitical reality as of March 2026
# Iran: active US/Israel strikes, Khamenei killed, currency collapse, IRGC degraded
# Russia/Ukraine: year 4 of war, active frontline
# Gaza/Lebanon: ongoing conflict
# Sudan: civil war year 2

MOCK_GTI = {
    # CRITICAL (80-100)
    "IR": {"score": 97, "level": "CRITICAL", "label": "Iran"},        # Active US+Israel war, leader killed
    "UA": {"score": 93, "level": "CRITICAL", "label": "Ukraine"},     # Active war year 4
    "RU": {"score": 91, "level": "CRITICAL", "label": "Russia"},      # Active war, sanctions
    "PS": {"score": 90, "level": "CRITICAL", "label": "Palestine"},   # Gaza active conflict
    "SD": {"score": 88, "level": "CRITICAL", "label": "Sudan"},       # Civil war year 2
    "MM": {"score": 85, "level": "CRITICAL", "label": "Myanmar"},     # Military junta civil war
    "YE": {"score": 83, "level": "CRITICAL", "label": "Yemen"},       # Houthi + US strikes
    "SY": {"score": 81, "level": "CRITICAL", "label": "Syria"},       # Post-Assad instability
    "SS": {"score": 80, "level": "CRITICAL", "label": "South Sudan"}, # Civil conflict
    "AF": {"score": 80, "level": "CRITICAL", "label": "Afghanistan"}, # Taliban control
    "IL": {"score": 82, "level": "CRITICAL", "label": "Israel"},      # Active multi-front war

    # HIGH (60-79)
    "IQ": {"score": 74, "level": "HIGH", "label": "Iraq"},            # PMF + US tensions
    "LB": {"score": 72, "level": "HIGH", "label": "Lebanon"},         # Post-Hezbollah conflict
    "KP": {"score": 70, "level": "HIGH", "label": "North Korea"},     # ICBM tests
    "CN": {"score": 68, "level": "HIGH", "label": "China"},           # Taiwan + trade war
    "TW": {"score": 65, "level": "HIGH", "label": "Taiwan"},          # Cross-strait tensions
    "PK": {"score": 63, "level": "HIGH", "label": "Pakistan"},        # Political instability
    "ET": {"score": 62, "level": "HIGH", "label": "Ethiopia"},        # Regional conflict
    "LY": {"score": 61, "level": "HIGH", "label": "Libya"},           # Factional war
    "SO": {"score": 60, "level": "HIGH", "label": "Somalia"},         # Al-Shabaab
    "ML": {"score": 60, "level": "HIGH", "label": "Mali"},            # Sahel coup
    "CF": {"score": 60, "level": "HIGH", "label": "Central African Republic"},
    "SA": {"score": 62, "level": "HIGH", "label": "Saudi Arabia"},    # Iran war fallout, oil disruption
    "MX": {"score": 55, "level": "HIGH", "label": "Mexico"},          # Cartel violence
    "VE": {"score": 52, "level": "HIGH", "label": "Venezuela"},       # Political crisis
    "KZ": {"score": 50, "level": "HIGH", "label": "Kazakhstan"},      # Russia proximity risk

    # MEDIUM (30-59)
    "TR": {"score": 48, "level": "MEDIUM", "label": "Turkey"},
    "IN": {"score": 46, "level": "MEDIUM", "label": "India"},
    "EG": {"score": 44, "level": "MEDIUM", "label": "Egypt"},         # Iran war regional spillover
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

    # LOW (0-29)
    "US": {"score": 25, "level": "LOW", "label": "United States"},    # Active Iran war actor
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
    "KR": {"score": 35, "level": "MEDIUM", "label": "South Korea"},
    "ES": {"score": 12, "level": "LOW", "label": "Spain"},
    "IT": {"score": 13, "level": "LOW", "label": "Italy"},
    "PL": {"score": 22, "level": "LOW", "label": "Poland"},
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