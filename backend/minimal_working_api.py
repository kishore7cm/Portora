#!/usr/bin/env python3
"""
Minimal working API server for portfolio data
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="Minimal Portfolio API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Minimal Portfolio API is running", "status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is working"}

@app.get("/portfolio")
def get_portfolio(user_id: int = 1):
    """Get portfolio data"""
    return {
        "portfolio": [
            {
                "Ticker": "AAPL",
                "Qty": 100.0,
                "Current_Price": 175.0,
                "Total_Value": 17500.0,
                "Gain_Loss": 875.0,
                "Gain_Loss_Percent": 5.26,
                "Category": "Stock",
                "RSI": 65,
                "MACD": 0.5,
                "Market": "US",
                "Trend": "Bullish",
                "Action": "Hold",
                "Score": 85,
                "Sentiment": "Positive"
            },
            {
                "Ticker": "AMZN",
                "Qty": 139.52,
                "Current_Price": 220.71,
                "Total_Value": 30793.23,
                "Gain_Loss": 1539.66,
                "Gain_Loss_Percent": 5.26,
                "Category": "Stock",
                "RSI": 68,
                "MACD": 0.4,
                "Market": "US",
                "Trend": "Bullish",
                "Action": "Hold",
                "Score": 88,
                "Sentiment": "Positive"
            },
            {
                "Ticker": "Cash",
                "Qty": 1,
                "Current_Price": 15000.0,
                "Total_Value": 15000.0,
                "Gain_Loss": 0,
                "Gain_Loss_Percent": 0,
                "Category": "Cash",
                "RSI": 50,
                "MACD": 0,
                "Market": "US",
                "Trend": "Neutral",
                "Action": "Hold",
                "Score": 75,
                "Sentiment": "Neutral"
            }
        ],
        "summary": {
            "total_value": 327625.00,
            "total_gain_loss": 2625.00,
            "total_gain_loss_percent": 0.81,
            "cash_balance": 15000.0
        }
    }

@app.get("/sp500")
def get_sp500():
    """Get S&P 500 data"""
    return [
        {"symbol": "AAPL", "price": 175.50, "change": 2.50, "changePercent": 1.45, "rsi": 65, "macd": 0.5, "score": 85, "trend": "Bullish", "sector": "Technology"},
        {"symbol": "MSFT", "price": 350.25, "change": -3.75, "changePercent": -1.06, "rsi": 45, "macd": -0.2, "score": 60, "trend": "Bearish", "sector": "Technology"},
        {"symbol": "GOOGL", "price": 2800.00, "change": 25.00, "changePercent": 0.90, "rsi": 70, "macd": 0.8, "score": 90, "trend": "Bullish", "sector": "Technology"}
    ]

@app.get("/insights/{user_id}")
def get_insights(user_id: int):
    """Get AI insights"""
    return {
        "user_id": user_id,
        "insights": [
            "Your portfolio shows steady growth with a 0.81% return this week. The balanced allocation across stocks (72.5%) and crypto (22.9%) provides good diversification while maintaining growth potential.",
            "With strong performance in tech stocks like AAPL and AMZN, consider taking some profits and rebalancing into defensive sectors.",
            "Your cash position of 4.3% is slightly below the recommended 5-10% range. Consider increasing cash reserves for upcoming opportunities."
        ],
        "source": "ai",
        "disclaimer": "AI insights generated automatically. Not financial advice.",
        "generated_at": "2025-10-02T09:00:00Z"
    }

if __name__ == "__main__":
    print("🚀 Starting Minimal Portfolio API on http://127.0.0.1:8001")
    print("📊 Available endpoints:")
    print("  - GET / (root)")
    print("  - GET /health (health check)")
    print("  - GET /portfolio?user_id=1 (portfolio data)")
    print("  - GET /sp500 (S&P 500 data)")
    print("  - GET /insights/1 (AI insights)")
    
    try:
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=8001, 
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
