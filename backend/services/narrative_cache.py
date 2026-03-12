import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path

CACHE_PATH = Path(__file__).parent.parent / "narrative_cache.json"
CACHE_TTL_HOURS = 24

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
    return data["narratives"]

def _save_cache(narratives: list[dict]):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "cached_at":    time.time(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "narratives":   narratives,
        }, f, indent=2)
    print(f"[narrative_cache] Saved {len(narratives)} narratives")

def _load_env():
    _env_path = r'D:\downloads\Geo-Intel\backend\.env'
    with open(_env_path, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()

async def _generate_narratives(signals: list[dict]) -> list[dict]:
    _load_env()
    from groq import Groq

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    signal_text = "\n".join([
        f"- {s['asset']} ({s['direction']} {int(s['confidence']*100)}%): {s['summary']} | Cluster: {s['cluster']} | Region: {s['region']}"
        for s in signals
    ])

    prompt = f"""You are a geopolitical market intelligence analyst. Based on the following active market signals, identify exactly 3 macro narrative clusters driving global markets right now.

ACTIVE SIGNALS:
{signal_text}

Return ONLY a JSON array with exactly 3 objects. Each object must have these exact fields:
- id: "n1", "n2", or "n3"
- title: short narrative name (max 5 words)
- summary: 2-sentence explanation of the narrative and its market implications
- strength: float 0.0-1.0 representing narrative strength
- regions: array of affected region strings
- assets: array of affected asset tickers

Return ONLY the JSON array, no markdown, no explanation, no backticks."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.3,
        )
        raw = response.choices[0].message.content.strip()
        # Strip any accidental markdown
        raw = raw.replace("```json", "").replace("```", "").strip()
        narratives = json.loads(raw)
        # Validate structure
        for n in narratives:
            n.setdefault("id", "n1")
            n.setdefault("title", "Unknown Narrative")
            n.setdefault("summary", "")
            n.setdefault("strength", 0.7)
            n.setdefault("regions", [])
            n.setdefault("assets", [])
        return narratives[:3]
    except Exception as e:
        print(f"[narrative_cache] Groq error: {e}")
        # Fallback narratives
        return [
            {
                "id": "n1",
                "title": "Energy Supply Squeeze",
                "summary": "Russia-Ukraine conflict and Iran war are simultaneously disrupting global energy supply chains. WTI crude and natural gas prices face sustained upward pressure.",
                "strength": 0.91,
                "regions": ["EUROPE", "MIDDLE EAST"],
                "assets": ["WTI", "BRENT", "XLE"],
            },
            {
                "id": "n2",
                "title": "Middle East Escalation Arc",
                "summary": "Multi-front conflict involving Iran, Israel, and US forces is driving the largest safe-haven rotation in years. Gold at $5,096 reflects systemic uncertainty.",
                "strength": 0.85,
                "regions": ["MIDDLE EAST"],
                "assets": ["XAUUSD", "XAGUSD", "CHF"],
            },
            {
                "id": "n3",
                "title": "USD Weaponization Wave",
                "summary": "US-China tariff escalation combined with hawkish Fed signals is driving dollar strength and emerging market capital outflows. EM equities face sustained pressure.",
                "strength": 0.78,
                "regions": ["ASIA PAC", "GLOBAL"],
                "assets": ["USDCNH", "EEM", "DXY"],
            },
        ]

async def get_cached_narratives() -> list[dict]:
    if _is_cache_valid():
        print("[narrative_cache] Serving from cache")
        return _load_cache()

    print("[narrative_cache] Regenerating narratives via Groq...")

    # Load signals from signal cache to derive narratives from
    try:
        from backend.services.signal_cache import get_cached_signals
        signals = await get_cached_signals()
    except Exception as e:
        print(f"[narrative_cache] Could not load signals: {e}")
        signals = []

    narratives = await _generate_narratives(signals)
    _save_cache(narratives)
    return narratives