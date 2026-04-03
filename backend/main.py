from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from routes import stock_routes, sentiment_routes, prediction_routes

app = FastAPI(
    title="Stock Sentiment Predictor API",
    description="Real-time stock price + sentiment analysis + ML prediction",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stock_routes.router, prefix="/api/stock", tags=["Stock Data"])
app.include_router(sentiment_routes.router, prefix="/api/sentiment", tags=["Sentiment"])
app.include_router(prediction_routes.router, prefix="/api/predict", tags=["Prediction"])

@app.get("/")
def root():
    return {"message": "Stock Sentiment Predictor API is running!", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
