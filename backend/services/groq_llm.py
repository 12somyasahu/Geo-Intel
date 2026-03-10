import os
from groq import Groq

client = None

def get_client():
    global client
    if client is None:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return client

async def generate_signal(articles: list[dict], country: str) -> str:
    """Generate a market signal from GDELT articles using Groq."""
    headlines = "\n".join([a.get("title", "") for a in articles[:5]])
    prompt = f"""You are a geopolitical market analyst.
Based on these recent headlines about {country}:
{headlines}

Generate a concise market signal (1-2 sentences) explaining:
1. The geopolitical trigger
2. The likely market impact and direction

Be specific and data-driven."""

    response = get_client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
    )
    return response.choices[0].message.content