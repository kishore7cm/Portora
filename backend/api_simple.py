"""
Simplified API for initial deployment without heavy dependencies
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from datetime import datetime

app = FastAPI(title="Portora API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
def root():
    return {"ok": True, "service": "Portora Portfolio Advisor API"}

@app.get("/health")
def health_check():
    """Health check endpoint for deployment platforms"""
    return {
        "status": "healthy",
        "service": "Portora Portfolio Advisor API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Mock portfolio data for initial testing
@app.get("/portfolio")
def get_portfolio():
    """Mock portfolio data for initial deployment"""
    return {
        "portfolio": [
            {
                "Category": "Equity",
                "Ticker": "AAPL",
                "Qty": 10,
                "Curr $": 1500.00,
                "Curr %": 15.0,
                "Tgt %": 20.0,
                "Drift %": -5.0,
                "RSI": 65.2,
                "MACD": 0.15,
                "Market": "US",
                "Trend": "Bullish",
                "Action": "Hold"
            },
            {
                "Category": "Equity", 
                "Ticker": "MSFT",
                "Qty": 8,
                "Curr $": 2400.00,
                "Curr %": 24.0,
                "Tgt %": 25.0,
                "Drift %": -1.0,
                "RSI": 58.7,
                "MACD": 0.08,
                "Market": "US",
                "Trend": "Bullish",
                "Action": "Hold"
            }
        ],
        "summary": [
            {
                "Category": "Equity",
                "Curr $": 3900.00,
                "Curr %": 39.0,
                "Tgt %": 45.0,
                "Drift": -6.0
            }
        ],
        "historical": [
            {"month": "2024-01", "value": 8500},
            {"month": "2024-02", "value": 9200},
            {"month": "2024-03", "value": 8800},
            {"month": "2024-04", "value": 9500},
            {"month": "2024-05", "value": 10200},
            {"month": "2024-06", "value": 9800}
        ]
    }

@app.get("/sp500")
def get_sp500():
    """Mock S&P 500 data for initial deployment"""
    return {
        "sp500": [
            {
                "Ticker": "AAPL",
                "Name": "Apple Inc.",
                "Sector": "Technology",
                "Price": 150.00,
                "Change": 2.50,
                "Change %": 1.69,
                "Volume": 45000000,
                "MarketCap": 2500000000000,
                "P_E": 28.5,
                "RSI": 65.2,
                "MACD": 0.15,
                "Trend": "Bullish",
                "Action": "Buy",
                "Score": 85,
                "Reason": "Strong fundamentals"
            }
        ]
    }

@app.get("/portfolio-health")
def get_portfolio_health():
    """Mock portfolio health data"""
    return {
        "overall_score": 78,
        "drift_score": 15,
        "diversification_score": 85,
        "risk_score": 72,
        "badges": [
            {"name": "Well Diversified", "status": "earned"},
            {"name": "Low Risk", "status": "earned"}
        ],
        "recommendations": [
            "Consider rebalancing technology allocation",
            "Add more international exposure"
        ]
    }

@app.get("/alerts")
def get_alerts():
    """Mock alerts data"""
    return {
        "alerts": [
            {
                "id": 1,
                "type": "rebalance",
                "title": "Portfolio Rebalance Needed",
                "message": "Your portfolio has drifted 5% from target allocation",
                "priority": "medium",
                "created_at": "2024-01-15T10:30:00Z",
                "read": False
            }
        ]
    }

@app.get("/alerts/count")
def get_alert_count():
    """Mock alert count"""
    return {"unread_count": 1}

@app.get("/onboarding/status")
def get_onboarding_status():
    """Mock onboarding status"""
    return {"has_seen_onboarding": False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
