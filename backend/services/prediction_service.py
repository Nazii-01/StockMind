import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings("ignore")


def predict_stock(ticker: str, sentiment_score: float = 50.0) -> dict:
    """
    Multi-model prediction combining:
    - LSTM-style sequence prediction (via numpy)
    - Random Forest signal classification
    - Sentiment-weighted score
    """
    stock = yf.Ticker(ticker.upper())
    hist = stock.history(period="6mo")

    if hist.empty or len(hist) < 30:
        raise ValueError(f"Insufficient data for {ticker}")

    df = hist[["Open", "High", "Low", "Close", "Volume"]].copy()
    df = _add_features(df)
    df.dropna(inplace=True)

    closes = df["Close"].values
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(closes.reshape(-1, 1)).flatten()

    # ── LSTM-style prediction (sliding window linear extrapolation) ──
    window = 20
    X_seq, y_seq = [], []
    for i in range(window, len(scaled)):
        X_seq.append(scaled[i - window:i])
        y_seq.append(scaled[i])
    X_seq, y_seq = np.array(X_seq), np.array(y_seq)

    lr = LinearRegression()
    lr.fit(X_seq, y_seq)
    last_window = scaled[-window:].reshape(1, -1)
    next_scaled = lr.predict(last_window)[0]
    next_price = float(scaler.inverse_transform([[next_scaled]])[0][0])

    # 5-day forecast
    forecast_prices = []
    rolling = list(scaled[-window:])
    for _ in range(5):
        inp = np.array(rolling[-window:]).reshape(1, -1)
        pred = lr.predict(inp)[0]
        rolling.append(pred)
        forecast_prices.append(float(scaler.inverse_transform([[pred]])[0][0]))

    current_price = float(closes[-1])
    price_change_pct = ((next_price - current_price) / current_price) * 100

    # ── Random Forest signal classifier ──
    features = ["SMA20", "SMA50", "RSI", "MACD", "BB_width", "Volume_ratio"]
    available = [f for f in features if f in df.columns]
    X_clf = df[available].values
    y_clf = (df["Close"].shift(-1) > df["Close"]).astype(int).values
    X_clf = X_clf[:-1]
    y_clf = y_clf[:-1]

    if len(X_clf) > 20:
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_clf, y_clf)
        last_features = df[available].values[-1].reshape(1, -1)
        rf_prob = float(rf.predict_proba(last_features)[0][1])  # prob of UP
        feature_importance = dict(zip(available, rf.feature_importances_.tolist()))
    else:
        rf_prob = 0.5
        feature_importance = {}

    # ── Sentiment-weighted composite score ──
    sentiment_weight = 0.25
    sentiment_factor = (sentiment_score - 50) / 50  # -1 to +1
    ml_signal = (rf_prob - 0.5) * 2                  # -1 to +1
    composite = (1 - sentiment_weight) * ml_signal + sentiment_weight * sentiment_factor

    # ── Buy / Hold / Sell signal ──
    if composite > 0.15:
        signal = "BUY"
        signal_color = "green"
        confidence = min(95, int(50 + composite * 45))
    elif composite < -0.15:
        signal = "SELL"
        signal_color = "red"
        confidence = min(95, int(50 + abs(composite) * 45))
    else:
        signal = "HOLD"
        signal_color = "yellow"
        confidence = int(40 + abs(composite) * 20)

    # ── Support & Resistance ──
    support = round(float(df["Close"].tail(20).min()), 2)
    resistance = round(float(df["Close"].tail(20).max()), 2)

    # ── Forecast dates ──
    last_date = hist.index[-1]
    forecast_dates = []
    d = last_date
    for _ in range(5):
        d += timedelta(days=1)
        while d.weekday() >= 5:
            d += timedelta(days=1)
        forecast_dates.append(d.strftime("%Y-%m-%d"))

    return {
        "ticker": ticker.upper(),
        "current_price": round(current_price, 2),
        "predicted_next_day": round(next_price, 2),
        "price_change_pct": round(price_change_pct, 2),
        "signal": signal,
        "signal_color": signal_color,
        "confidence": confidence,
        "rf_probability": round(rf_prob * 100, 1),
        "sentiment_factor": round(sentiment_factor, 3),
        "composite_score": round(composite, 3),
        "support": support,
        "resistance": resistance,
        "forecast": [
            {"date": d, "price": round(p, 2)}
            for d, p in zip(forecast_dates, forecast_prices)
        ],
        "feature_importance": feature_importance,
        "last_updated": datetime.now().isoformat()
    }


def _add_features(df: pd.DataFrame) -> pd.DataFrame:
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    df["EMA12"] = df["Close"].ewm(span=12).mean()
    df["EMA26"] = df["Close"].ewm(span=26).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    bb_mid = df["Close"].rolling(20).mean()
    bb_std = df["Close"].rolling(20).std()
    df["BB_upper"] = bb_mid + 2 * bb_std
    df["BB_lower"] = bb_mid - 2 * bb_std
    df["BB_width"] = (df["BB_upper"] - df["BB_lower"]) / bb_mid

    df["Volume_ratio"] = df["Volume"] / df["Volume"].rolling(20).mean()

    return df
