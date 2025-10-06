"""
Perfect Portfolio API - The Most Efficient Way
Exactly how I would build it for myself
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import sys
import os
from typing import Dict, List
from datetime import datetime, date

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Import our perfect services
from services.data_service import DataService
from services.portfolio_service import PortfolioService
from core.database import get_db

# Create FastAPI app - clean and simple
app = FastAPI(
    title="Perfect Portfolio API",
    description="The most efficient way - clean architecture, type-safe, production-ready",
    version="3.0.0"
)

# CORS - simple and effective
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Perfect dependency injection
def get_data_service(db: Session = Depends(get_db)) -> DataService:
    return DataService(db)

def get_portfolio_service(data_service: DataService = Depends(get_data_service)) -> PortfolioService:
    return PortfolioService(data_service)

# Perfect API endpoints
@app.get("/")
def root():
    """Perfect root endpoint"""
    return {
        "name": "Perfect Portfolio API",
        "version": "3.0.0",
        "status": "running",
        "architecture": "clean",
        "docs": "/docs"
    }

@app.get("/health")
def health_check(data_service: DataService = Depends(get_data_service)):
    """Perfect health check"""
    try:
        health = data_service.health_check()
        return {
            "status": "healthy",
            "version": "3.0.0",
            "services": health
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/api/v3/portfolio")
def get_portfolio(
    user_id: int = 1,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """Perfect portfolio endpoint"""
    try:
        print(f"🎯 Perfect API: Getting portfolio for user {user_id}")
        result = portfolio_service.get_portfolio_summary(user_id)
        
        # Perfect logging
        print(f"✅ Perfect API: {result.summary.Total_Holdings} holdings, ${result.summary.Total_Value:,.2f}")
        
        # Debug GLDM
        gldm_items = [item for item in result.portfolio if item.Ticker == "GLDM"]
        if gldm_items:
            gldm = gldm_items[0]
            print(f"🔍 Perfect GLDM: ${gldm.Current_Price:.2f}, {gldm.Gain_Loss_Percent:.2f}%")
        
        return result.dict()
        
    except Exception as e:
        print(f"❌ Perfect API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/debug/gldm")
def get_gldm_debug(
    user_id: int = 1,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """Perfect GLDM debug"""
    try:
        result = portfolio_service.get_gldm_debug_info(user_id)
        return result.dict()
    except Exception as e:
        print(f"❌ Perfect GLDM Debug Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/portfolio/update-prices")
def update_prices(
    user_id: int = 1,
    force_update: bool = False,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """Perfect price update"""
    try:
        print(f"🔄 Perfect API: Updating prices for user {user_id}")
        result = portfolio_service.update_prices_from_csv(user_id, force_update)
        print(f"✅ Perfect Update: {result.updated_count} holdings updated")
        return result.dict()
    except Exception as e:
        print(f"❌ Perfect Update Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/portfolio/{user_id}/top-holdings")
def get_top_holdings(
    user_id: int,
    limit: int = 10,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """Perfect top holdings"""
    try:
        result = portfolio_service.get_top_holdings(user_id, limit)
        return [item.dict() for item in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/portfolio/{user_id}/top-movers")
def get_top_movers(
    user_id: int,
    limit: int = 10,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """Perfect top movers"""
    try:
        result = portfolio_service.get_top_movers(user_id, limit)
        return [item.dict() for item in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/analysis/return/{ticker}")
def calculate_return(
    ticker: str,
    start_date: str = "2025-09-23",
    end_date: str = "2025-09-30",
    user_id: int = 1,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """Perfect return calculation"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        result = portfolio_service.calculate_return(user_id, ticker, start, end)
        if not result:
            raise HTTPException(status_code=404, detail=f"No data for {ticker}")
        
        return result.dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Legacy compatibility
@app.get("/portfolio")
def get_portfolio_legacy(
    user_id: int = 1,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """Legacy endpoint for backward compatibility"""
    print("⚠️  Using legacy endpoint - consider upgrading to /api/v3/portfolio")
    return get_portfolio(user_id, portfolio_service)

@app.get("/portfolio/gldm-debug")
def get_gldm_debug_legacy(
    user_id: int = 1,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """Legacy debug endpoint"""
    print("⚠️  Using legacy endpoint - consider upgrading to /api/v3/debug/gldm")
    return get_gldm_debug(user_id, portfolio_service)

# Perfect startup
@app.on_event("startup")
async def startup():
    print("🚀 Perfect Portfolio API Starting...")
    print("📊 Clean Architecture | Type-Safe | Production-Ready")
    print("🔧 CSV-based data with perfect database integration")

if __name__ == "__main__":
    print("🎯 Starting Perfect Portfolio API - The Most Efficient Way")
    print("✨ Exactly how I would build it for myself")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )
