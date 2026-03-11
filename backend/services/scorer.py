import re

# Negative/positive keyword weights for quick GTI scoring
NEGATIVE_KEYWORDS = [
    ("attack", 8), ("strike", 7), ("missile", 9), ("bomb", 9),
    ("war", 8), ("conflict", 6), ("killed", 8), ("casualties", 8),
    ("nuclear", 10), ("invasion", 10), ("coup", 8), ("sanctions", 5),
    ("threat", 5), ("tension", 4), ("escalat", 7), ("crisis", 6),
    ("troops", 5), ("military", 4), ("weapon", 6), ("siege", 8),
    ("blockade", 7), ("assassin", 9), ("terror", 8), ("explosion", 8),
]

POSITIVE_KEYWORDS = [
    ("ceasefire", -6), ("peace", -5), ("deal", -3), ("agreement", -3),
    ("diplomacy", -4), ("talks", -2), ("withdraw", -3), ("accord", -4),
]

def score_headlines(headlines: list[dict], base_score: float = 30.0) -> float:
    if not headlines:
        return base_score

    total = 0.0
    for article in headlines:
        text = (article.get("title", "") + " " + article.get("url", "")).lower()
        article_score = 0.0
        for kw, weight in NEGATIVE_KEYWORDS:
            if kw in text:
                article_score += weight
        for kw, weight in POSITIVE_KEYWORDS:
            if kw in text:
                article_score += weight  # weight is already negative
        total += article_score

    # Normalize: avg score per article, scale to 0-100
    avg = total / len(headlines)
    raw = base_score + avg
    return round(min(max(raw, 0), 100), 1)

def score_to_level(score: float) -> str:
    if score >= 80: return "CRITICAL"
    if score >= 60: return "HIGH"
    if score >= 40: return "MEDIUM"
    if score >= 20: return "LOW"
    return "MINIMAL"