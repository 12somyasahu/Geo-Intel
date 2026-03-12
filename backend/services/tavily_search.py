import os
from tavily import TavilyClient

_client = None

def get_client():
    global _client
    if _client is None:
        _env_path = r'D:\downloads\Geo-Intel\backend\.env'
        with open(_env_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip()
        _client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    return _client

COUNTRY_SEARCH_QUERIES = {
    "RU": "Russia Ukraine war military conflict 2026",
    "UA": "Ukraine war frontline Zelensky 2026",
    "IR": "Iran war US Israel strikes military 2026",
    "IL": "Israel war Gaza Lebanon strikes 2026",
    "CN": "China Taiwan military PLA threat 2026",
    "TW": "Taiwan China strait military tension 2026",
    "KP": "North Korea missile nuclear Kim Jong Un 2026",
    "PS": "Palestine Gaza conflict humanitarian 2026",
    "SD": "Sudan civil war RSF conflict 2026",
    "YE": "Yemen Houthi US strikes Red Sea 2026",
    "SY": "Syria conflict instability 2026",
    "AF": "Afghanistan Taliban conflict 2026",
    "PK": "Pakistan military political conflict 2026",
    "IN": "India border tension China Pakistan 2026",
    "SA": "Saudi Arabia oil Iran war 2026",
    "IQ": "Iraq militia PMF US tension 2026",
    "LB": "Lebanon Hezbollah conflict 2026",
    "MM": "Myanmar junta civil war 2026",
    "TR": "Turkey military conflict Kurdish 2026",
    "VE": "Venezuela political crisis military 2026",
    "MX": "Mexico cartel violence security 2026",
    "ET": "Ethiopia conflict Tigray 2026",
    "LY": "Libya conflict factions war 2026",
    "SO": "Somalia Al-Shabaab conflict 2026",
    "ML": "Mali coup Sahel instability 2026",
    "US": "United States Iran war sanctions military 2026",
    "CN": "China trade war Taiwan military 2026",
}

async def fetch_country_intelligence(iso: str) -> list[dict]:
    query = COUNTRY_SEARCH_QUERIES.get(iso.upper(), f"{iso} conflict security risk 2026")
    try:
        client = get_client()
        results = client.search(
            query=query,
            search_depth="basic",
            max_results=8,
            include_answer=False,
        )
        articles = []
        for r in results.get("results", []):
            articles.append({
                "title":       r.get("title", ""),
                "url":         r.get("url", ""),
                "content":     r.get("content", "")[:300],
                "publishedAt": r.get("published_date", ""),
                "source":      r.get("url", "").split("/")[2] if r.get("url") else "",
            })
        return articles
    except Exception as e:
        print(f"Tavily error for {iso}: {e}")
        return []