"""
groq_llm.py — Transmission-Model Signal Generator

Architecture (hedge fund style):
  Headlines + GTI
      ↓
  Gate 1: GTI threshold check (0-25 = CASH, no signal)
      ↓
  Step 1: Event classifier (Groq call 1) — what archetype is this?
      ↓
  Step 2: Transmission router (hardcoded rules) — archetype → channel → candidate assets
      ↓
  Step 3: Signal generator (Groq call 2) — pick from constrained list, explain why
      ↓
  Output: real tradeable ticker + direction + CoT

LLM never invents assets. It only chooses from the pre-approved universe.
"""

import json
from backend.services.env_loader import get_groq_client

# ── Approved Asset Universe ───────────────────────────
ASSET_UNIVERSE = {
    # Commodities
    "GLD":  {"name": "SPDR Gold Shares",            "class": "Commodity",   "sensitivity": "safe_haven"},
    "SLV":  {"name": "iShares Silver Trust",         "class": "Commodity",   "sensitivity": "safe_haven"},
    "USO":  {"name": "United States Oil Fund",       "class": "Commodity",   "sensitivity": "energy"},
    "BNO":  {"name": "United States Brent Oil",      "class": "Commodity",   "sensitivity": "energy"},
    "DBA":  {"name": "Invesco DB Agriculture",       "class": "Commodity",   "sensitivity": "food_supply"},
    # Currencies
    "UUP":  {"name": "Invesco DB USD Bullish",       "class": "Currency",    "sensitivity": "safe_haven"},
    "FXF":  {"name": "CurrencyShares Swiss Franc",   "class": "Currency",    "sensitivity": "safe_haven"},
    "FXY":  {"name": "CurrencyShares Japanese Yen",  "class": "Currency",    "sensitivity": "safe_haven"},
    # Sovereign Debt
    "TLT":  {"name": "iShares 20Y Treasury Bond",    "class": "Bond",        "sensitivity": "safe_haven"},
    "EMB":  {"name": "iShares EM Bond USD",          "class": "Bond",        "sensitivity": "em_risk"},
    "VWOB": {"name": "Vanguard EM Govt Bond",        "class": "Bond",        "sensitivity": "em_risk"},
    # Defense / Rearmament
    "ITA":  {"name": "iShares US Aerospace & Defense","class": "Equity",     "sensitivity": "defense"},
    "XAR":  {"name": "SPDR S&P Aerospace & Defense", "class": "Equity",      "sensitivity": "defense"},
    # Defensive Equity
    "XLU":  {"name": "Utilities Select Sector SPDR", "class": "Equity",      "sensitivity": "defensive"},
    "XLP":  {"name": "Consumer Staples Select SPDR", "class": "Equity",      "sensitivity": "defensive"},
    "USMV": {"name": "iShares MSCI USA Min Vol",     "class": "Equity",      "sensitivity": "defensive"},
    # Energy Equity
    "XLE":  {"name": "Energy Select Sector SPDR",    "class": "Equity",      "sensitivity": "energy"},
    # Semiconductor / Tech
    "SMH":  {"name": "VanEck Semiconductor ETF",     "class": "Equity",      "sensitivity": "semiconductor"},
    "SOXX": {"name": "iShares Semiconductor ETF",    "class": "Equity",      "sensitivity": "semiconductor"},
    # Broad EM
    "EEM":  {"name": "iShares MSCI Emerging Markets","class": "Equity",      "sensitivity": "em_risk"},
    "VWO":  {"name": "Vanguard FTSE Emerging Mkts",  "class": "Equity",      "sensitivity": "em_risk"},
    # Developed Markets
    "EFA":  {"name": "iShares MSCI EAFE",            "class": "Equity",      "sensitivity": "developed_ex_us"},
    # Regional
    "EWG":  {"name": "iShares MSCI Germany",         "class": "Equity",      "sensitivity": "europe"},
    "EWU":  {"name": "iShares MSCI United Kingdom",  "class": "Equity",      "sensitivity": "europe"},
    "EWT":  {"name": "iShares MSCI Taiwan",          "class": "Equity",      "sensitivity": "taiwan"},
    "MCHI": {"name": "iShares MSCI China",           "class": "Equity",      "sensitivity": "china"},
    "INDA": {"name": "iShares MSCI India",           "class": "Equity",      "sensitivity": "india"},
    "KSA":  {"name": "iShares MSCI Saudi Arabia",    "class": "Equity",      "sensitivity": "middle_east"},
    # Broad
    "IVV":  {"name": "iShares Core S&P 500",         "class": "Equity",      "sensitivity": "broad_us"},
    "IWM":  {"name": "iShares Russell 2000",         "class": "Equity",      "sensitivity": "broad_us"},
}

# ── Transmission Channel Mapping ──────────────────────
# archetype → { channel, candidate_tickers, default_direction }
TRANSMISSION_MAP = {
    "middle_east_energy": {
        "channel":   "Energy supply chokepoint — Strait of Hormuz / regional oil infrastructure",
        "long":      ["USO", "BNO", "XLE", "GLD"],
        "short":     ["EEM", "EFA", "KSA"],
        "reasoning": "Middle East conflict threatens ~20M bbl/day through Strait of Hormuz. Oil supply deficit → crude spike. Capital flees EM equities.",
    },
    "asia_pacific_tech": {
        "channel":   "Semiconductor supply chain disruption — Taiwan Strait / South China Sea",
        "long":      ["GLD", "UUP", "FXY", "TLT"],
        "short":     ["SMH", "SOXX", "EWT", "MCHI"],
        "reasoning": "Taiwan/China tension threatens global chip supply. TSMC controls 92% of advanced node production. Tech sell-off + flight to safety.",
    },
    "em_instability": {
        "channel":   "Capital flight from emerging markets — sovereign risk premium spike",
        "long":      ["UUP", "GLD", "TLT", "IWM"],
        "short":     ["EEM", "VWO", "EMB", "VWOB"],
        "reasoning": "EM political crisis triggers capital flight. Dollar strengthens, EM bonds/equities sell off. Average EM equity drop 2.5-5% during international conflict.",
    },
    "global_systemic": {
        "channel":   "Systemic macro contagion — flight to safety across all risk assets",
        "long":      ["GLD", "TLT", "UUP", "FXF", "FXY", "USMV", "XLU", "XLP"],
        "short":     ["EEM", "VWO", "EFA", "EWG"],
        "reasoning": "Superpowers in direct conflict triggers uncertainty trinity. Gold + Treasuries + USD are only reliable diversifiers. All equities sell off.",
    },
    "military_buildup": {
        "channel":   "Structural defense spending increase — secular rearmament cycle",
        "long":      ["ITA", "XAR", "GLD"],
        "short":     ["EEM", "VWO"],
        "reasoning": "Prolonged military standoff drives structural defense budget increases. NATO targeting 5% GDP. Multi-decade BUY on aerospace and defense.",
    },
    "trade_war": {
        "channel":   "Supply chain fragmentation — tariff escalation and export restrictions",
        "long":      ["GLD", "UUP", "IWM", "XLP"],
        "short":     ["EWG", "MCHI", "SMH", "EFA"],
        "reasoning": "Trade war fragments supply chains. Exporter-heavy indices (Germany, China) sell off. US domestic small-caps relatively insulated.",
    },
    "food_agriculture": {
        "channel":   "Agricultural supply disruption — grain/food export blockade",
        "long":      ["DBA", "GLD"],
        "short":     ["EEM", "VWO"],
        "reasoning": "Black Sea or key agricultural region disruption spikes food commodity prices. EM food importers face inflation shock.",
    },
    "cyber_infrastructure": {
        "channel":   "Critical infrastructure attack — cybersecurity demand spike",
        "long":      ["ITA", "XAR", "GLD"],
        "short":     ["XLU", "EEM"],
        "reasoning": "State-sponsored cyber attack on infrastructure elevates defense/cybersecurity demand. Utilities vulnerable as attack vector.",
    },
}

# ── GTI Threshold Gates ────────────────────────────────────────────────────────
def _get_signal_gate(gti_score: float) -> dict:
    if gti_score <= 25:
        return {"allow": False, "tier": "CASH",   "confidence_cap": 0.0,  "label": "Below signal threshold"}
    if gti_score <= 50:
        return {"allow": True,  "tier": "WEAK",   "confidence_cap": 0.50, "label": "Watch — low confidence only"}
    if gti_score <= 70:
        return {"allow": True,  "tier": "SIGNAL", "confidence_cap": 0.75, "label": "Standard signal"}
    if gti_score <= 85:
        return {"allow": True,  "tier": "STRONG", "confidence_cap": 0.88, "label": "Strong signal"}
    return     {"allow": True,  "tier": "CRISIS", "confidence_cap": 0.95, "label": "Crisis signal"}


# ── Step 1: Event Classifier ───────────────────────────────────────────────────
CLASSIFIER_PROMPT = """You are a geopolitical event classifier. Classify the geopolitical situation into EXACTLY ONE archetype.

Available archetypes:
- middle_east_energy: Conflict near oil infrastructure, Strait of Hormuz, Iran, Iraq, Saudi Arabia, Yemen, Red Sea
- asia_pacific_tech: China-Taiwan tension, South China Sea, semiconductor supply chain risk
- em_instability: Political coup, hyperinflation, civil war, capital flight in emerging markets
- global_systemic: Direct conflict between major powers, nuclear threats, NATO involvement, systemic contagion
- military_buildup: Arms race, defense spending increases, prolonged standoff without active combat
- trade_war: Tariffs, sanctions, export bans, supply chain decoupling
- food_agriculture: Grain export blockade, agricultural supply disruption
- cyber_infrastructure: State-sponsored cyberattack, critical infrastructure breach

Return ONLY a JSON object with these fields:
{
  "archetype": "one of the archetypes above",
  "confidence": 0.0-1.0,
  "key_event": "one sentence describing the primary event"
}

No markdown, no backticks."""

async def _classify_event(headlines: list[dict], context: str) -> dict:
    headlines_text = "\n".join([f"- {h.get('title','')}" for h in headlines[:6]])
    prompt = f"Context: {context}\n\nHeadlines:\n{headlines_text}\n\nClassify this geopolitical situation."
    try:
        client = get_groq_client()
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": CLASSIFIER_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=200,
            temperature=0.1,
        )
        raw = r.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
        return json.loads(raw)
    except Exception as e:
        print(f"[groq_llm] Classifier error: {e}")
        # Fallback: detect from context keywords
        ctx = context.lower()
        if any(k in ctx for k in ["iran","iraq","saudi","yemen","hormuz","oil"]):
            return {"archetype": "middle_east_energy", "confidence": 0.7, "key_event": context}
        if any(k in ctx for k in ["taiwan","china","semiconductor","chip"]):
            return {"archetype": "asia_pacific_tech", "confidence": 0.7, "key_event": context}
        if any(k in ctx for k in ["russia","ukraine","nato"]):
            return {"archetype": "global_systemic", "confidence": 0.7, "key_event": context}
        return {"archetype": "em_instability", "confidence": 0.5, "key_event": context}


# ── Step 2: Signal Generator ───────────────────────────────────────────────────
def _build_signal_prompt(archetype: str, transmission: dict, gti_score: float, gate: dict, headlines: list[dict], key_event: str) -> str:
    ticker_list = json.dumps({
        t: ASSET_UNIVERSE[t]["name"]
        for t in (transmission["long"] + transmission["short"])
        if t in ASSET_UNIVERSE
    }, indent=2)
    headlines_text = "\n".join([f"- {h.get('title','')}" for h in headlines[:5]])

    return f"""You are a geopolitical macro trader generating a market signal.

SITUATION:
Event: {key_event}
GTI Score: {gti_score}/100 ({gate['tier']} tier — {gate['label']})
Transmission Channel: {transmission['channel']}
Channel Logic: {transmission['reasoning']}

HEADLINES:
{headlines_text}

ALLOWED TICKERS ONLY (you MUST choose from this list):
{ticker_list}

RULES:
1. Choose EXACTLY ONE ticker from the allowed list above
2. Direction: BUY or SELL only
3. Confidence: maximum {gate['confidence_cap']} (hard cap for this GTI tier)
4. Summary: one sentence, max 15 words
5. Reasoning: 2-3 sentences explaining the transmission mechanism

Return ONLY JSON:
{{
  "direction": "BUY" or "SELL",
  "asset": "full asset name",
  "ticker": "ticker symbol from allowed list",
  "confidence": number,
  "summary": "one sentence",
  "reasoning": "2-3 sentence chain of thought"
}}

No markdown, no backticks, no extra text."""


async def generate_signal(headlines: list[dict], context: str, gti_score: float) -> dict:
    """Main entry point — full transmission model pipeline."""

    # Gate 1: GTI threshold
    gate = _get_signal_gate(gti_score)
    if not gate["allow"]:
        return {
            "direction":  "NEUTRAL",
            "asset":      "Cash",
            "ticker":     "CASH",
            "confidence": 0.0,
            "summary":    f"GTI {gti_score} — below signal threshold. No tradeable event detected.",
            "reasoning":  "Low GTI scores indicate routine political friction already priced into markets. Generating signals here causes algorithmic churn without alpha.",
            "archetype":  "none",
            "channel":    "none",
        }

    if not headlines:
        return {
            "direction":  "NEUTRAL",
            "asset":      "Cash",
            "ticker":     "CASH",
            "confidence": 0.0,
            "summary":    "Insufficient intelligence data for signal generation.",
            "reasoning":  "No headlines available to analyze.",
            "archetype":  "none",
            "channel":    "none",
        }

    # Step 1: Classify event archetype
    classification = await _classify_event(headlines, context)
    archetype = classification.get("archetype", "em_instability")
    key_event = classification.get("key_event", context)

    # Step 2: Get transmission channel
    transmission = TRANSMISSION_MAP.get(archetype, TRANSMISSION_MAP["em_instability"])

    # Step 3: Generate constrained signal
    prompt = _build_signal_prompt(archetype, transmission, gti_score, gate, headlines, key_event)

    try:
        client = get_groq_client()
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.2,
        )
        raw = r.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
        result = json.loads(raw)

        # Enforce confidence cap
        result["confidence"] = min(float(result.get("confidence", 0.5)), gate["confidence_cap"])

        # Validate ticker is in approved universe — fallback if hallucinated
        if result.get("ticker") not in ASSET_UNIVERSE:
            fallback = transmission["long"][0]
            print(f"[groq_llm] Hallucinated ticker {result.get('ticker')} — falling back to {fallback}")
            result["ticker"] = fallback
            result["asset"]  = ASSET_UNIVERSE[fallback]["name"]

        result["archetype"] = archetype
        result["channel"]   = transmission["channel"]
        return result

    except Exception as e:
        print(f"[groq_llm] Signal generator error: {e}")
        fallback = transmission["long"][0]
        return {
            "direction":  "BUY",
            "asset":      ASSET_UNIVERSE[fallback]["name"],
            "ticker":     fallback,
            "confidence": min(0.55, gate["confidence_cap"]),
            "summary":    f"{key_event[:80]}",
            "reasoning":  transmission["reasoning"],
            "archetype":  archetype,
            "channel":    transmission["channel"],
        }