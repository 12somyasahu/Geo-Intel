import httpx

GDELT_BASE = "https://api.gdeltproject.org/api/v2/doc/doc"

async def fetch_gdelt_events(query: str, limit: int = 10) -> list[dict]:
    """Fetch recent GDELT news events for a query term."""
    params = {
        "query": query,
        "mode": "artlist",
        "maxrecords": limit,
        "format": "json",
        "timespan": "24h",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.get(GDELT_BASE, params=params)
            data = r.json()
            return data.get("articles", [])
        except Exception as e:
            print(f"GDELT fetch error: {e}")
            return []