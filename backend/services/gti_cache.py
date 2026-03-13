import json
import time
from datetime import datetime, timezone
from pathlib import Path
from backend.services.env_loader import get_tavily_client

CACHE_PATH = Path(__file__).parent.parent / "gti_cache.json"
CACHE_TTL_HOURS = 6

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

# Event-focused queries — verbs + weapons + recency
# Multiple queries per high-priority country for burst detection
LIVE_COUNTRIES = {
    "IR": {"label": "Iran",         "queries": [
        "Iran missile strike OR airstrike OR attack today",
        "Iran Israel war casualties frontline today",
        "Iran IRGC military strike OR bombed today",
    ]},
    "UA": {"label": "Ukraine",      "queries": [
        "Ukraine missile strike OR shelling OR drone attack today",
        "Ukraine frontline battle offensive casualties today",
        "Ukraine Russia war attack killed today",
    ]},
    "RU": {"label": "Russia",       "queries": [
        "Russia Ukraine attack strike offensive today",
        "Russia military assault frontline killed today",
        "Russia airstrike drone strike shelling today",
    ]},
    "IL": {"label": "Israel",       "queries": [
        "Israel airstrike OR strike OR attack today",
        "Israel Gaza Lebanon war casualties today",
        "Israel Iran military clash killed today",
    ]},
    "PS": {"label": "Palestine",    "queries": [
        "Gaza airstrike bombing casualties killed today",
        "Palestine conflict attack humanitarian today",
    ]},
    "SD": {"label": "Sudan",        "queries": [
        "Sudan RSF attack killed conflict today",
        "Sudan civil war casualties shelling today",
    ]},
    "MM": {"label": "Myanmar",      "queries": [
        "Myanmar military attack airstrike killed today",
        "Myanmar civil war clash resistance today",
    ]},
    "YE": {"label": "Yemen",        "queries": [
        "Yemen Houthi missile strike attack today",
        "Yemen US airstrike strike killed today",
    ]},
    "SY": {"label": "Syria",        "queries": [
        "Syria attack strike killed conflict today",
        "Syria military clash insurgent today",
    ]},
    "AF": {"label": "Afghanistan",  "queries": [
        "Afghanistan Taliban attack killed today",
        "Afghanistan conflict clash explosion today",
    ]},
    "SS": {"label": "South Sudan",  "queries": [
        "South Sudan conflict attack killed today",
    ]},
    "CN": {"label": "China",        "queries": [
        "China Taiwan military strike OR drill OR threat today",
        "China PLA military escalation today",
    ]},
    "TW": {"label": "Taiwan",       "queries": [
        "Taiwan China military threat strait tension today",
        "Taiwan PLA drill invasion threat today",
    ]},
    "KP": {"label": "North Korea",  "queries": [
        "North Korea missile launch test fired today",
        "North Korea nuclear threat Kim Jong Un today",
    ]},
    "PK": {"label": "Pakistan",     "queries": [
        "Pakistan military attack conflict killed today",
        "Pakistan India border tension clash today",
    ]},
    "SA": {"label": "Saudi Arabia", "queries": [
        "Saudi Arabia Iran attack oil strike today",
        "Saudi Arabia Houthi missile drone attack today",
    ]},
    "IQ": {"label": "Iraq",         "queries": [
        "Iraq militia attack US forces killed today",
        "Iraq PMF strike clash explosion today",
    ]},
    "LB": {"label": "Lebanon",      "queries": [
        "Lebanon attack conflict killed today",
        "Lebanon Israel Hezbollah clash strike today",
    ]},
    "IN": {"label": "India",        "queries": [
        "India Pakistan border clash attack killed today",
        "India China military tension conflict today",
    ]},
    "TR": {"label": "Turkey",       "queries": [
        "Turkey military strike attack Kurdish Syria today",
        "Turkey conflict killed clash today",
    ]},
}

# Ground truth floor scores — active war zones never score below this
MINIMUM_SCORES = {
    "IR": 88, "UA": 88, "RU": 82, "IL": 85, "PS": 88,
    "SD": 85, "MM": 82, "YE": 78, "SS": 75, "AF": 75, "SY": 72,
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
        return (time.time() - data.get("cached_at", 0)) / 3600 < CACHE_TTL_HOURS
    except Exception:
        return False

def _load_cache() -> list[dict]:
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["countries"]

def _save_cache(countries: list[dict]):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "cached_at":    time.time(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "countries":    countries,
        }, f, indent=2)
    print(f"[gti_cache] Saved {len(countries)} countries")

async def _score_country(iso: str, label: str, queries: list[str]) -> dict:
    from backend.services.scorer import score_headlines, score_to_level
    all_headlines = []
    seen_titles = set()

    try:
        client = get_tavily_client()
        for query in queries:
            results = client.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                topic="news",
            )
            for r in results.get("results", []):
                url   = r.get("url", "")
                title = r.get("title", "").strip()
                if not title or title in seen_titles:
                    continue
                if any(b in url for b in ["youtube.com", "facebook.com", "twitter.com", "reddit.com", "wikipedia.org"]):
                    continue
                seen_titles.add(title)
                all_headlines.append({
                    "title":       title,
                    "content":     r.get("content", "")[:400],
                    "source":      url.split("/")[2].replace("www.", "") if url else "",
                    "publishedAt": r.get("published_date", ""),
                    "url":         url,
                })
    except Exception as e:
        print(f"[gti_cache] Tavily error for {iso}: {e}")

    score, _ = score_headlines(all_headlines, country_label=label)

    # Apply minimum floor for confirmed active war zones
    floor = MINIMUM_SCORES.get(iso, 0)
    if score < floor:
        score = floor
        print(f"[gti_cache] {iso} score floored at {floor} (calculated: {score})")

    final_score = round(min(100.0, score), 1)
    return {
        "iso":   iso,
        "score": final_score,
        "level": _score_to_level(final_score),
        "label": label,
    }

async def get_cached_gti() -> list[dict]:
    if _is_cache_valid():
        print("[gti_cache] Serving from cache")
        return _load_cache()

    print("[gti_cache] Regenerating live GTI scores with advanced scorer...")
    countries = []

    for iso, meta in LIVE_COUNTRIES.items():
        print(f"[gti_cache] Scoring {iso} ({meta['label']})...")
        countries.append(await _score_country(iso, meta["label"], meta["queries"]))

    for iso, meta in STATIC_GTI.items():
        countries.append({"iso": iso, **meta})

    _save_cache(countries)
    return countries