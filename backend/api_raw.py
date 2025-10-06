#!/usr/bin/env python3
"""
Ultra-simple API - just return raw database data
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from database import SessionLocal
from models import PortfolioValues, User

app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Raw Portfolio API", "status": "running"}

@app.get("/portfolio")
def get_portfolio_raw():
    """Get raw portfolio data from database"""
    db = SessionLocal()
    try:
        # Get all portfolio values for user 1
        holdings = db.query(PortfolioValues).filter(PortfolioValues.user_id == 1).all()
        
        portfolio_data = []
        for holding in holdings:
            portfolio_data.append({
                "Ticker": holding.ticker,
                "Current_Price": holding.current_price,
                "Total_Value": holding.total_value,
                "Cost_Basis": holding.cost_basis,
                "Gain_Loss": holding.gain_loss,
                "Gain_Loss_Percent": holding.gain_loss_percent,
                "Category": holding.category
            })
        
        return {
            "portfolio": portfolio_data,
            "count": len(portfolio_data),
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}
    finally:
        db.close()

@app.get("/gldm")
def get_gldm_only():
    """Get only GLDM data"""
    db = SessionLocal()
    try:
        gldm = db.query(PortfolioValues).filter(
            PortfolioValues.user_id == 1,
            PortfolioValues.ticker == "GLDM"
        ).first()
        
        if not gldm:
            return {"error": "GLDM not found", "status": "error"}
        
        return {
            "ticker": gldm.ticker,
            "current_price": gldm.current_price,
            "total_value": gldm.total_value,
            "cost_basis": gldm.cost_basis,
            "gain_loss": gldm.gain_loss,
            "gain_loss_percent": gldm.gain_loss_percent,
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Raw Portfolio API on port 8004...")
    uvicorn.run(app, host="127.0.0.1", port=8004)
