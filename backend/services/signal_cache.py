import json
import time
from datetime import datetime, timezone
from pathlib import Path
from backend.services.env_loader import get_tavily_client, get_groq_client

CACHE_PATH = Path(__file__).parent.parent / "signals_cache.json"
CACHE_TTL_HOURS = 24

SIGNAL_DEFINITIONS = [
    {"id": "sig_001", "asset": "WTI Crude",  "ticker": "WTI",    "direction": "BUY",  "confidence": 0.87, "cluster": "Energy Supply Squeeze",    "region": "EUROPE",      "search_query": "Russia Ukraine energy pipeline oil supply disruption 2026",         "asset_context": "WTI Crude oil prices"},
    {"id": "sig_002", "asset": "Gold",        "ticker": "XAUUSD", "direction": "BUY",  "confidence": 0.81, "cluster": "Middle East Escalation Arc", "region": "MIDDLE EAST", "search_query": "Israel Iran war escalation Middle East conflict 2026",              "asset_context": "Gold safe haven demand"},
    {"id": "sig_003", "asset": "USD/CNH",     "ticker": "USDCNH", "direction": "BUY",  "confidence": 0.74, "cluster": "USD Weaponization Wave",     "region": "ASIA PAC",    "search_query": "US China trade war tariffs sanctions yuan dollar 2026",            "asset_context": "USD/CNH currency pair and yuan depreciation"},
    {"id": "sig_004", "asset": "MSCI EM",     "ticker": "EEM",    "direction": "SELL", "confidence": 0.69, "cluster": "USD Weaponization Wave",     "region": "GLOBAL",      "search_query": "emerging markets dollar strength capital outflow Fed rates 2026",  "asset_context": "MSCI Emerging Markets equity index"},
]

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
        return json.load(f)["signals"]

def _save_cache(signals: list[dict]):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump({"cached_at": time.time(), "generated_at": datetime.now(timezone.utc).isoformat(), "signals": signals}, f, indent=2)
    print(f"[signal_cache] Saved {len(signals)} signals")

async def _generate_signal(defn: dict) -> dict:
    from backend.services.scorer import score_headlines
    headlines = []
    try:
        client = get_tavily_client()
        results = client.search(query=defn["search_query"], search_depth="basic", max_results=6)
        for r in results.get("results", []):
            url = r.get("url", "")
            if any(b in url for b in ["youtube.com", "facebook.com", "twitter.com", "reddit.com"]):
                continue
            headlines.append({"title": r.get("title", ""), "content": r.get("content", "")[:300], "source": url.split("/")[2] if url else ""})
    except Exception as e:
        print(f"[signal_cache] Tavily error for {defn['id']}: {e}")

    try:
        from backend.services.groq_llm import generate_signal
        signal_result = await generate_signal(headlines, f"{defn['asset_context']} — {defn['cluster']}", 50)
        summary   = signal_result.get("summary", defn["asset"] + " signal")
        reasoning = signal_result.get("reasoning", "")
    except Exception as e:
        print(f"[signal_cache] Groq error for {defn['id']}: {e}")
        summary   = defn["asset"] + " signal based on current geopolitical conditions"
        reasoning = ""

    return {
        "id":         defn["id"],
        "asset":      defn["asset"],
        "ticker":     defn["ticker"],
        "direction":  defn["direction"],
        "confidence": defn["confidence"],
        "summary":    summary,
        "reasoning":  reasoning,
        "cluster":    defn["cluster"],
        "region":     defn["region"],
        "timestamp":  datetime.now(timezone.utc).isoformat(),
    }

async def get_cached_signals() -> list[dict]:
    if _is_cache_valid():
        print("[signal_cache] Serving from cache")
        return _load_cache()
    print("[signal_cache] Regenerating signals via Tavily + Groq...")
    signals = []
    for defn in SIGNAL_DEFINITIONS:
        print(f"[signal_cache] Generating {defn['id']} ({defn['asset']})...")
        signals.append(await _generate_signal(defn))
    _save_cache(signals)
    return signals