"""
FastAPI CRUD Endpoints for Normalized Portfolio Database
Complete CRUD operations with efficient queries
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date, datetime
import uvicorn

# Database imports
from core.database import get_db
from domain.models_v2 import (
    User, Portfolio, DailyPrice, PortfolioDailyValue, 
    PortfolioSummary, AssetCategory, PortfolioTransaction, CashTransaction
)

# Create FastAPI app
app = FastAPI(
    title="Portfolio API - Normalized Database",
    description="Complete CRUD operations for normalized portfolio management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for requests/responses
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=255)

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: Optional[str]
    
    class Config:
        from_attributes = True

class PortfolioCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    ticker: str = Field(..., min_length=1, max_length=20)
    units: float = Field(..., gt=0)
    avg_price: float = Field(..., gt=0)
    buy_date: date

class PortfolioResponse(BaseModel):
    portfolio_id: int
    user_id: int
    ticker: str
    units: float
    avg_price: float
    buy_date: date
    
    class Config:
        from_attributes = True

class DailyPriceCreate(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20)
    price_date: date
    close_price: float = Field(..., gt=0)
    open_price: Optional[float] = Field(None, gt=0)
    high_price: Optional[float] = Field(None, gt=0)
    low_price: Optional[float] = Field(None, gt=0)
    volume: Optional[int] = Field(None, ge=0)

class DailyPriceResponse(BaseModel):
    price_id: int
    ticker: str
    price_date: date
    close_price: float
    open_price: Optional[float]
    high_price: Optional[float]
    low_price: Optional[float]
    volume: Optional[int]
    
    class Config:
        from_attributes = True

class PositionValue(BaseModel):
    ticker: str
    units: float
    price: float
    position_val: float

class PortfolioSummaryResponse(BaseModel):
    user_id: int
    date: str
    total_value: float
    positions: List[PositionValue]

class PortfolioWithCashResponse(BaseModel):
    user_id: int
    date: str
    total_value: float
    cash: float
    positions: List[PositionValue]

class CashTransactionCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    amount: float
    transaction_date: date
    type: str = Field(..., pattern="^(deposit|withdrawal)$")
    description: Optional[str] = Field(None, max_length=255)

class CashTransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    transaction_date: date
    type: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# CRUD Endpoints

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "Portfolio API - Normalized Database",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "users": "/users/",
            "portfolio": "/portfolio/",
            "prices": "/prices/",
            "daily_values": "/daily-values/",
            "summary": "/summary/"
        }
    }

# User CRUD
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Add a new user"""
    try:
        # Check if email already exists
        if user.email:
            existing_user = db.query(User).filter(User.email == user.email).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Create new user
        db_user = User(name=user.name, email=user.email)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@app.get("/users/", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all users"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# Portfolio CRUD
@app.post("/portfolio/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def add_portfolio_position(position: PortfolioCreate, db: Session = Depends(get_db)):
    """Add a new portfolio position"""
    try:
        # Verify user exists
        user = db.query(User).filter(User.user_id == position.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create portfolio position
        db_position = Portfolio(
            user_id=position.user_id,
            ticker=position.ticker,
            units=position.units,
            avg_price=position.avg_price,
            buy_date=position.buy_date
        )
        
        db.add(db_position)
        db.commit()
        db.refresh(db_position)
        
        return db_position
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add portfolio position: {str(e)}"
        )

@app.get("/portfolio/{user_id}", response_model=List[PortfolioResponse])
def get_user_portfolio(user_id: int, db: Session = Depends(get_db)):
    """Get all portfolio positions for a user"""
    # Verify user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    positions = (
        db.query(Portfolio)
        .filter(Portfolio.user_id == user_id)
        .order_by(desc(Portfolio.units * Portfolio.avg_price))
        .all()
    )
    
    return positions

# Daily Prices CRUD
@app.post("/prices/", response_model=DailyPriceResponse, status_code=status.HTTP_201_CREATED)
def insert_daily_price(price_data: DailyPriceCreate, db: Session = Depends(get_db)):
    """Insert daily price data"""
    try:
        # Check if price already exists for this ticker and date
        existing_price = (
            db.query(DailyPrice)
            .filter(
                and_(
                    DailyPrice.ticker == price_data.ticker,
                    DailyPrice.price_date == price_data.price_date
                )
            )
            .first()
        )
        
        if existing_price:
            # Update existing price
            existing_price.close_price = price_data.close_price
            existing_price.open_price = price_data.open_price
            existing_price.high_price = price_data.high_price
            existing_price.low_price = price_data.low_price
            existing_price.volume = price_data.volume
            
            db.commit()
            db.refresh(existing_price)
            return existing_price
        else:
            # Create new price record
            db_price = DailyPrice(
                ticker=price_data.ticker,
                price_date=price_data.price_date,
                close_price=price_data.close_price,
                open_price=price_data.open_price,
                high_price=price_data.high_price,
                low_price=price_data.low_price,
                volume=price_data.volume
            )
            
            db.add(db_price)
            db.commit()
            db.refresh(db_price)
            return db_price
            
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to insert daily price: {str(e)}"
        )

@app.get("/prices/{ticker}", response_model=List[DailyPriceResponse])
def get_ticker_prices(
    ticker: str, 
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get daily prices for a ticker"""
    query = db.query(DailyPrice).filter(DailyPrice.ticker == ticker)
    
    if start_date:
        query = query.filter(DailyPrice.price_date >= start_date)
    if end_date:
        query = query.filter(DailyPrice.price_date <= end_date)
    
    prices = (
        query.order_by(desc(DailyPrice.price_date))
        .limit(limit)
        .all()
    )
    
    return prices

# Portfolio Daily Values
@app.get("/daily-values/{user_id}")
def get_portfolio_daily_values(
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get portfolio daily values for a user"""
    # Verify user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    query = (
        db.query(PortfolioDailyValue)
        .join(Portfolio)
        .filter(Portfolio.user_id == user_id)
    )
    
    if start_date:
        query = query.filter(PortfolioDailyValue.date >= start_date)
    if end_date:
        query = query.filter(PortfolioDailyValue.date <= end_date)
    
    daily_values = query.order_by(PortfolioDailyValue.date).all()
    
    # Group by date
    result = {}
    for dv in daily_values:
        date_str = dv.date.isoformat()
        if date_str not in result:
            result[date_str] = {
                "date": date_str,
                "total_value": 0,
                "positions": []
            }
        
        result[date_str]["total_value"] += dv.position_val
        result[date_str]["positions"].append({
            "ticker": dv.portfolio.ticker,
            "units": dv.units,
            "price": dv.price,
            "position_val": dv.position_val
        })
    
    return list(result.values())

# Portfolio Summary
@app.get("/summary/{user_id}", response_model=PortfolioSummaryResponse)
def get_portfolio_summary_by_date(
    user_id: int,
    target_date: date,
    db: Session = Depends(get_db)
):
    """Get total portfolio summary by user and date - Main endpoint requested"""
    
    # Verify user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get portfolio daily values for the specific date
    daily_values = (
        db.query(PortfolioDailyValue, Portfolio.ticker)
        .join(Portfolio)
        .filter(
            and_(
                Portfolio.user_id == user_id,
                PortfolioDailyValue.date == target_date
            )
        )
        .all()
    )
    
    if not daily_values:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No portfolio data found for user {user_id} on {target_date}"
        )
    
    # Calculate total value and build positions list
    total_value = 0
    positions = []
    
    for daily_value, ticker in daily_values:
        total_value += daily_value.position_val
        positions.append(PositionValue(
            ticker=ticker,
            units=daily_value.units,
            price=daily_value.price,
            position_val=daily_value.position_val
        ))
    
    return PortfolioSummaryResponse(
        user_id=user_id,
        date=target_date.isoformat(),
        total_value=total_value,
        positions=positions
    )

@app.get("/summary/{user_id}/range")
def get_portfolio_summary_range(
    user_id: int,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """Get portfolio summary over a date range"""
    
    # Get portfolio summaries from the summary table
    summaries = (
        db.query(PortfolioSummary)
        .filter(
            and_(
                PortfolioSummary.user_id == user_id,
                PortfolioSummary.date >= start_date,
                PortfolioSummary.date <= end_date
            )
        )
        .order_by(PortfolioSummary.date)
        .all()
    )
    
    result = []
    for summary in summaries:
        result.append({
            "date": summary.date.isoformat(),
            "total_value": summary.total_value,
            "total_cost_basis": summary.total_cost_basis,
            "total_gain_loss": summary.total_gain_loss,
            "total_gain_loss_percent": summary.total_gain_loss_percent,
            "num_positions": summary.num_positions
        })
    
    return result

# Bulk operations
@app.post("/prices/bulk")
def bulk_insert_prices(prices: List[DailyPriceCreate], db: Session = Depends(get_db)):
    """Bulk insert daily prices"""
    try:
        inserted_count = 0
        updated_count = 0
        
        for price_data in prices:
            # Check if exists
            existing = (
                db.query(DailyPrice)
                .filter(
                    and_(
                        DailyPrice.ticker == price_data.ticker,
                        DailyPrice.price_date == price_data.price_date
                    )
                )
                .first()
            )
            
            if existing:
                # Update
                existing.close_price = price_data.close_price
                existing.open_price = price_data.open_price
                existing.high_price = price_data.high_price
                existing.low_price = price_data.low_price
                existing.volume = price_data.volume
                updated_count += 1
            else:
                # Insert
                db_price = DailyPrice(
                    ticker=price_data.ticker,
                    price_date=price_data.price_date,
                    close_price=price_data.close_price,
                    open_price=price_data.open_price,
                    high_price=price_data.high_price,
                    low_price=price_data.low_price,
                    volume=price_data.volume
                )
                db.add(db_price)
                inserted_count += 1
        
        db.commit()
        
        return {
            "inserted": inserted_count,
            "updated": updated_count,
            "total": len(prices),
            "status": "success"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk insert failed: {str(e)}"
        )

# Cash Transaction Endpoints
@app.post("/cash-transactions/", response_model=CashTransactionResponse, status_code=status.HTTP_201_CREATED)
def add_cash_transaction(transaction: CashTransactionCreate, db: Session = Depends(get_db)):
    """Add a cash transaction (deposit or withdrawal)"""
    try:
        # Verify user exists
        user = db.query(User).filter(User.user_id == transaction.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Ensure amount is properly signed based on transaction type
        amount = transaction.amount
        if transaction.type == 'withdrawal' and amount > 0:
            amount = -amount
        elif transaction.type == 'deposit' and amount < 0:
            amount = abs(amount)
        
        # Create cash transaction
        cash_transaction = CashTransaction(
            user_id=transaction.user_id,
            amount=amount,
            transaction_date=transaction.transaction_date,
            type=transaction.type,
            description=transaction.description
        )
        
        db.add(cash_transaction)
        db.commit()
        db.refresh(cash_transaction)
        
        return cash_transaction
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add cash transaction: {str(e)}"
        )

@app.get("/cash-transactions/{user_id}", response_model=List[CashTransactionResponse])
def get_user_cash_transactions(user_id: int, db: Session = Depends(get_db)):
    """Get all cash transactions for a user"""
    # Verify user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    transactions = (
        db.query(CashTransaction)
        .filter(CashTransaction.user_id == user_id)
        .order_by(CashTransaction.transaction_date.desc())
        .all()
    )
    
    return transactions

def get_cash_balance(db: Session, user_id: int, target_date: date) -> float:
    """Calculate cumulative cash balance up to target date"""
    
    transactions = (
        db.query(CashTransaction)
        .filter(
            and_(
                CashTransaction.user_id == user_id,
                CashTransaction.transaction_date <= target_date
            )
        )
        .order_by(CashTransaction.transaction_date)
        .all()
    )
    
    cash_balance = 0.0
    
    for transaction in transactions:
        if transaction.type == 'deposit':
            cash_balance += transaction.amount
        elif transaction.type == 'withdrawal':
            cash_balance -= transaction.amount
    
    return cash_balance

# Main Portfolio Endpoint with Cash Balance
@app.get("/portfolio/{user_id}/{target_date}", response_model=PortfolioWithCashResponse)
def get_portfolio_with_cash(
    user_id: int, 
    target_date: date,
    db: Session = Depends(get_db)
):
    """
    Get portfolio summary with cash balance for a specific user and date
    
    Returns the exact format requested:
    {
      "user_id": 101,
      "date": "2025-10-02",
      "total_value": 50500,
      "cash": 5000,
      "positions": [
        {"ticker": "AAPL", "units": 10, "price": 175, "position_val": 1750},
        {"ticker": "BTC-USD", "units": 0.5, "price": 60000, "position_val": 30000},
        {"ticker": "BND", "units": 20, "price": 85, "position_val": 1700}
      ]
    }
    """
    
    # Verify user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get portfolio daily values for the specific date
    daily_values = (
        db.query(PortfolioDailyValue, Portfolio.ticker)
        .join(Portfolio)
        .filter(
            and_(
                Portfolio.user_id == user_id,
                PortfolioDailyValue.date == target_date,
                ~Portfolio.ticker.startswith('CASH')  # Exclude cash positions
            )
        )
        .all()
    )
    
    # Calculate cash balance
    cash_balance = get_cash_balance(db, user_id, target_date)
    
    # Build positions list and calculate portfolio total
    positions = []
    portfolio_total = 0.0
    
    for daily_value, ticker in daily_values:
        portfolio_total += daily_value.position_val
        positions.append(PositionValue(
            ticker=ticker,
            units=daily_value.units,
            price=daily_value.price,
            position_val=daily_value.position_val
        ))
    
    # Calculate total value (portfolio + cash)
    total_value = portfolio_total + cash_balance
    
    if not positions and cash_balance == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No portfolio data found for user {user_id} on {target_date}"
        )
    
    return PortfolioWithCashResponse(
        user_id=user_id,
        date=target_date.isoformat(),
        total_value=total_value,
        cash=cash_balance,
        positions=positions
    )

@app.get("/cash-balance/{user_id}/{target_date}")
def get_cash_balance_endpoint(
    user_id: int,
    target_date: date,
    db: Session = Depends(get_db)
):
    """Get cash balance for a user on a specific date"""
    
    # Verify user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    cash_balance = get_cash_balance(db, user_id, target_date)
    
    return {
        "user_id": user_id,
        "date": target_date.isoformat(),
        "cash_balance": cash_balance
    }

if __name__ == "__main__":
    print("🚀 Starting Portfolio API - Normalized Database")
    print("📊 Complete CRUD operations with efficient queries")
    uvicorn.run(app, host="127.0.0.1", port=8002, reload=True)
