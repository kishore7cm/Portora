#!/usr/bin/env python3
"""
Simple API built from scratch - ONLY reads from database
No complex calculations, no data transformations
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db
from models import PortfolioValues, User
import uvicorn

# Create FastAPI app
app = FastAPI(title="Simple Portfolio API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "Simple Portfolio API", "status": "running"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/portfolio")
def get_portfolio_simple(user_id: int = 1, db: Session = Depends(get_db)):
    """
    Get portfolio data - SIMPLE VERSION
    Just read from database, no calculations
    """
    try:
        print(f"📊 Getting portfolio for user_id: {user_id}")
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found", "status": "error"}
        
        # Get portfolio values - DIRECT from database
        portfolio_values = db.query(PortfolioValues).filter(PortfolioValues.user_id == user_id).all()
        print(f"📊 Found {len(portfolio_values)} portfolio holdings")
        
        if not portfolio_values:
            return {
                "portfolio": [],
                "summary": {"Total_Value": 0, "Total_Holdings": 0},
                "status": "success"
            }
        
        # Convert to simple format - NO CALCULATIONS
        portfolio_data = []
        total_value = 0
        total_cost_basis = 0
        total_gain_loss = 0
        
        for holding in portfolio_values:
            # Just use the values directly from database
            portfolio_item = {
                "Ticker": holding.ticker,
                "Current_Price": holding.current_price,  # Direct from DB
                "Total_Value": holding.total_value,      # Direct from DB
                "Cost_Basis": holding.cost_basis,        # Direct from DB
                "Gain_Loss": holding.gain_loss,          # Direct from DB
                "Gain_Loss_Percent": holding.gain_loss_percent,  # Direct from DB
                "Category": holding.category or "Stock"
            }
            
            portfolio_data.append(portfolio_item)
            
            # Sum up totals
            total_value += holding.total_value
            total_cost_basis += holding.cost_basis
            total_gain_loss += holding.gain_loss
            
            # Debug output for GLDM
            if holding.ticker == "GLDM":
                print(f"🔍 GLDM DEBUG:")
                print(f"   Current Price: ${holding.current_price:.2f}")
                print(f"   Total Value: ${holding.total_value:.2f}")
                print(f"   Gain/Loss %: {holding.gain_loss_percent:.2f}%")
        
        # Calculate summary
        total_gain_loss_percent = (total_gain_loss / total_cost_basis) * 100 if total_cost_basis > 0 else 0
        
        summary = {
            "Total_Value": total_value,
            "Total_Cost_Basis": total_cost_basis,
            "Total_Gain_Loss": total_gain_loss,
            "Total_Gain_Loss_Percent": total_gain_loss_percent,
            "Total_Holdings": len(portfolio_data),
            "User": user.name
        }
        
        print(f"📊 Portfolio Summary:")
        print(f"   Total Value: ${total_value:.2f}")
        print(f"   Total Holdings: {len(portfolio_data)}")
        
        return {
            "portfolio": portfolio_data,
            "summary": summary,
            "status": "success"
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {"error": str(e), "status": "error"}

@app.get("/portfolio/gldm-debug")
def get_gldm_debug(user_id: int = 1, db: Session = Depends(get_db)):
    """Debug endpoint specifically for GLDM"""
    try:
        gldm = db.query(PortfolioValues).filter(
            PortfolioValues.user_id == user_id,
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
            "category": gldm.category,
            "status": "success"
        }
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

if __name__ == "__main__":
    print("🚀 Starting Simple Portfolio API...")
    print("📊 This API ONLY reads from database - no calculations")
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)
