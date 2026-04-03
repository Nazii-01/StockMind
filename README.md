# 🧠 StockMind AI — Real-Time Stock Sentiment & Price Predictor

A full-stack AI-powered stock analysis system with:
- **Real-time prices** via Yahoo Finance (free, no API key needed)
- **NLP sentiment analysis** on live news headlines using VADER
- **ML prediction** using Random Forest + Linear Regression on technical indicators
- **Buy / Sell / Hold signals** with confidence scores
- **5-day price forecast**
- **Beautiful dashboard** with live charts

---

## 🏗️ Project Structure

```
stock-predictor/
├── backend/
│   ├── main.py                        # FastAPI app entry point
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile                     # Docker image for backend
│   ├── routes/
│   │   ├── stock_routes.py            # /api/stock endpoints
│   │   ├── sentiment_routes.py        # /api/sentiment endpoints
│   │   └── prediction_routes.py      # /api/predict endpoints
│   └── services/
│       ├── stock_service.py           # yfinance data fetching + indicators
│       ├── sentiment_service.py       # VADER NLP analysis
│       └── prediction_service.py     # ML model (RF + LR)
├── frontend/
│   └── index.html                     # Complete dashboard (single file)
├── docker-compose.yml                 # Run everything with Docker
├── run.sh                             # Mac/Linux one-click runner
└── run.bat                            # Windows one-click runner
```

---

## 🚀 Quick Start (No Docker — Recommended for First Run)

### Prerequisites
- **Python 3.9+** — [Download](https://python.org/downloads/)
- Internet connection (for live stock data)

### Option A: One-Click Script

**Mac / Linux:**
```bash
chmod +x run.sh
./run.sh
```

**Windows:**
```
Double-click run.bat
```

### Option B: Manual Setup

```bash
# 1. Go into backend folder
cd backend

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate it
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start the API server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Open the Dashboard
Just open `frontend/index.html` in your browser (double-click it or drag it into Chrome).

The dashboard connects to `http://localhost:8000` automatically.

---

## 🐳 Docker Setup (Optional)

Make sure Docker Desktop is installed, then:

```bash
docker-compose up --build
```

- Backend API → http://localhost:8000
- Frontend dashboard → http://localhost:3000

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stock/{ticker}` | Real-time price, OHLCV, technicals |
| GET | `/api/sentiment/{ticker}` | News sentiment analysis |
| GET | `/api/predict/{ticker}` | ML price prediction + signal |
| GET | `/api/stock/market/overview` | S&P 500, NASDAQ, Dow, VIX |
| GET | `/api/stock/market/movers` | Top gainers & losers |
| GET | `/health` | Health check |

Interactive docs at: http://localhost:8000/docs

---

## 🧠 How the ML Works

### Sentiment Analysis (VADER)
- Fetches live news headlines from Yahoo Finance
- VADER (Valence Aware Dictionary and sEntiment Reasoner) scores each headline
- Aggregates into a 0–100 sentiment score
- Positive > 60, Negative < 40, Neutral in between

### Price Prediction
1. **Feature Engineering**: SMA20, SMA50, RSI, MACD, Bollinger Bands, Volume Ratio
2. **Linear Regression** on sliding 20-day windows → next-day price estimate
3. **Random Forest Classifier** → probability of UP move tomorrow
4. **Sentiment Weighting**: Composite = 75% ML signal + 25% sentiment factor
5. **Signal Generation**: BUY if composite > 0.15, SELL if < -0.15, else HOLD

### 5-Day Forecast
Iterative rolling-window prediction using trained LR model.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Web API framework |
| `uvicorn` | ASGI server |
| `yfinance` | Free Yahoo Finance data |
| `pandas / numpy` | Data processing |
| `scikit-learn` | Random Forest + preprocessing |
| `vaderSentiment` | NLP sentiment analysis |

---

## ⚠️ Disclaimer

This project is for **educational purposes only**. Do not make real investment decisions based on this tool. Stock prediction is inherently uncertain.

---

## 🙏 Credits
- Data: Yahoo Finance via `yfinance`
- Sentiment: VADER NLP
- Icons & Fonts: Google Fonts (Syne, JetBrains Mono)
- Charts: Chart.js
