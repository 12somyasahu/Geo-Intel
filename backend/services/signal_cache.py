import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path

CACHE_PATH = Path(__file__).parent.parent / "signals_cache.json"
CACHE_TTL_HOURS = 24

# Base signal definitions - asset, ticker, cluster, region, countries to search
SIGNAL_DEFINITIONS = [
    {
        "id":      "sig_001",
        "asset":   "WTI Crude",
        "ticker":  "WTI",
        "direction": "BUY",
        "confidence": 0.87,
        "cluster": "Energy Supply Squeeze",
        "region":  "EUROPE",
        "search_query": "Russia Ukraine energy pipeline oil supply disruption 2026",
        "asset_context": "WTI Crude oil prices",
    },
    {
        "id":      "sig_002",
        "asset":   "Gold",
        "ticker":  "XAUUSD",
        "direction": "BUY",
        "confidence": 0.81,
        "cluster": "Middle East Escalation Arc",
        "region":  "MIDDLE EAST",
        "search_query": "Israel Iran war escalation Middle East conflict 2026",
        "asset_context": "Gold safe haven demand",
    },
    {
        "id":      "sig_003",
        "asset":   "USD/CNH",
        "ticker":  "USDCNH",
        "direction": "BUY",
        "confidence": 0.74,
        "cluster": "USD Weaponization Wave",
        "region":  "ASIA PAC",
        "search_query": "US China trade war tariffs sanctions yuan 2026",
        "asset_context": "USD/CNH currency pair and yuan depreciation",
    },
    {
        "id":      "sig_004",
        "asset":   "MSCI EM",
        "ticker":  "EEM",
        "direction": "SELL",
        "confidence": 0.69,
        "cluster": "USD Weaponization Wave",
        "region":  "GLOBAL",
        "search_query": "emerging markets dollar strength capital outflow Fed 2026",
        "asset_context": "MSCI Emerging Markets equity index",
    },
]


def _is_cache_valid() -> bool:
    if not CACHE_PATH.exists():
        return False
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        cached_at = data.get("cached_at", 0)
        age_hours = (time.time() - cached_at) / 3600
        return age_hours < CACHE_TTL_HOURS
    except Exception:
        return False


def _load_cache() -> list[dict]:
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["signals"]


def _save_cache(signals: list[dict]):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "cached_at": time.time(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "signals": signals,
        }, f, indent=2)
    print(f"[signal_cache] Saved {len(signals)} signals to {CACHE_PATH}")


async def _generate_signal(defn: dict) -> dict:
    """Fetch headlines via Tavily + generate reasoning via Groq for one signal."""
    from backend.services.tavily_search import fetch_country_intelligence
    from backend.services.groq_llm import generate_signal as groq_generate

    # Fetch headlines using the signal's search query
    try:
        from tavily import TavilyClient
        _env_path = r'D:\downloads\Geo-Intel\backend\.env'
        with open(_env_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip()

        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        results = client.search(
            query=defn["search_query"],
            search_depth="basic",
            max_results=6,
        )
        headlines = []
        for r in results.get("results", []):
            headlines.append({
                "title":   r.get("title", ""),
                "content": r.get("content", "")[:300],
                "source":  r.get("url", "").split("/")[2] if r.get("url") else "",
            })
    except Exception as e:
        print(f"[signal_cache] Tavily error for {defn['id']}: {e}")
        headlines = []

    # Generate summary + reasoning via Groq
    try:
        signal_result = await groq_generate(
            headlines,
            f"{defn['asset_context']} — {defn['cluster']}",
            50  # neutral baseline score
        )
        summary   = signal_result.get("summary", defn["asset"] + " signal")
        reasoning = signal_result.get("reasoning", "")
    except Exception as e:
        print(f"[signal_cache] Groq error for {defn['id']}: {e}")
        summary   = defn["asset"] + " signal based on current geopolitical conditions"
        reasoning = ""

    return {
        "id":        defn["id"],
        "asset":     defn["asset"],
        "ticker":    defn["ticker"],
        "direction": defn["direction"],
        "confidence": defn["confidence"],
        "summary":   summary,
        "reasoning": reasoning,
        "cluster":   defn["cluster"],
        "region":    defn["region"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def get_cached_signals() -> list[dict]:
    """Main entry point — returns cached signals, regenerating if stale."""
    if _is_cache_valid():
        print("[signal_cache] Serving from cache")
        return _load_cache()

    print("[signal_cache] Cache stale or missing — regenerating via Tavily + Groq...")
    signals = []
    for defn in SIGNAL_DEFINITIONS:
        print(f"[signal_cache] Generating {defn['id']} ({defn['asset']})...")
        sig = await _generate_signal(defn)
        signals.append(sig)

    _save_cache(signals)
    return signals