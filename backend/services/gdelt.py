import httpx
import os

GNEWS_URL = "https://gnews.io/api/v4/search"

COUNTRY_QUERIES = {
    "RU": "Russia Ukraine war military",
    "UA": "Ukraine war conflict attack",
    "IL": "Israel Gaza war strike",
    "IR": "Iran nuclear sanctions missile",
    "CN": "China Taiwan military threat",
    "TW": "Taiwan China strait tension",
    "KP": "North Korea missile nuclear",
    "SY": "Syria conflict attack",
    "YE": "Yemen Houthi attack shipping",
    "MM": "Myanmar military coup",
    "SA": "Saudi Arabia OPEC oil",
    "IN": "India Pakistan border tension",
    "PK": "Pakistan military conflict",
    "US": "United States sanctions tariff policy",
}

async def fetch_country_headlines(iso: str, limit: int = 10) -> list[dict]:
    query = COUNTRY_QUERIES.get(iso.upper(), iso)
    params = {
        "q": query,
        "lang": "en",
        "max": min(limit, 10),
        "apikey": os.getenv("GNEWS_API_KEY"),
    }
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(GNEWS_URL, params=params)
            data = r.json()
            articles = data.get("articles", [])
            return [
                {
                    "title": a.get("title", ""),
                    "url":   a.get("url", ""),
                    "publishedAt": a.get("publishedAt", ""),
                    "source": a.get("source", {}).get("name", ""),
                }
                for a in articles if a.get("title")
            ]
        except Exception as e:
            print(f"GNews error for {iso}: {e}")
            return []