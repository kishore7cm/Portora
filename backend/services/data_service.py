"""
Data Service - Perfect Data Layer
Clean, efficient, single responsibility
"""

import pandas as pd
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import date, datetime
from pathlib import Path

from domain.models import User, PortfolioHolding, MarketData
from core.config import settings
from core.logging import logger

class DataService:
    """Perfect data service - single source of truth"""
    
    def __init__(self, db: Session):
        self.db = db
        self.csv_path = settings.CSV_PATH
    
    # User operations
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_user(self, name: str, email: str) -> User:
        """Create new user"""
        user = User(name=name, email=email)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        logger.info(f"Created user: {user.name}")
        return user
    
    # Portfolio operations
    def get_portfolio_holdings(self, user_id: int) -> List[PortfolioHolding]:
        """Get all portfolio holdings for user"""
        return (
            self.db.query(PortfolioHolding)
            .filter(PortfolioHolding.user_id == user_id)
            .order_by(desc(PortfolioHolding.total_value))
            .all()
        )
    
    def get_holding_by_ticker(self, user_id: int, ticker: str) -> Optional[PortfolioHolding]:
        """Get specific holding by ticker"""
        return (
            self.db.query(PortfolioHolding)
            .filter(
                and_(
                    PortfolioHolding.user_id == user_id,
                    PortfolioHolding.ticker == ticker
                )
            )
            .first()
        )
    
    def update_holding_price(self, user_id: int, ticker: str, new_price: float) -> bool:
        """Update holding with new price"""
        try:
            holding = self.get_holding_by_ticker(user_id, ticker)
            if not holding:
                logger.warning(f"Holding not found: {ticker} for user {user_id}")
                return False
            
            old_price = holding.current_price
            holding.update_price(new_price)
            
            self.db.commit()
            logger.debug(f"Updated {ticker}: ${old_price:.2f} → ${new_price:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update {ticker}: {e}")
            self.db.rollback()
            return False
    
    # Market data operations
    def load_csv_data(self) -> pd.DataFrame:
        """Load historical data from CSV with caching"""
        try:
            if not Path(self.csv_path).exists():
                logger.error(f"CSV file not found: {self.csv_path}")
                return pd.DataFrame()
            
            df = pd.read_csv(self.csv_path)
            df['date'] = pd.to_datetime(df['date']).dt.date
            logger.debug(f"Loaded {len(df)} records from CSV")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            return pd.DataFrame()
    
    def get_price_on_date(self, ticker: str, target_date: date) -> Optional[float]:
        """Get price for ticker on specific date"""
        df = self.load_csv_data()
        if df.empty:
            return None
        
        price_data = df[
            (df['ticker'] == ticker) & 
            (df['date'] == target_date)
        ]
        
        if not price_data.empty:
            return float(price_data['close'].iloc[0])
        
        logger.debug(f"No price data for {ticker} on {target_date}")
        return None
    
    def get_latest_price(self, ticker: str) -> Optional[float]:
        """Get latest price for ticker from CSV"""
        df = self.load_csv_data()
        if df.empty:
            return None
        
        ticker_data = df[df['ticker'] == ticker].sort_values('date')
        if not ticker_data.empty:
            latest_price = float(ticker_data['close'].iloc[-1])
            latest_date = ticker_data['date'].iloc[-1]
            logger.debug(f"Latest {ticker}: ${latest_price:.2f} on {latest_date}")
            return latest_price
        
        logger.debug(f"No data found for ticker: {ticker}")
        return None
    
    def get_price_range(self, ticker: str, start_date: date, end_date: date) -> pd.DataFrame:
        """Get price data for ticker in date range"""
        df = self.load_csv_data()
        if df.empty:
            return pd.DataFrame()
        
        return df[
            (df['ticker'] == ticker) &
            (df['date'] >= start_date) &
            (df['date'] <= end_date)
        ].sort_values('date')
    
    # Database market data operations (for future use)
    def store_market_data(self, ticker: str, date: datetime, ohlcv: Dict[str, float]) -> MarketData:
        """Store market data in database"""
        market_data = MarketData(
            ticker=ticker,
            date=date,
            open_price=ohlcv['open'],
            high_price=ohlcv['high'],
            low_price=ohlcv['low'],
            close_price=ohlcv['close'],
            volume=ohlcv.get('volume', 0)
        )
        
        self.db.add(market_data)
        self.db.commit()
        self.db.refresh(market_data)
        return market_data
    
    def get_market_data(self, ticker: str, start_date: date, end_date: date) -> List[MarketData]:
        """Get market data from database"""
        return (
            self.db.query(MarketData)
            .filter(
                and_(
                    MarketData.ticker == ticker,
                    MarketData.date >= start_date,
                    MarketData.date <= end_date
                )
            )
            .order_by(MarketData.date)
            .all()
        )
    
    # Health check
    def health_check(self) -> Dict[str, any]:
        """Check data service health"""
        try:
            # Test database
            user_count = self.db.query(User).count()
            holding_count = self.db.query(PortfolioHolding).count()
            
            # Test CSV
            df = self.load_csv_data()
            csv_records = len(df)
            
            return {
                "database": {
                    "users": user_count,
                    "holdings": holding_count,
                    "status": "healthy"
                },
                "csv": {
                    "records": csv_records,
                    "path": self.csv_path,
                    "status": "healthy" if csv_records > 0 else "no_data"
                },
                "overall_status": "healthy"
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "database": {"status": "error", "error": str(e)},
                "csv": {"status": "error"},
                "overall_status": "unhealthy"
            }