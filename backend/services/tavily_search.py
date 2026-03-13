from backend.services.env_loader import get_tavily_client

COUNTRY_SEARCH_QUERIES = {
    "RU": "Russia Ukraine war military conflict 2026",
    "UA": "Ukraine war frontline offensive defense 2026",
    "IR": "Iran US Israel war strikes military 2026",
    "IL": "Israel war Gaza Lebanon Iran strikes 2026",
    "CN": "China Taiwan military PLA threat trade war 2026",
    "TW": "Taiwan China strait military tension 2026",
    "KP": "North Korea missile nuclear Kim Jong Un 2026",
    "PS": "Palestine Gaza conflict humanitarian 2026",
    "SD": "Sudan civil war RSF conflict 2026",
    "YE": "Yemen Houthi US strikes Red Sea 2026",
    "SY": "Syria conflict instability post-Assad 2026",
    "AF": "Afghanistan Taliban conflict 2026",
    "PK": "Pakistan military political conflict 2026",
    "IN": "India border tension China Pakistan 2026",
    "SA": "Saudi Arabia oil Iran war security 2026",
    "IQ": "Iraq militia PMF US tension 2026",
    "LB": "Lebanon Hezbollah conflict reconstruction 2026",
    "MM": "Myanmar junta civil war resistance 2026",
    "TR": "Turkey military conflict Kurdish Syria 2026",
    "VE": "Venezuela political crisis military 2026",
    "MX": "Mexico cartel violence security 2026",
    "ET": "Ethiopia conflict Tigray 2026",
    "LY": "Libya conflict factions war 2026",
    "SO": "Somalia Al-Shabaab conflict 2026",
    "ML": "Mali coup Sahel instability 2026",
    "US": "United States Iran war sanctions military 2026",
    "NG": "Nigeria security conflict Boko Haram 2026",
    "EG": "Egypt security stability Iran war 2026",
}

async def fetch_country_intelligence(iso: str) -> list[dict]:
    query = COUNTRY_SEARCH_QUERIES.get(iso.upper(), f"{iso} conflict security risk geopolitical 2026")
    try:
        client = get_tavily_client()
        results = client.search(
            query=query,
            search_depth="basic",
            max_results=8,
            include_answer=False,
        )
        articles = []
        for r in results.get("results", []):
            url = r.get("url", "")
            # Filter social/video platforms
            if any(blocked in url for blocked in ["youtube.com", "facebook.com", "twitter.com", "reddit.com", "tiktok.com"]):
                continue
            articles.append({
                "title":       r.get("title", ""),
                "url":         url,
                "content":     r.get("content", "")[:300],
                "publishedAt": r.get("published_date", ""),
                "source":      url.split("/")[2] if url else "",
            })
        return articles
    except Exception as e:
        print(f"[tavily_search] Error for {iso}: {e}")
        return []