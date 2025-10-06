"""
Simple working API server for portfolio data - No complex dependencies
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Simple Portfolio API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample portfolio data
SAMPLE_PORTFOLIO_DATA = {
    "user_id": 1,
    "date": "2025-10-02",
    "total_value": 327625.00,
    "cash": 15000.0,
    "positions": [
        {"ticker": "AAPL", "units": 100.0, "price": 175.0, "position_val": 17500.0},
        {"ticker": "AMZN", "units": 139.52, "price": 220.71, "position_val": 30793.23},
        {"ticker": "MSFT", "units": 80.0, "price": 520.0, "position_val": 41600.0},
        {"ticker": "NVDA", "units": 150.0, "price": 180.0, "position_val": 27000.0},
        {"ticker": "TSLA", "units": 28.69, "price": 425.85, "position_val": 12216.95},
        {"ticker": "GOOGL", "units": 120.0, "price": 165.0, "position_val": 19800.0},
        {"ticker": "META", "units": 90.0, "price": 580.0, "position_val": 52200.0},
        {"ticker": "BND", "units": 200.0, "price": 85.0, "position_val": 17000.0},
        {"ticker": "VCIT", "units": 150.0, "price": 85.0, "position_val": 12750.0},
        {"ticker": "VOO", "units": 80.0, "price": 520.0, "position_val": 41600.0},
        {"ticker": "BTC", "units": 0.12, "price": 112017.21, "position_val": 13913.45},
        {"ticker": "ETH", "units": 15.0, "price": 4300.0, "position_val": 64500.0}
    ]
}

DASHBOARD_DATA = {
    "portfolio_created": "2025-09-23",
    "starting_value": 325000.0,
    "current_value": 327625.00,
    "time_period_days": 9,
    "net_worth": 327625.00,
    "total_gain_loss": 2625.00,
    "return_pct": 0.81,
    "allocation": {
        "stock": 72.5,
        "bond": 9.0,
        "crypto": 22.9,
        "cash": 4.4
    },
    "top_holdings": [
        {"ticker": "AMZN", "units": 139.52, "price": 220.71, "position_val": 30793.23},
        {"ticker": "BTC", "units": 0.12, "price": 112017.21, "position_val": 13913.45},
        {"ticker": "TSLA", "units": 28.69, "price": 425.85, "position_val": 12216.95}
    ],
    "movers": {"up": [], "down": []},
    "risk": {"sharpe_ratio": 1.85, "volatility_annualized": 18.2},
    "diversification": {"score": 75, "risk_level": "Medium"},
    "health_score": 80,
    "missing_prices": [],
    "data_quality": None
}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "simple-portfolio-api"}

@app.get("/portfolio/{user_id}/{date}")
def get_portfolio(user_id: int, date: str):
    """Get portfolio data for user and date"""
    return SAMPLE_PORTFOLIO_DATA

@app.get("/dashboard/{user_id}")
def get_dashboard(user_id: int):
    """Get dashboard data for user"""
    return DASHBOARD_DATA

@app.get("/portfolio")
def get_portfolio_legacy(user_id: int):
    """Legacy API format"""
    return {
        "portfolio": [
            {
                "Ticker": pos["ticker"],
                "Qty": pos["units"],
                "Current_Price": pos["price"],
                "Total_Value": pos["position_val"],
                "Cost_Basis": pos["position_val"],
                "Gain_Loss": 0,
                "Gain_Loss_Percent": 0,
                "Category": "Stock" if pos["ticker"] in ["AAPL", "AMZN", "MSFT", "NVDA", "TSLA"] else "Bond" if pos["ticker"] in ["BND", "VCIT"] else "Crypto"
            }
            for pos in SAMPLE_PORTFOLIO_DATA["positions"]
        ],
        "summary": {
            "Total_Value": SAMPLE_PORTFOLIO_DATA["total_value"],
            "Total_Cost_Basis": 325000.0,
            "Total_Gain_Loss": 2625.0,
            "Total_Gain_Loss_Percent": 0.81,
            "Total_Holdings": len(SAMPLE_PORTFOLIO_DATA["positions"]),
            "User": "Portfolio User"
        }
    }

@app.get("/insights/{user_id}")
def get_insights(user_id: int):
    """Get AI-powered portfolio insights"""
    return {
        "user_id": user_id,
        "insights": [
            "Your portfolio shows steady growth with a 0.81% return this week, outperforming many traditional benchmarks with consistent weekly gains.",
            "With 72.5% in stocks and 22.9% in crypto, your allocation is growth-oriented but consider monitoring volatility during market downturns.",
            "Strong diversification across 15+ positions helps minimize single-asset concentration risk. Your largest holding represents a healthy portion without over-concentration."
        ],
        "source": "ai",
        "disclaimer": "AI insights generated automatically. Not financial advice.",
        "generated_at": "2025-10-02T09:00:00Z"
    }

if __name__ == "__main__":
    print("🚀 Starting Simple Portfolio API on port 8001...")
    uvicorn.run(app, host="127.0.0.1", port=8001)
