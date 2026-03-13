from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.tavily_search import fetch_country_intelligence
from backend.services.scorer import score_headlines, score_to_level, DEFAULT_SCENARIO
from backend.services.groq_llm import generate_signal
from backend.services.gti_cache import get_cached_gti

router = APIRouter()

class ScenarioWeights(BaseModel):
    energy_weight:   float = 1.0
    conflict_weight: float = 1.0
    trade_weight:    float = 1.0
    cyber_weight:    float = 1.0
    monetary_weight: float = 1.0


async def _get_gti_score(iso: str) -> tuple[float, str]:
    """Get GTI score from cache first, fresh calculation as fallback."""
    try:
        countries = await get_cached_gti()
        for c in countries:
            if c["iso"] == iso:
                return c["score"], c["level"]
    except Exception as e:
        print(f"[analyze] Cache lookup failed for {iso}: {e}")
    return None, None


@router.get("/analyze/{iso}")
async def analyze_country(iso: str):
    iso = iso.upper()
    headlines = await fetch_country_intelligence(iso)

    # Use cached GTI score (properly scored with VADER + floors)
    cached_score, cached_level = await _get_gti_score(iso)

    if cached_score is not None:
        score, level = cached_score, cached_level
        _, breakdown = score_headlines(headlines)  # breakdown only
    else:
        # Fallback: fresh calculation
        score, breakdown = score_headlines(headlines)
        level = score_to_level(score)

    _, breakdown = score_headlines(headlines)
    signal = await generate_signal(headlines, iso, score)

    return {
        "iso":       iso,
        "gti":       {"score": score, "level": level},
        "breakdown": breakdown,
        "headlines": headlines,
        "signal":    signal,
        "scenario":  DEFAULT_SCENARIO,
        "source":    "tavily",
    }


@router.post("/analyze/{iso}/scenario")
async def analyze_country_scenario(iso: str, weights: ScenarioWeights):
    iso = iso.upper()
    scenario = weights.model_dump()
    headlines = await fetch_country_intelligence(iso)

    # Use cached baseline GTI, then apply scenario multiplier on top
    cached_score, _ = await _get_gti_score(iso)
    baseline_score = cached_score if cached_score is not None else 0.0

    score, breakdown = score_headlines(headlines, scenario=scenario)

    # Blend: scenario adjusts on top of authoritative cached baseline
    scenario_multiplier = (
        scenario.get("conflict_weight", 1.0) * 0.4 +
        scenario.get("energy_weight",   1.0) * 0.2 +
        scenario.get("trade_weight",    1.0) * 0.15 +
        scenario.get("cyber_weight",    1.0) * 0.1 +
        scenario.get("monetary_weight", 1.0) * 0.15
    )
    adjusted_score = round(min(100.0, baseline_score * scenario_multiplier), 1)
    level = score_to_level(adjusted_score)

    active_sliders = [
        k.replace("_weight", "").upper()
        for k, v in scenario.items() if v > 1.2
    ]
    scenario_context = f"[SCENARIO: {', '.join(active_sliders)} amplified]" if active_sliders else ""
    signal = await generate_signal(headlines, f"{iso} {scenario_context}", adjusted_score)

    return {
        "iso":          iso,
        "gti":          {"score": adjusted_score, "level": level},
        "baseline_gti": {"score": baseline_score, "level": score_to_level(baseline_score)},
        "delta":        round(adjusted_score - baseline_score, 1),
        "breakdown":    breakdown,
        "headlines":    headlines,
        "signal":       signal,
        "scenario":     scenario,
        "source":       "tavily",
    }