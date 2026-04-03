from fastapi import APIRouter, HTTPException
from services.sentiment_service import get_news_sentiment

router = APIRouter()

@router.get("/{ticker}")
def news_sentiment(ticker: str):
    try:
        return get_news_sentiment(ticker)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
