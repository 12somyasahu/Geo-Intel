import re

# Keywords grouped by category — maps to What-If slider weights
KEYWORD_CATEGORIES = {
    "conflict": [
    ("attack", 8), ("strike", 7), ("missile", 9), ("bomb", 9),
    ("war", 8), ("conflict", 6), ("kill", 8), ("casualt", 8),
    ("invasion", 10), ("coup", 8), ("troop", 5), ("military", 4),
    ("weapon", 6), ("siege", 8), ("blockade", 7), ("assassin", 9),
    ("terror", 8), ("explo", 8), ("airstrike", 9), ("offensiv", 7),
    ("escalat", 7), ("crisis", 6), ("threat", 5), ("tension", 4),
    ("sanction", 5), ("nuclear", 9),
],
    "energy": [
        ("oil", 5), ("pipeline", 6), ("opec", 5), ("crude", 5),
        ("gas", 4), ("energy", 4), ("fuel", 4), ("refinery", 6),
        ("petroleum", 5), ("lng", 6), ("tanker", 6), ("drilling", 4),
    ],
    "trade": [
        ("sanctions", 6), ("tariff", 5), ("embargo", 7), ("export", 3),
        ("import", 3), ("supply chain", 5), ("trade war", 7),
        ("restriction", 4), ("ban", 4), ("blockade", 6),
    ],
    "cyber": [
        ("cyber", 7), ("hack", 7), ("ransomware", 8), ("malware", 8),
        ("infrastructure attack", 9), ("data breach", 6), ("espionage", 7),
        ("surveillance", 5), ("disinformation", 5),
    ],
    "monetary": [
        ("nuclear", 10), ("sanctions", 5), ("currency", 4), ("inflation", 3),
        ("rate hike", 4), ("default", 6), ("debt", 3), ("devaluation", 6),
        ("central bank", 3), ("forex", 4), ("reserve", 3),
    ],
}

PEACE_KEYWORDS = [
    ("ceasefire", -6), ("peace", -5), ("deal", -3), ("agreement", -3),
    ("diplomacy", -4), ("talks", -2), ("withdraw", -3), ("accord", -4),
    ("truce", -6), ("negotiat", -4), ("reconcil", -5),
]

DEFAULT_SCENARIO = {
    "energy_weight":   1.0,
    "conflict_weight": 1.0,
    "trade_weight":    1.0,
    "cyber_weight":    1.0,
    "monetary_weight": 1.0,
}

CATEGORY_TO_WEIGHT = {
    "conflict": "conflict_weight",
    "energy":   "energy_weight",
    "trade":    "trade_weight",
    "cyber":    "cyber_weight",
    "monetary": "monetary_weight",
}

def score_headlines(
    headlines: list[dict],
    base_score: float = 30.0,
    scenario: dict = None
) -> tuple[float, dict]:
    """
    Returns (final_score, breakdown) where breakdown shows contribution per category.
    Scenario weights amplify or dampen each category's contribution.
    """
    if scenario is None:
        scenario = DEFAULT_SCENARIO

    if not headlines:
        return base_score, {}

    category_totals = {cat: 0.0 for cat in KEYWORD_CATEGORIES}
    peace_total = 0.0

    for article in headlines:
        text = (article.get("title", "") + " " + article.get("url", "")).lower()

        for category, keywords in KEYWORD_CATEGORIES.items():
            for kw, weight in keywords:
                if kw in text:
                    category_totals[category] += weight

        for kw, weight in PEACE_KEYWORDS:
            if kw in text:
                peace_total += weight  # already negative

    # Apply scenario weights per category
    weighted_total = 0.0
    breakdown = {}
    for category, total in category_totals.items():
        weight_key = CATEGORY_TO_WEIGHT[category]
        multiplier = scenario.get(weight_key, 1.0)
        weighted = total * multiplier
        weighted_total += weighted
        breakdown[category] = round(weighted / len(headlines), 2)

    # Add peace dampening (not amplified by sliders)
    weighted_total += peace_total

    avg = weighted_total / len(headlines)
    final = round(min(max(base_score + avg, 0), 100), 1)

    return final, breakdown


def score_to_level(score: float) -> str:
    if score >= 80: return "CRITICAL"
    if score >= 60: return "HIGH"
    if score >= 40: return "MEDIUM"
    if score >= 20: return "LOW"
    return "MINIMAL"