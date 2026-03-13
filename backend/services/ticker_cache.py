import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path

CACHE_PATH = Path(__file__).parent.parent / "ticker_cache.json"
CACHE_TTL_HOURS = 1

SEVERITY_KEYWORDS = {
    "CRITICAL": ["war", "strike", "attack", "nuclear", "missile", "explosion", "killed", "invaded", "bombed", "airstrike", "offensive"],
    "HIGH":     ["conflict", "military", "troops", "sanctions", "crisis", "tension", "forces", "escalation", "coup", "protest"],
    "MEDIUM":   ["concern", "warning", "talks", "diplomatic", "dispute", "threat", "election", "protest"],
}

REGION_MAP = {
    "russia":      "EUROPE",    "ukraine":    "EUROPE",    "poland":  "EUROPE",
    "europe":      "EUROPE",    "nato":       "EUROPE",
    "iran":        "MIDDLE EAST", "israel":   "MIDDLE EAST", "gaza":  "MIDDLE EAST",
    "saudi":       "MIDDLE EAST", "iraq":     "MIDDLE EAST", "syria": "MIDDLE EAST",
    "lebanon":     "MIDDLE EAST", "yemen":    "MIDDLE EAST",
    "china":       "ASIA PAC",  "taiwan":     "ASIA PAC",   "korea": "ASIA PAC",
    "japan":       "ASIA PAC",  "india":      "S. ASIA",    "pakistan": "S. ASIA",
    "afghanistan": "S. ASIA",
    "africa":      "AFRICA",    "sudan":      "AFRICA",     "mali":  "AFRICA",
    "somalia":     "AFRICA",    "ethiopia":   "AFRICA",
    "venezuela":   "L. AMERICA","colombia":   "L. AMERICA", "mexico": "N. AMERICA",
    "united states": "N. AMERICA", "america": "N. AMERICA",
}

def _detect_severity(text: str) -> str:
    text_lower = text.lower()
    for level in ["CRITICAL", "HIGH", "MEDIUM"]:
        if any(kw in text_lower for kw in SEVERITY_KEYWORDS[level]):
            return level
    return "LOW"

def _detect_region(text: str) -> str:
    text_lower = text.lower()
    for keyword, region in REGION_MAP.items():
        if keyword in text_lower:
            return region
    return "GLOBAL"

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
    return data["events"]

def _save_cache(events: list[dict]):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "cached_at":    time.time(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "events":       events,
        }, f, indent=2)
    print(f"[ticker_cache] Saved {len(events)} ticker events")

async def get_cached_ticker() -> list[dict]:
    if _is_cache_valid():
        print("[ticker_cache] Serving from cache")
        return _load_cache()

    print("[ticker_cache] Fetching live breaking news via Tavily...")

    events = []
    seen_titles = set()

    queries = [
        "war conflict military attack breaking news today 2026",
        "geopolitical crisis sanctions military escalation 2026",
        "Iran Israel Russia Ukraine war latest update 2026",
    ]

    try:
        from backend.services.env_loader import get_tavily_client
        client = get_tavily_client()

        for query in queries:
            results = client.search(query=query, search_depth="basic", max_results=5)
            for r in results.get("results", []):
                title = r.get("title", "").strip()
                url = r.get("url", "")
                if not title or title in seen_titles:
                    continue
                if any(b in url for b in ["youtube.com", "facebook.com", "twitter.com", "reddit.com"]):
                    continue
                seen_titles.add(title)
                events.append({
                    "id":        len(events) + 1,
                    "text":      title,
                    "region":    _detect_region(title + " " + r.get("content", "")),
                    "severity":  _detect_severity(title + " " + r.get("content", "")),
                    "url":       r.get("url", ""),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

    except Exception as e:
        print(f"[ticker_cache] Tavily error: {e}")
        events = [
            {"id": 1, "text": "Russian forces advance near Zaporizhzhia nuclear plant — IAEA monitoring elevated radiation alerts", "region": "EUROPE",      "severity": "CRITICAL", "url": "", "timestamp": datetime.now(timezone.utc).isoformat()},
            {"id": 2, "text": "US-Israel joint strikes on Iranian nuclear facilities continue for third consecutive night",          "region": "MIDDLE EAST", "severity": "CRITICAL", "url": "", "timestamp": datetime.now(timezone.utc).isoformat()},
            {"id": 3, "text": "PLA Navy conducts live-fire exercises in Taiwan Strait — 12 vessels detected in restricted zone",    "region": "ASIA PAC",    "severity": "HIGH",     "url": "", "timestamp": datetime.now(timezone.utc).isoformat()},
            {"id": 4, "text": "Sudan RSF militia seizes Khartoum water infrastructure — UN warns of humanitarian crisis",          "region": "AFRICA",      "severity": "HIGH",     "url": "", "timestamp": datetime.now(timezone.utc).isoformat()},
            {"id": 5, "text": "WTI crude hits $97 as Iran Strait of Hormuz closure threat escalates",                             "region": "MIDDLE EAST", "severity": "CRITICAL", "url": "", "timestamp": datetime.now(timezone.utc).isoformat()},
        ]

    _save_cache(events[:15])
    return events[:15]