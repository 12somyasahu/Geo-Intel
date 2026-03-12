from fastapi import APIRouter, HTTPException
from backend.services.price_service import get_price_data, get_all_prices

router = APIRouter()

@router.get("/prices")
def fetch_all_prices():
    return get_all_prices()

@router.get("/prices/{ticker}")
def fetch_price(ticker: str):
    data = get_price_data(ticker.upper())
    if not data:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found or unavailable")
    return data