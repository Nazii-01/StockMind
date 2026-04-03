from fastapi import APIRouter, HTTPException
from services.stock_service import get_stock_data, get_market_overview, get_top_movers

router = APIRouter()

@router.get("/{ticker}")
def stock_data(ticker: str, period: str = "3mo"):
    try:
        return get_stock_data(ticker, period)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/market/overview")
def market_overview():
    return get_market_overview()

@router.get("/market/movers")
def top_movers():
    return get_top_movers()
