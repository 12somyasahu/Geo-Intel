from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.gdelt import fetch_country_headlines
from backend.services.scorer import score_headlines, score_to_level, DEFAULT_SCENARIO
from backend.services.groq_llm import generate_signal

router = APIRouter()

class ScenarioWeights(BaseModel):
    energy_weight:   float = 1.0
    conflict_weight: float = 1.0
    trade_weight:    float = 1.0
    cyber_weight:    float = 1.0
    monetary_weight: float = 1.0

@router.get("/analyze/{iso}")
async def analyze_country(iso: str):
    """Standard analysis with default weights."""
    iso = iso.upper()
    headlines = await fetch_country_headlines(iso)
    score, breakdown = score_headlines(headlines)
    level = score_to_level(score)
    signal = await generate_signal(headlines, iso, score)

    return {
        "iso": iso,
        "gti": {"score": score, "level": level},
        "breakdown": breakdown,
        "headlines": headlines,
        "signal": signal,
        "scenario": DEFAULT_SCENARIO,
    }

@router.post("/analyze/{iso}/scenario")
async def analyze_country_scenario(iso: str, weights: ScenarioWeights):
    """What-If analysis — applies slider weights to scoring formula."""
    iso = iso.upper()
    scenario = weights.model_dump()
    headlines = await fetch_country_headlines(iso)
    score, breakdown = score_headlines(headlines, scenario=scenario)
    level = score_to_level(score)

    # Add scenario context to Groq prompt
    active_sliders = [
        k.replace("_weight", "").upper()
        for k, v in scenario.items() if v > 1.2
    ]
    scenario_context = f"[SCENARIO: {', '.join(active_sliders)} amplified]" if active_sliders else ""
    signal = await generate_signal(headlines, f"{iso} {scenario_context}", score)

    # Baseline for delta comparison
    baseline_score, _ = score_headlines(headlines)

    return {
        "iso": iso,
        "gti": {"score": score, "level": level},
        "baseline_gti": {"score": baseline_score, "level": score_to_level(baseline_score)},
        "delta": round(score - baseline_score, 1),
        "breakdown": breakdown,
        "headlines": headlines,
        "signal": signal,
        "scenario": scenario,
    }