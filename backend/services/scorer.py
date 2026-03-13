"""
scorer.py — Advanced GTI Scoring Engine

Pipeline per article:
  1. VADER sentiment intensity (negative compound score)
  2. Event verb detection (strike/attack/missile vs generic mentions)
  3. Source credibility weighting (Reuters=1.0, Wikipedia=0.0)
  4. Recency weighting (today=2.0x, this week=1.0x)
  5. Named entity density (country-specific relevance multiplier)
  6. Weighted sum → normalized 0-100 GTI score

Formula:
  GTI = (vader_score * 0.35) + (event_score * 0.30) + 
        (source_score * 0.15) + (recency_score * 0.10) + 
        (entity_score * 0.10)
  Normalized to 0-100
"""

import re
from datetime import datetime, timezone, timedelta

# ── VADER ─────────────────────────────────────────────────────────────────────
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _vader = SentimentIntensityAnalyzer()

    # Augment VADER lexicon with high-intensity geopolitical terms
    GEOPOLITICAL_LEXICON = {
        "airstrike": -3.5, "airstrikes": -3.5, "missile": -3.2, "missiles": -3.2,
        "ballistic": -3.0, "drone strike": -3.5, "bombardment": -3.8,
        "shelling": -3.2, "artillery": -2.8, "frontline": -2.5,
        "casualties": -3.0, "killed": -3.5, "massacre": -4.0,
        "offensive": -2.8, "invasion": -3.8, "occupation": -2.5,
        "nuclear": -3.5, "warhead": -3.8, "detonation": -4.0,
        "genocide": -4.0, "ethnic cleansing": -4.0, "war crime": -3.8,
        "ceasefire": 1.5, "peace talks": 2.0, "diplomatic": 1.2,
        "sanctions": -2.5, "embargo": -2.2, "blockade": -2.8,
        "coup": -3.2, "crackdown": -2.8, "martial law": -3.0,
        "famine": -3.5, "humanitarian crisis": -3.2, "displacement": -2.5,
        "IRGC": -2.5, "Hamas": -2.5, "Hezbollah": -2.5, "ISIS": -3.5,
        "Wagner": -2.8, "militia": -2.2, "insurgent": -2.5,
    }
    _vader.lexicon.update(GEOPOLITICAL_LEXICON)
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("[scorer] WARNING: vaderSentiment not installed — using fallback scoring")

# ── spaCy NER ─────────────────────────────────────────────────────────────────
try:
    import spacy
    _nlp = spacy.load("en_core_web_sm", disable=["parser", "tagger"])
    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False
    print("[scorer] WARNING: spaCy not available — entity density disabled")

# ── Event Detection ───────────────────────────────────────────────────────────
EVENT_VERBS = [
    "attack", "attacked", "strike", "struck", "strikes", "hit", "hits",
    "bombed", "bombing", "shelled", "shelling", "invaded", "invasion",
    "launched", "fired", "firing", "killed", "killed", "clash", "clashed",
    "offensive", "advance", "capture", "captured", "seized", "seize",
    "drone", "missile", "airstrike", "airstrikes", "bombardment",
    "detonated", "explosion", "exploded", "ambush", "ambushed",
    "coup", "crackdown", "massacre", "assassinated", "assassination",
]

WEAPON_TERMS = [
    "missile", "missiles", "drone", "drones", "airstrike", "airstrikes",
    "artillery", "rocket", "rockets", "bomb", "bombs", "warhead",
    "ballistic", "cruise missile", "ICBM", "nuclear", "chemical weapon",
    "tank", "gunfire", "sniper", "mortar", "rpg",
]

DEESCALATION_TERMS = [
    "ceasefire", "peace talks", "negotiations", "diplomatic", "withdraw",
    "withdrawal", "truce", "agreement", "deal", "normalization",
]

# ── Source Credibility ────────────────────────────────────────────────────────
SOURCE_WEIGHTS = {
    # Tier 1 — breaking news wire services (1.0)
    "reuters.com": 1.0, "apnews.com": 1.0, "bbc.com": 0.95, "bbc.co.uk": 0.95,
    "aljazeera.com": 0.95, "france24.com": 0.90,
    # Tier 2 — major news outlets (0.85)
    "theguardian.com": 0.85, "nytimes.com": 0.85, "wsj.com": 0.85,
    "washingtonpost.com": 0.85, "ft.com": 0.85, "bloomberg.com": 0.85,
    "cnn.com": 0.80, "nbcnews.com": 0.80, "abcnews.go.com": 0.80,
    "cbsnews.com": 0.80, "politico.com": 0.80, "axios.com": 0.80,
    # Tier 3 — regional / specialized (0.70)
    "haaretz.com": 0.75, "timesofisrael.com": 0.75, "jpost.com": 0.70,
    "dawn.com": 0.70, "thehindu.com": 0.70, "arabNews.com": 0.70,
    "kyivpost.com": 0.75, "pravda.com.ua": 0.70,
    "understandingwar.org": 0.85, "crisisgroup.org": 0.85,
    "cfr.org": 0.80, "csis.org": 0.80, "atlanticcouncil.org": 0.75,
    "pbs.org": 0.75, "npr.org": 0.75, "dw.com": 0.80,
    "euronews.com": 0.75, "middleeasteye.net": 0.70,
    "russiamatters.org": 0.70, "defensenews.com": 0.80,
    "militarytimes.com": 0.75, "janes.com": 0.85,
    # Tier 4 — low credibility / noise (0.2)
    "wikipedia.org": 0.0,   # zero — pure noise for live scoring
    "youtube.com": 0.0,
    "facebook.com": 0.0,
    "reddit.com": 0.0,
    "twitter.com": 0.0,
    "x.com": 0.0,
}
DEFAULT_SOURCE_WEIGHT = 0.50  # unknown sources


def _get_source_weight(source: str) -> float:
    if not source:
        return DEFAULT_SOURCE_WEIGHT
    source = source.lower().replace("www.", "")
    for domain, weight in SOURCE_WEIGHTS.items():
        if domain in source:
            return weight
    return DEFAULT_SOURCE_WEIGHT


# ── Recency Weighting ─────────────────────────────────────────────────────────
def _get_recency_weight(published_at: str) -> float:
    if not published_at:
        return 1.0  # unknown date — neutral
    try:
        # Try parsing ISO format
        pub = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        age_hours = (now - pub).total_seconds() / 3600
        if age_hours <= 12:   return 2.0
        if age_hours <= 24:   return 1.7
        if age_hours <= 48:   return 1.4
        if age_hours <= 168:  return 1.0   # 1 week
        return 0.7  # older than a week
    except Exception:
        return 1.0


# ── VADER Scoring ─────────────────────────────────────────────────────────────
def _vader_score(text: str) -> float:
    """Returns 0-1 conflict intensity from VADER compound score."""
    if not VADER_AVAILABLE or not text:
        return _fallback_sentiment(text)
    scores = _vader.polarity_scores(text)
    # Negative compound → conflict intensity
    # compound ranges -1 to 1; we want 0-1 conflict score
    neg_intensity = max(0.0, -scores["compound"])
    # Also use raw negative score for amplification
    raw_neg = scores["neg"]
    return min(1.0, (neg_intensity * 0.7) + (raw_neg * 0.3))


def _fallback_sentiment(text: str) -> float:
    """Simple keyword fallback when VADER unavailable."""
    if not text:
        return 0.0
    text_lower = text.lower()
    hits = sum(1 for term in EVENT_VERBS + WEAPON_TERMS if term in text_lower)
    return min(1.0, hits * 0.15)


# ── Event Score ───────────────────────────────────────────────────────────────
def _event_score(text: str) -> float:
    """Returns 0-1 event intensity based on verb + weapon detection."""
    if not text:
        return 0.0
    text_lower = text.lower()

    verb_hits   = sum(1 for v in EVENT_VERBS   if v in text_lower)
    weapon_hits = sum(1 for w in WEAPON_TERMS  if w in text_lower)
    deesc_hits  = sum(1 for d in DEESCALATION_TERMS if d in text_lower)

    # Deescalation reduces score
    raw = (verb_hits * 0.15) + (weapon_hits * 0.20) - (deesc_hits * 0.30)
    return max(0.0, min(1.0, raw))


# ── Entity Density ────────────────────────────────────────────────────────────
def _entity_density(text: str, country_label: str = "") -> float:
    """Returns 0-1 relevance score based on geopolitical entity density."""
    if not SPACY_AVAILABLE or not text:
        # Fallback: check if country name appears in text
        if country_label and country_label.lower() in text.lower():
            return 0.6
        return 0.4

    doc = _nlp(text[:500])  # cap for speed
    geo_entities = [ent for ent in doc.ents if ent.label_ in ("GPE", "ORG", "NORP", "FAC")]
    density = min(1.0, len(geo_entities) * 0.15)

    # Boost if target country is mentioned
    if country_label and country_label.lower() in text.lower():
        density = min(1.0, density + 0.3)

    return density


# ── Main Scorer ───────────────────────────────────────────────────────────────
DEFAULT_SCENARIO = {
    "energy_weight":   1.0,
    "conflict_weight": 1.0,
    "trade_weight":    1.0,
    "cyber_weight":    1.0,
    "monetary_weight": 1.0,
}

CATEGORY_KEYWORDS = {
    "conflict":  ["war", "attack", "strike", "missile", "bomb", "kill", "battle", "frontline", "offensive", "invasion", "airstrike", "artillery", "drone", "casualties", "shoot", "clash", "coup"],
    "energy":    ["oil", "gas", "pipeline", "opec", "energy", "crude", "fuel", "lng", "refinery", "petroleum", "nuclear plant", "power grid"],
    "trade":     ["sanction", "tariff", "embargo", "export ban", "import", "blockade", "trade war", "restriction", "seized"],
    "cyber":     ["hack", "cyberattack", "ransomware", "espionage", "breach", "malware", "cyber", "intelligence", "surveillance"],
    "monetary":  ["currency", "inflation", "default", "collapse", "devaluation", "central bank", "reserves", "bond", "financial crisis"],
}

def score_headlines(
    headlines: list[dict],
    scenario: dict = None,
    country_label: str = "",
) -> tuple[float, dict]:
    """
    Score a list of headlines into a GTI score 0-100.
    Returns (score, breakdown_dict).
    """
    if scenario is None:
        scenario = DEFAULT_SCENARIO

    if not headlines:
        return 0.0, {k: 0.0 for k in CATEGORY_KEYWORDS}

    article_scores = []

    for h in headlines:
        title       = h.get("title", "")
        content     = h.get("content", "")
        source      = h.get("source", "")
        published   = h.get("publishedAt", "")
        full_text   = f"{title} {content}"

        # Skip zero-weight sources entirely
        src_weight = _get_source_weight(source)
        if src_weight == 0.0:
            continue

        vader    = _vader_score(full_text)
        event    = _event_score(full_text)
        recency  = _get_recency_weight(published)
        entity   = _entity_density(full_text, country_label)

        # Composite article score (0-1)
        raw = (
            vader   * 0.35 +
            event   * 0.30 +
            src_weight * 0.15 +
            (recency / 2.0) * 0.10 +   # normalize recency 0-1
            entity  * 0.10
        )

        # Apply recency multiplier to final score
        article_scores.append(raw * recency * src_weight)

    if not article_scores:
        return 0.0, {k: 0.0 for k in CATEGORY_KEYWORDS}

    # Average article scores, boosted by article count (more events = higher score)
    base = sum(article_scores) / len(article_scores)
    volume_boost = min(1.5, 1.0 + (len(article_scores) - 1) * 0.05)
    normalized = min(1.0, base * volume_boost)

    # ── Category breakdown (for scenario sliders) ──────────────────────────
    breakdown = {}
    all_text = " ".join(h.get("title", "") + " " + h.get("content", "") for h in headlines).lower()

    for cat, keywords in CATEGORY_KEYWORDS.items():
        hits = sum(all_text.count(kw) for kw in keywords)
        weight_key = f"{cat}_weight"
        multiplier = scenario.get(weight_key, 1.0)
        breakdown[cat] = round(hits * multiplier, 1)

    # Apply scenario weights to final score
    scenario_multiplier = (
        scenario.get("conflict_weight", 1.0) * 0.4 +
        scenario.get("energy_weight",   1.0) * 0.2 +
        scenario.get("trade_weight",    1.0) * 0.15 +
        scenario.get("cyber_weight",    1.0) * 0.1 +
        scenario.get("monetary_weight", 1.0) * 0.15
    )

    final_score = normalized * 100 * scenario_multiplier
    return round(min(100.0, final_score), 1), breakdown


def score_to_level(score: float) -> str:
    if score >= 75: return "CRITICAL"
    if score >= 50: return "HIGH"
    if score >= 25: return "MEDIUM"
    return "LOW"