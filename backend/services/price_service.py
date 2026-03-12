import yfinance as yf
import time
from datetime import datetime

TICKER_MAP = {
    "WTI":    "CL=F",
    "XAUUSD": "GC=F",
    "USDCNH": "USDCNH=X",
    "EEM":    "EEM",
    "XAGUSD": "SI=F",
    "DXY":    "DX-Y.NYB",
    "SPX":    "^GSPC",
    "VIX":    "^VIX",
    "BRENT":  "BZ=F",
}

_cache: dict = {}
CACHE_TTL = 300  # 5 minutes

def _is_stale(key: str) -> bool:
    if key not in _cache:
        return True
    return (time.time() - _cache[key]["fetched_at"]) > CACHE_TTL

def get_price_data(our_ticker: str) -> dict | None:
    yf_symbol = TICKER_MAP.get(our_ticker.upper())
    if not yf_symbol:
        return None

    cache_key = our_ticker.upper()
    if not _is_stale(cache_key):
        return _cache[cache_key]

    try:
        ticker = yf.Ticker(yf_symbol)
        hist   = ticker.history(period="7d", interval="1d")
        if hist.empty:
            return None

        closes       = hist["Close"].tolist()
        sparkline    = [round(v, 4) for v in closes]
        current      = closes[-1]
        prev         = closes[-2] if len(closes) > 1 else closes[0]
        change_pct   = round(((current - prev) / prev) * 100, 2)

        month_hist        = ticker.history(period="30d", interval="1d")
        month_start       = month_hist["Close"].iloc[0] if not month_hist.empty else current
        month_change_pct  = round(((current - month_start) / month_start) * 100, 2)

        result = {
            "ticker":           our_ticker.upper(),
            "yf_symbol":        yf_symbol,
            "price":            round(current, 4),
            "change_pct":       change_pct,
            "month_change_pct": month_change_pct,
            "sparkline":        sparkline,
            "fetched_at":       time.time(),
            "timestamp":        datetime.utcnow().isoformat(),
        }
        _cache[cache_key] = result
        return result

    except Exception as e:
        print(f"yfinance error for {our_ticker} ({yf_symbol}): {e}")
        return None

def get_all_prices() -> dict:
    return {t: d for t in TICKER_MAP if (d := get_price_data(t))}