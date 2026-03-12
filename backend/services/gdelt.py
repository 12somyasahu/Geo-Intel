import httpx
import os

GNEWS_URL = "https://gnews.io/api/v4/search"

COUNTRY_QUERIES = {
    "RU": "Russia military Ukraine Kremlin Putin",
    "UA": "Ukraine Zelensky Kyiv war frontline",
    "IL": "Israel IDF Gaza Netanyahu strike",
    "IR": "Iran IRGC nuclear Khamenei sanctions",
    "CN": "China Xi Jinping PLA Taiwan Beijing",
    "TW": "Taiwan strait PLA military Taipei",
    "KP": "North Korea Kim Jong Un missile ICBM",
    "SY": "Syria Assad Damascus conflict",
    "YE": "Yemen Houthi Ansarallah Red Sea",
    "MM": "Myanmar junta Tatmadaw coup Naypyidaw",
    "SA": "Saudi Arabia MBS OPEC Riyadh oil",
    "IN": "India Modi BJP border China Pakistan",
    "PK": "Pakistan ISI military Islamabad conflict",
    "US": "United States Congress White House sanctions policy",
    "AF": "Afghanistan Taliban Kabul",
    "IQ": "Iraq militia Baghdad PMF",
    "KR": "South Korea Seoul North Korea DMZ",
    "JP": "Japan defense SDF China Sea Tokyo",
    "GB": "United Kingdom London NATO defense",
    "DE": "Germany Bundeswehr NATO Berlin defense",
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
            
            # Deduplicate by title
            seen_titles = set()
            unique = []
            for a in articles:
                title = a.get("title", "")
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    unique.append({
                        "title": title,
                        "url": a.get("url", ""),
                        "publishedAt": a.get("publishedAt", ""),
                        "source": a.get("source", {}).get("name", ""),
                    })
            return unique
        except Exception as e:
            print(f"GNews error for {iso}: {e}")
            return []
        