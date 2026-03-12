import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path

CACHE_PATH = Path(__file__).parent.parent / "gti_cache.json"
CACHE_TTL_HOURS = 6

# Low-change countries — sensible static defaults, not worth burning Tavily quota
STATIC_GTI = {
    "US": {"score": 25, "level": "LOW",    "label": "United States"},
    "GB": {"score": 18, "level": "LOW",    "label": "United Kingdom"},
    "FR": {"score": 16, "level": "LOW",    "label": "France"},
    "DE": {"score": 14, "level": "LOW",    "label": "Germany"},
    "JP": {"score": 12, "level": "LOW",    "label": "Japan"},
    "CA": {"score": 10, "level": "LOW",    "label": "Canada"},
    "AU": {"score":  9, "level": "LOW",    "label": "Australia"},
    "SE": {"score":  8, "level": "LOW",    "label": "Sweden"},
    "NO": {"score":  7, "level": "LOW",    "label": "Norway"},
    "CH": {"score":  6, "level": "LOW",    "label": "Switzerland"},
    "NZ": {"score":  5, "level": "LOW",    "label": "New Zealand"},
    "KR": {"score": 35, "level": "MEDIUM", "label": "South Korea"},
    "ES": {"score": 12, "level": "LOW",    "label": "Spain"},
    "IT": {"score": 13, "level": "LOW",    "label": "Italy"},
    "PL": {"score": 22, "level": "LOW",    "label": "Poland"},
    "BR": {"score": 30, "level": "MEDIUM", "label": "Brazil"},
    "ID": {"score": 27, "level": "MEDIUM", "label": "Indonesia"},
    "AR": {"score": 38, "level": "MEDIUM", "label": "Argentina"},
    "BD": {"score": 36, "level": "MEDIUM", "label": "Bangladesh"},
    "TH": {"score": 33, "level": "MEDIUM", "label": "Thailand"},
    "PH": {"score": 32, "level": "MEDIUM", "label": "Philippines"},
    "CO": {"score": 29, "level": "MEDIUM", "label": "Colombia"},
    "KE": {"score": 34, "level": "MEDIUM", "label": "Kenya"},
    "ZA": {"score": 39, "level": "MEDIUM", "label": "South Africa"},
}

# Top 20 hotspots — live Tavily scoring
LIVE_COUNTRIES = {
    "RU": {"label": "Russia",               "query": "Russia Ukraine war military conflict March 2026"},
    "UA": {"label": "Ukraine",              "query": "Ukraine war frontline offensive defense March 2026"},
    "IR": {"label": "Iran",                 "query": "Iran US Israel war strikes military March 2026"},
    "IL": {"label": "Israel",               "query": "Israel war Gaza Lebanon Iran strikes March 2026"},
    "PS": {"label": "Palestine",            "query": "Gaza Palestine conflict humanitarian crisis March 2026"},
    "SD": {"label": "Sudan",                "query": "Sudan civil war RSF conflict humanitarian March 2026"},
    "MM": {"label": "Myanmar",              "query": "Myanmar military junta civil war resistance March 2026"},
    "YE": {"label": "Yemen",                "query": "Yemen Houthi US strikes Red Sea conflict March 2026"},
    "SY": {"label": "Syria",                "query": "Syria instability conflict post-Assad March 2026"},
    "AF": {"label": "Afghanistan",          "query": "Afghanistan Taliban conflict instability March 2026"},
    "SS": {"label": "South Sudan",          "query": "South Sudan civil conflict violence March 2026"},
    "CN": {"label": "China",                "query": "China Taiwan military tension trade war March 2026"},
    "TW": {"label": "Taiwan",               "query": "Taiwan China military strait tension March 2026"},
    "KP": {"label": "North Korea",          "query": "North Korea missile nuclear test Kim Jong Un March 2026"},
    "PK": {"label": "Pakistan",             "query": "Pakistan military political instability conflict March 2026"},
    "SA": {"label": "Saudi Arabia",         "query": "Saudi Arabia Iran war oil security March 2026"},
    "IQ": {"label": "Iraq",                 "query": "Iraq militia PMF US Iran tension March 2026"},
    "LB": {"label": "Lebanon",              "query": "Lebanon Hezbollah conflict reconstruction March 2026"},
    "IN": {"label": "India",                "query": "India border tension China Pakistan conflict March 2026"},
    "TR": {"label": "Turkey",               "query": "Turkey military conflict Syria Kurdish March 2026"},
}

def _score_to_level(score: float) -> str:
    if score >= 75: return "CRITICAL"
    if score >= 50: return "HIGH"
    if score >= 25: return "MEDIUM"
    return "LOW"

def _is_cache_valid() -> bool:
    if not CACHE_PATH.exists():
        return False
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        age_hours = (time.time() - data.get("cached_at", 0)) / 3600
        return age_hours < CACHE_TTL_HOURS
    except Exception:
        return False

def _load_cache() -> list[dict]:
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["countries"]

def _save_cache(countries: list[dict]):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "cached_at":    time.time(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "countries":    countries,
        }, f, indent=2)
    print(f"[gti_cache] Saved {len(countries)} countries")

def _load_env():
    _env_path = r'D:\downloads\Geo-Intel\backend\.env'
    with open(_env_path, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()

async def _score_country(iso: str, label: str, query: str) -> dict:
    from backend.services.scorer import score_headlines
    try:
        _load_env()
        from tavily import TavilyClient
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        results = client.search(query=query, search_depth="basic", max_results=6)
        headlines = []
        for r in results.get("results", []):
            headlines.append({
                "title":   r.get("title", ""),
                "content": r.get("content", "")[:300],
                "source":  r.get("url", "").split("/")[2] if r.get("url") else "",
            })
        score, _ = score_headlines(headlines)
        # Clamp so active war zones don't score LOW due to analytical headlines
        if iso in ["IR", "UA", "RU", "PS", "SD", "YE", "IL"] and score < 60:
            score = max(score, 60 + (hash(iso) % 20))
    except Exception as e:
        print(f"[gti_cache] Error scoring {iso}: {e}")
        score = 40.0

    return {
        "iso":   iso,
        "score": round(score, 1),
        "level": _score_to_level(score),
        "label": label,
    }

async def get_cached_gti() -> list[dict]:
    if _is_cache_valid():
        print("[gti_cache] Serving from cache")
        return _load_cache()

    print("[gti_cache] Regenerating live GTI scores...")
    countries = []

    # Live scored countries
    for iso, meta in LIVE_COUNTRIES.items():
        print(f"[gti_cache] Scoring {iso}...")
        entry = await _score_country(iso, meta["label"], meta["query"])
        countries.append(entry)

    # Static defaults
    for iso, meta in STATIC_GTI.items():
        countries.append({"iso": iso, **meta})

    _save_cache(countries)
    return countries