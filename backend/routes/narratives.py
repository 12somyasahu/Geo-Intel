from fastapi import APIRouter
from backend.models import Narrative

router = APIRouter()

MOCK_NARRATIVES = [
    Narrative(
        id="nar_001", title="Energy Supply Squeeze", strength=0.84,
        summary="Pipeline disruptions and OPEC+ cuts creating structural supply deficit",
        regions=["EUROPE", "MIDDLE EAST"], assets=["WTI", "Brent", "Nat Gas"]
    ),
    Narrative(
        id="nar_002", title="Middle East Escalation Arc", strength=0.76,
        summary="Multi-front conflict expanding risk premium across commodities",
        regions=["MIDDLE EAST"], assets=["Gold", "Oil", "USD"]
    ),
    Narrative(
        id="nar_003", title="USD Weaponization Wave", strength=0.71,
        summary="Sanctions + tariff escalation driving dollar dominance narrative",
        regions=["ASIA PAC", "GLOBAL"], assets=["USD/CNH", "MSCI EM", "BTC"]
    ),
]

@router.get("/narratives", response_model=list[Narrative])
def get_narratives():
    return MOCK_NARRATIVES