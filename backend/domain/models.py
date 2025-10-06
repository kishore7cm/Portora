"""
Domain Models - The Perfect Way
Clean, focused, business-oriented
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, func
from core.database import Base
from typing import Optional
from datetime import datetime

class User(Base):
    """User model - using existing table structure"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}')>"

class PortfolioHolding(Base):
    """Portfolio holding model - clean and focused"""
    __tablename__ = "portfolio_values"  # Use existing table name
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    
    # Core data
    current_price = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    cost_basis = Column(Float, nullable=False)
    
    # Calculated fields
    gain_loss = Column(Float, nullable=False)
    gain_loss_percent = Column(Float, nullable=False)
    
    # Metadata
    category = Column(String(50), default="Stock")
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes for performance
    __table_args__ = (
        {"extend_existing": True}
    )
    
    @property
    def shares(self) -> float:
        """Calculate shares from total_value and current_price"""
        return self.total_value / self.current_price if self.current_price > 0 else 0
    
    @property
    def avg_price(self) -> float:
        """Calculate average price from cost_basis and shares"""
        shares = self.shares
        return self.cost_basis / shares if shares > 0 else 0
    
    def update_price(self, new_price: float) -> None:
        """Update holding with new price"""
        shares = self.shares
        self.current_price = new_price
        self.total_value = shares * new_price
        self.gain_loss = self.total_value - self.cost_basis
        self.gain_loss_percent = (self.gain_loss / self.cost_basis) * 100 if self.cost_basis > 0 else 0
    
    def __repr__(self):
        return f"<PortfolioHolding(ticker='{self.ticker}', value=${self.total_value:.2f})>"

class MarketData(Base):
    """Market data model for historical prices"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # OHLCV data
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, default=0)
    
    # Metadata
    source = Column(String(50), default="CSV")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Composite index for performance
    __table_args__ = (
        {"extend_existing": True}
    )
    
    def __repr__(self):
        return f"<MarketData(ticker='{self.ticker}', date='{self.date}', close=${self.close_price:.2f})>"
