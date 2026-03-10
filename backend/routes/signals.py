from fastapi import APIRouter
from backend.models import Signal
from datetime import datetime

router = APIRouter()

MOCK_SIGNALS = [
    Signal(
        id="sig_001", asset="WTI Crude", ticker="WTI",
        direction="BUY", confidence=0.87,
        summary="Russia-Ukraine pipeline disruption tightening supply",
        cluster="Energy Supply Squeeze", region="EUROPE",
        timestamp=datetime.utcnow().isoformat()
    ),
    Signal(
        id="sig_002", asset="Gold", ticker="XAUUSD",
        direction="BUY", confidence=0.81,
        summary="Multi-front escalation driving safe haven demand",
        cluster="Middle East Escalation Arc", region="MIDDLE EAST",
        timestamp=datetime.utcnow().isoformat()
    ),
    Signal(
        id="sig_003", asset="USD/CNH", ticker="USDCNH",
        direction="BUY", confidence=0.74,
        summary="US-China tariff escalation signals Yuan pressure",
        cluster="USD Weaponization Wave", region="ASIA PAC",
        timestamp=datetime.utcnow().isoformat()
    ),
    Signal(
        id="sig_004", asset="MSCI EM", ticker="EEM",
        direction="SELL", confidence=0.69,
        summary="Dollar strength + EM capital outflows accelerating",
        cluster="USD Weaponization Wave", region="GLOBAL",
        timestamp=datetime.utcnow().isoformat()
    ),
]

@router.get("/signals", response_model=list[Signal])
def get_signals():
    return MOCK_SIGNALS