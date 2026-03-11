import os
import re
import json
from groq import Groq

# Manual loader — bypasses dotenv BOM encoding issue on Windows
_env_path = r'D:\downloads\Geo-Intel\backend\.env'
with open(_env_path, 'r', encoding='utf-8-sig') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

print("GROQ KEY:", os.getenv("GROQ_API_KEY")[:8] if os.getenv("GROQ_API_KEY") else "NONE")

_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set in environment")
        _client = Groq(api_key=api_key)
    return _client

async def generate_signal(headlines: list[dict], country: str, gti_score: float) -> dict:
    if not headlines:
        return {
            "direction": "NEUTRAL",
            "asset": "N/A",
            "confidence": 0.5,
            "summary": "No headlines available.",
            "reasoning": "Insufficient data to generate a signal."
        }

    titles = "\n".join([f"- {h['title']}" for h in headlines[:6]])

    prompt = f"""You are a senior geopolitical market analyst at a hedge fund.

Country/Region: {country}
GTI Risk Score: {gti_score}/100
Recent headlines (last 24h):
{titles}

Respond ONLY with a single valid JSON object. No markdown, no code fences, no newlines inside string values, no apostrophes or quotes inside string values:
{{"direction":"BUY or SELL or NEUTRAL","asset":"most affected asset e.g. WTI Crude","confidence":0.75,"summary":"one sentence signal explanation","reasoning":"two sentences explaining trigger and market impact"}}"""

    try:
        response = get_client().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.2,
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        text = re.sub(r'[\x00-\x1f\x7f]', ' ', text)
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Groq JSON parse error: {e} | raw: {text}")
        return {
            "direction": "NEUTRAL",
            "asset": "N/A",
            "confidence": 0.5,
            "summary": "Signal parse failed.",
            "reasoning": str(e)
        }
    except Exception as e:
        print(f"Groq error: {e}")
        return {
            "direction": "NEUTRAL",
            "asset": "N/A",
            "confidence": 0.5,
            "summary": "LLM unavailable.",
            "reasoning": str(e)
        }
