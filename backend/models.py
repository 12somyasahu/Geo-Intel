from pydantic import BaseModel
from typing import Optional

class Signal(BaseModel):
    id: str
    asset: str
    ticker: str
    direction: str        # BUY | SELL
    confidence: float
    summary: str
    reasoning: Optional[str] = None
    cluster: str
    region: str
    timestamp: str

class GTIScore(BaseModel):
    iso: str
    score: float
    level: str            # CRITICAL | HIGH | MEDIUM | LOW | MINIMAL
    label: str

class Narrative(BaseModel):
    id: str
    title: str
    summary: str
    strength: float
    regions: list[str]
    assets: list[str]

class TickerEvent(BaseModel):
    id: str
    text: str
    region: str
    severity: str
    timestamp: str