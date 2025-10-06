"""
Portfolio API v2 - Clean Architecture
Best practices: Service layer, dependency injection, proper error handling
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db
from services.data_service import DataService
from services.portfolio_service import PortfolioService
from typing import Dict
import uvicorn


# Create FastAPI app with proper configuration
app = FastAPI(
    title="Portfolio API v2",
    description="Clean architecture portfolio API with service layer",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency injection for services
def get_data_service(db: Session = Depends(get_db)) -> DataService:
    """Get data service instance"""
    return DataService(db)


def get_portfolio_service(data_service: DataService = Depends(get_data_service)) -> PortfolioService:
    """Get portfolio service instance"""
    return PortfolioService(data_service)


# API Endpoints
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Portfolio API v2 - Clean Architecture",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}


@app.get("/portfolio")
def get_portfolio(
    user_id: int = 1,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
) -> Dict:
    """
    Get portfolio data using clean service architecture
    """
    try:
        print(f"📊 API v2: Getting portfolio for user {user_id}")
        result = portfolio_service.get_portfolio_summary(user_id)
        
        # Debug output for GLDM
        gldm_items = [item for item in result["portfolio"] if item["Ticker"] == "GLDM"]
        if gldm_items:
            gldm = gldm_items[0]
            print(f"🔍 API v2 GLDM: ${gldm['Current_Price']:.2f}, {gldm['Gain_Loss_Percent']:.2f}%")
        
        return result
        
    except Exception as e:
        print(f"❌ API v2 Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/portfolio/update-prices")
def update_portfolio_prices(
    user_id: int = 1,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
) -> Dict:
    """
    Update portfolio prices from CSV data
    """
    try:
        print(f"🔄 API v2: Updating prices for user {user_id}")
        result = portfolio_service.update_prices_from_csv(user_id)
        return result
        
    except Exception as e:
        print(f"❌ API v2 Update Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/gldm-debug")
def get_gldm_debug(
    user_id: int = 1,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
) -> Dict:
    """
    Debug endpoint for GLDM data comparison
    """
    try:
        result = portfolio_service.get_gldm_debug_info(user_id)
        return result
        
    except Exception as e:
        print(f"❌ API v2 GLDM Debug Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/return/{ticker}")
def calculate_ticker_return(
    ticker: str,
    start_date: str = "2025-09-23",
    end_date: str = "2025-09-30",
    user_id: int = 1,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
) -> Dict:
    """
    Calculate return for a specific ticker between dates
    """
    try:
        from datetime import datetime
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        result = portfolio_service.calculate_return(user_id, ticker, start, end)
        if not result:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        print(f"❌ API v2 Return Calculation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Additional endpoints for scalability
@app.get("/portfolio/{user_id}/summary")
def get_portfolio_summary(
    user_id: int,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
) -> Dict:
    """Get portfolio summary only (faster endpoint)"""
    try:
        result = portfolio_service.get_portfolio_summary(user_id)
        return result["summary"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/{user_id}/holdings")
def get_portfolio_holdings(
    user_id: int,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
) -> Dict:
    """Get portfolio holdings only"""
    try:
        result = portfolio_service.get_portfolio_summary(user_id)
        return {"holdings": result["portfolio"], "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("🚀 Starting Portfolio API v2 - Clean Architecture")
    print("📊 Service-based architecture with proper separation of concerns")
    print("🔧 Using CSV as source of truth for market data")
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)
