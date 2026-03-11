from fastapi import APIRouter
from backend.services.gdelt import fetch_country_headlines
from backend.services.scorer import score_headlines, score_to_level
from backend.services.groq_llm import generate_signal

router = APIRouter()

@router.get("/analyze/{iso}")
async def analyze_country(iso: str):
    iso = iso.upper()
    headlines = await fetch_country_headlines(iso)
    score = score_headlines(headlines)
    level = score_to_level(score)
    signal = await generate_signal(headlines, iso, score)

    return {
        "iso": iso,
        "gti": {"score": score, "level": level},
        "headlines": headlines,
        "signal": signal,
    }