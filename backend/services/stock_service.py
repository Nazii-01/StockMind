import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional


def get_stock_data(ticker: str, period: str = "3mo") -> dict:
    """Fetch real-time stock data using yfinance (free, no API key needed)"""
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info

        # Get historical data
        hist = stock.history(period=period)
        if hist.empty:
            raise ValueError(f"No data found for ticker: {ticker}")

        # Current price data
        current_price = info.get("currentPrice") or info.get("regularMarketPrice") or float(hist["Close"].iloc[-1])
        prev_close = info.get("previousClose") or float(hist["Close"].iloc[-2])
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100

        # Build OHLCV history list
        history = []
        for date, row in hist.tail(90).iterrows():
            history.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"])
            })

        # Technical indicators
        closes = hist["Close"]
        sma20 = float(closes.rolling(20).mean().iloc[-1])
        sma50 = float(closes.rolling(50).mean().iloc[-1]) if len(closes) >= 50 else sma20
        rsi = compute_rsi(closes)

        # Bollinger Bands
        bb_mid = closes.rolling(20).mean()
        bb_std = closes.rolling(20).std()
        bb_upper = float((bb_mid + 2 * bb_std).iloc[-1])
        bb_lower = float((bb_mid - 2 * bb_std).iloc[-1])

        return {
            "ticker": ticker.upper(),
            "name": info.get("longName", ticker.upper()),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "current_price": round(current_price, 2),
            "previous_close": round(prev_close, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", 0),
            "volume": info.get("volume", 0),
            "avg_volume": info.get("averageVolume", 0),
            "week_52_high": info.get("fiftyTwoWeekHigh", 0),
            "week_52_low": info.get("fiftyTwoWeekLow", 0),
            "dividend_yield": info.get("dividendYield", 0),
            "beta": info.get("beta", 1.0),
            "sma20": round(sma20, 2),
            "sma50": round(sma50, 2),
            "rsi": round(rsi, 2),
            "bb_upper": round(bb_upper, 2),
            "bb_lower": round(bb_lower, 2),
            "history": history,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise ValueError(f"Error fetching stock data for {ticker}: {str(e)}")


def compute_rsi(prices: pd.Series, period: int = 14) -> float:
    """Compute RSI technical indicator"""
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0


def get_market_overview() -> dict:
    """Get major indices overview"""
    indices = {
        "NIFTY 50": "^NSEI",
        "SENSEX": "^BSESN",
        "NIFTY IT": "^CNXIT",
        "NIFTY Bank": "^NSEBANK"
    }
    results = {}
    for name, symbol in indices.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if not hist.empty and len(hist) >= 2:
                current = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[-2])
                chg_pct = ((current - prev) / prev) * 100
                results[name] = {
                    "value": round(current, 2),
                    "change_pct": round(chg_pct, 2)
                }
        except:
            results[name] = {"value": 0, "change_pct": 0}
    return results


def get_top_movers() -> dict:
    """Get today's top gainers and losers from a watchlist"""
    tickers = ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "RELIANCE.NS", "TATAMOTORS.NS", "HINDUNILVR.NS", "BAJFINANCE.NS", "ICICIBANK.NS", "HDFC.NS"]
    movers = []
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            hist = stock.history(period="2d")
            if len(hist) >= 2:
                cur = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[-2])
                chg = ((cur - prev) / prev) * 100
                movers.append({"ticker": t, "price": round(cur, 2), "change_pct": round(chg, 2)})
        except:
            pass
    movers.sort(key=lambda x: x["change_pct"], reverse=True)
    return {
        "gainers": movers[:3],
        "losers": movers[-3:][::-1]
    }
