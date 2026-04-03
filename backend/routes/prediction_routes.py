from fastapi import APIRouter, HTTPException, Query
from services.prediction_service import predict_stock

router = APIRouter()

@router.get("/{ticker}")
def prediction(ticker: str, sentiment_score: float = Query(default=50.0, ge=0, le=100)):
    try:
        return predict_stock(ticker, sentiment_score)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
