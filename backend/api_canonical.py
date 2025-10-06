"""
Canonical Portfolio API - Following strict calculation rules
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
from decimal import Decimal
from zoneinfo import ZoneInfo

# Local imports
from core.database import SessionLocal, get_db
from services.portfolio_calculation_service import PortfolioCalculationService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Canonical Portfolio API",
    description="Portfolio calculation service with strict canonical rules",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class PriceUpdateRequest(BaseModel):
    stock_tickers: List[str] = Field(default_factory=list)
    bond_etf_tickers: List[str] = Field(default_factory=list)
    crypto_tickers: List[str] = Field(default_factory=list)
    as_of: Optional[str] = Field(None, description="YYYY-MM-DD format")

class PriceUpdateResponse(BaseModel):
    counts: Dict[str, int]
    total_inserted: int
    as_of: str

class PositionDetail(BaseModel):
    ticker: str
    units: float
    price: Optional[float]
    position_val: float

class AllocationBreakdown(BaseModel):
    stock: float
    bond: float
    crypto: float
    cash: float

class RiskMetrics(BaseModel):
    sharpe_ratio: Optional[float]
    volatility_annualized: Optional[float]

class DiversificationMetrics(BaseModel):
    score: int
    risk_level: str

class MissingPrice(BaseModel):
    ticker: str
    last_price_date: Optional[str]
    reason: str

class DashboardResponse(BaseModel):
    portfolio_created: Optional[str]
    starting_value: float
    current_value: float
    time_period_days: int
    net_worth: float
    total_gain_loss: float
    return_pct: Optional[float]
    allocation: AllocationBreakdown
    top_holdings: List[PositionDetail]
    movers: Dict[str, List[PositionDetail]]
    risk: RiskMetrics
    diversification: DiversificationMetrics
    health_score: int
    missing_prices: List[MissingPrice]
    data_quality: Optional[str] = None

class PerformanceDataPoint(BaseModel):
    date: str
    total_value: float

class PerformanceSummary(BaseModel):
    current_value: float
    total_return_pct: Optional[float]
    total_gain_loss: float
    period_days: int
    data_points: int
    start_date: str
    end_date: str

class PerformanceResponse(BaseModel):
    series: List[PerformanceDataPoint]
    summary: PerformanceSummary

# Dependency functions
def get_portfolio_service(db: Session = Depends(get_db)) -> PortfolioCalculationService:
    """Create portfolio service instance with database dependency"""
    return PortfolioCalculationService(db)

# Helper functions
def parse_date(date_str: Optional[str]) -> date:
    """Parse date string or return today"""
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date format: {date_str}. Use YYYY-MM-DD"
            )
    return date.today()

def la_yesterday() -> date:
    """Return yesterday's date in America/Los_Angeles time zone (calendar day)."""
    now_la = datetime.now(ZoneInfo("America/Los_Angeles"))
    return (now_la.date() - timedelta(days=1))

def round_money(value: Optional[Decimal]) -> Optional[float]:
    """Round money values to 2 decimal places"""
    if value is None:
        return None
    return round(float(value), 2)

def round_percentage(value: Optional[Decimal]) -> Optional[float]:
    """Round percentage values to 2 decimal places"""
    if value is None:
        return None
    return round(float(value), 2)

# API Endpoints

@app.post("/prices/update", response_model=PriceUpdateResponse)
def update_prices(
    request: PriceUpdateRequest,
    service: PortfolioCalculationService = Depends(get_portfolio_service)
):
    """
    Update daily prices for specified tickers
    """
    try:
        as_of_date = parse_date(request.as_of)
        
        counts = service.update_daily_prices(
            stock_tickers=request.stock_tickers,
            bond_etf_tickers=request.bond_etf_tickers,
            crypto_tickers=request.crypto_tickers,
            as_of=as_of_date
        )
        
        total_inserted = sum(counts.values())
        
        return PriceUpdateResponse(
            counts=counts,
            total_inserted=total_inserted,
            as_of=as_of_date.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Price update error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Price update failed: {str(e)}"
        )

@app.post("/prices/update-yesterday", response_model=PriceUpdateResponse)
def update_yesterday_prices(
    request: PriceUpdateRequest,
    service: PortfolioCalculationService = Depends(get_portfolio_service)
):
    """
    Update daily prices using yesterday (America/Los_Angeles) strictly via Alpaca (stocks/bonds) and Twelve (crypto).
    """
    try:
        as_of_date = la_yesterday()

        counts = service.update_daily_prices(
            stock_tickers=request.stock_tickers,
            bond_etf_tickers=request.bond_etf_tickers,
            crypto_tickers=request.crypto_tickers,
            as_of=as_of_date
        )

        total_inserted = sum(counts.values())
        return PriceUpdateResponse(
            counts=counts,
            total_inserted=total_inserted,
            as_of=as_of_date.isoformat()
        )
    except Exception as e:
        logger.error(f"Yesterday price update error: {e}")
        raise HTTPException(status_code=500, detail=f"Yesterday price update failed: {str(e)}")

@app.get("/dashboard/{user_id}", response_model=DashboardResponse)
def get_dashboard(
    user_id: int,
    as_of: Optional[str] = None,
    service: PortfolioCalculationService = Depends(get_portfolio_service)
):
    """
    Get comprehensive dashboard data for user
    """
    try:
        as_of_date = parse_date(as_of)
        
        # Get basic metrics
        portfolio_created = service.portfolio_created_date(user_id)
        starting_value = service.starting_value(user_id)
        current_value = service.current_value(user_id, as_of_date)
        net_worth = service.net_worth(user_id, as_of_date)
        total_gain_loss = service.total_gain_loss(user_id, as_of_date)
        return_pct = service.return_pct(user_id, as_of_date)
        
        # Calculate time period
        time_period_days = 0
        if portfolio_created:
            time_period_days = (as_of_date - portfolio_created).days
        
        # Get allocation breakdown
        allocation_data = service.allocation_breakdown(user_id, as_of_date)
        allocation = AllocationBreakdown(
            stock=round_percentage(allocation_data['stock']),
            bond=round_percentage(allocation_data['bond']),
            crypto=round_percentage(allocation_data['crypto']),
            cash=round_percentage(allocation_data['cash'])
        )
        
        # Get top holdings
        top_holdings_data = service.top_holdings(user_id, as_of_date, k=3)
        top_holdings = [
            PositionDetail(
                ticker=holding['ticker'],
                units=holding['units'],
                price=holding['price'],
                position_val=round_money(Decimal(str(holding['position_val'])))
            )
            for holding in top_holdings_data
        ]
        
        # Get portfolio snapshot for missing prices
        snapshot = service.compute_portfolio_snapshot(user_id, as_of_date)
        missing_prices = [
            MissingPrice(
                ticker=mp['ticker'],
                last_price_date=mp.get('last_price_date'),
                reason=mp['reason']
            )
            for mp in snapshot.missing_prices
        ]
        
        # Calculate data quality
        data_quality = None
        if snapshot.total_value > 0:
            missing_value = sum(
                pos.position_val for pos in snapshot.by_position 
                if pos.missing_price
            )
            missing_pct = (missing_value / snapshot.total_value) * 100
            if missing_pct > 20:
                data_quality = "LOW"
        
        # Placeholder values for complex metrics (implement as needed)
        risk = RiskMetrics(sharpe_ratio=None, volatility_annualized=None)
        diversification = DiversificationMetrics(score=75, risk_level="Medium")
        health_score = 80
        movers = {"up": [], "down": []}
        
        return DashboardResponse(
            portfolio_created=portfolio_created.isoformat() if portfolio_created else None,
            starting_value=round_money(starting_value),
            current_value=round_money(current_value),
            time_period_days=time_period_days,
            net_worth=round_money(net_worth),
            total_gain_loss=round_money(total_gain_loss),
            return_pct=round_percentage(return_pct),
            allocation=allocation,
            top_holdings=top_holdings,
            movers=movers,
            risk=risk,
            diversification=diversification,
            health_score=health_score,
            missing_prices=missing_prices,
            data_quality=data_quality
        )
        
    except Exception as e:
        logger.error(f"Dashboard error for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Dashboard calculation failed: {str(e)}"
        )

@app.post("/snapshot/yesterday/{user_id}")
def snapshot_yesterday(
    user_id: int,
    service: PortfolioCalculationService = Depends(get_portfolio_service)
):
    """
    Compute and persist a portfolio snapshot for yesterday (LA time), then return the DashboardResponse.
    """
    try:
        as_of_date = la_yesterday()
        service.upsert_daily_snapshot(user_id, as_of_date)
        # Reuse dashboard response
        return get_dashboard(user_id=user_id, as_of=as_of_date.isoformat(), service=service)
    except Exception as e:
        logger.error(f"Snapshot yesterday error for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Snapshot yesterday failed: {str(e)}")

@app.get("/dashboard/performance/{user_id}", response_model=PerformanceResponse)
def get_performance(
    user_id: int,
    start_date: str,
    end_date: str,
    service: PortfolioCalculationService = Depends(get_portfolio_service)
):
    """
    Get performance data for date range
    """
    try:
        start_dt = parse_date(start_date)
        end_dt = parse_date(end_date)
        
        if start_dt > end_dt:
            raise HTTPException(
                status_code=400,
                detail="start_date must be <= end_date"
            )
        
        # Get daily series from portfolio_summary
        from domain.models_v2 import PortfolioSummary
        
        series_data = (
            service.db.query(PortfolioSummary.date, PortfolioSummary.total_value)
            .filter(
                PortfolioSummary.user_id == user_id,
                PortfolioSummary.date >= start_dt,
                PortfolioSummary.date <= end_dt
            )
            .order_by(PortfolioSummary.date)
            .all()
        )
        
        series = [
            PerformanceDataPoint(
                date=row[0].isoformat(),
                total_value=round_money(Decimal(str(row[1])))
            )
            for row in series_data
        ]
        
        # Calculate summary
        current_value = 0.0
        start_value = 0.0
        total_return_pct = None
        total_gain_loss = 0.0
        
        if series:
            current_value = series[-1].total_value
            start_value = series[0].total_value
            total_gain_loss = current_value - start_value
            
            if start_value > 0:
                total_return_pct = round((total_gain_loss / start_value) * 100, 2)
        
        period_days = (end_dt - start_dt).days + 1
        data_points = len(series)
        
        summary = PerformanceSummary(
            current_value=current_value,
            total_return_pct=total_return_pct,
            total_gain_loss=total_gain_loss,
            period_days=period_days,
            data_points=data_points,
            start_date=start_dt.isoformat(),
            end_date=end_dt.isoformat()
        )
        
        return PerformanceResponse(
            series=series,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Performance error for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Performance calculation failed: {str(e)}"
        )

@app.get("/dashboard/audit/{user_id}")
def get_audit(
    user_id: int,
    as_of: Optional[str] = None,
    service: PortfolioCalculationService = Depends(get_portfolio_service)
):
    """
    Get detailed audit information for portfolio positions
    """
    try:
        as_of_date = parse_date(as_of)
        snapshot = service.compute_portfolio_snapshot(user_id, as_of_date)
        
        audit_data = []
        for pos in snapshot.by_position:
            # Determine source
            source = "static"
            if pos.asset_class in ["STOCK", "BOND_ETF"]:
                source = "alpaca"
            elif pos.asset_class == "CRYPTO":
                source = "twelve"
            
            # Determine if missing or stale
            missing_or_stale = pos.missing_price
            if not missing_or_stale and pos.price_date:
                days_old = (as_of_date - pos.price_date).days
                if pos.asset_class == "CRYPTO" and days_old > 1:
                    missing_or_stale = True
                elif pos.asset_class in ["STOCK", "BOND_ETF"] and days_old > 3:
                    missing_or_stale = True
            
            audit_data.append({
                "ticker": pos.ticker,
                "asset_class": pos.asset_class,
                "units": round_money(pos.units),
                "price_used": round_money(pos.price),
                "price_date": pos.price_date.isoformat() if pos.price_date else None,
                "position_val": round_money(pos.position_val),
                "source": source,
                "missing_or_stale": missing_or_stale
            })
        
        return {
            "user_id": user_id,
            "as_of": as_of_date.isoformat(),
            "positions": audit_data,
            "total_positions": len(audit_data),
            "missing_or_stale_count": sum(1 for pos in audit_data if pos["missing_or_stale"])
        }
        
    except Exception as e:
        logger.error(f"Audit error for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Audit calculation failed: {str(e)}"
        )

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "canonical-portfolio-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
