"""
Perfect Portfolio Database Models - Normalized Schema
Clean, efficient, and calculation-friendly structure
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import date, datetime
from typing import Optional

Base = declarative_base()

class User(Base):
    """Users table - Clean and simple"""
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True)
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    portfolio_summaries = relationship("PortfolioSummary", back_populates="user", cascade="all, delete-orphan")
    cash_transactions = relationship("CashTransaction", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, name='{self.name}')>"

class Portfolio(Base):
    """Portfolio holdings - Core positions"""
    __tablename__ = "portfolio"
    
    portfolio_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    asset_class = Column(String(20), nullable=True)  # STOCK, BOND_ETF, CRYPTO, CASH, BOND_CASH
    units = Column(Float, nullable=False)  # Number of shares/units
    avg_price = Column(Float, nullable=False)  # Average purchase price
    buy_date = Column(Date, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    daily_values = relationship("PortfolioDailyValue", back_populates="portfolio", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_portfolio_user_ticker', 'user_id', 'ticker'),
        Index('idx_portfolio_ticker_date', 'ticker', 'buy_date'),
    )
    
    @hybrid_property
    def cost_basis(self) -> float:
        """Calculate total cost basis"""
        return self.units * self.avg_price
    
    def current_value(self, current_price: float) -> float:
        """Calculate current position value"""
        return self.units * current_price
    
    def gain_loss(self, current_price: float) -> float:
        """Calculate absolute gain/loss"""
        return self.current_value(current_price) - self.cost_basis
    
    def gain_loss_percent(self, current_price: float) -> float:
        """Calculate percentage gain/loss"""
        if self.cost_basis == 0:
            return 0.0
        return (self.gain_loss(current_price) / self.cost_basis) * 100
    
    def __repr__(self):
        return f"<Portfolio(portfolio_id={self.portfolio_id}, ticker='{self.ticker}', units={self.units})>"

class DailyPrice(Base):
    """Daily market prices for all tickers"""
    __tablename__ = "daily_prices"
    
    price_id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    price_date = Column(Date, nullable=False, index=True)
    close_price = Column(Float, nullable=False)
    
    # Additional OHLCV data (optional)
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)
    
    # Composite indexes for efficient queries
    __table_args__ = (
        Index('idx_daily_prices_ticker_date', 'ticker', 'price_date', unique=True),
        Index('idx_daily_prices_date', 'price_date'),
    )
    
    def __repr__(self):
        return f"<DailyPrice(ticker='{self.ticker}', date='{self.price_date}', price=${self.close_price:.2f})>"

class PortfolioDailyValue(Base):
    """Daily portfolio position values - Pre-calculated for performance"""
    __tablename__ = "portfolio_daily_value"
    
    value_id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolio.portfolio_id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    units = Column(Float, nullable=False)  # Units held on this date
    price = Column(Float, nullable=False)  # Market price on this date
    position_val = Column(Float, nullable=False)  # Total position value (units * price)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="daily_values")
    
    # Indexes for time-series queries
    __table_args__ = (
        Index('idx_portfolio_daily_portfolio_date', 'portfolio_id', 'date', unique=True),
        Index('idx_portfolio_daily_date', 'date'),
    )
    
    @hybrid_property
    def calculated_value(self) -> float:
        """Verify calculated value matches stored value"""
        return self.units * self.price
    
    def __repr__(self):
        return f"<PortfolioDailyValue(portfolio_id={self.portfolio_id}, date='{self.date}', value=${self.position_val:.2f})>"

class PortfolioSummary(Base):
    """Daily portfolio summary - Aggregated totals for performance"""
    __tablename__ = "portfolio_summary"
    
    summary_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    total_value = Column(Float, nullable=False)
    
    # Asset class breakdowns
    equity_value = Column(Float, nullable=True, default=0.0)  # STOCK positions
    bond_etf_value = Column(Float, nullable=True, default=0.0)  # BOND_ETF positions
    crypto_value = Column(Float, nullable=True, default=0.0)  # CRYPTO positions
    cash_value = Column(Float, nullable=True, default=0.0)  # CASH from transactions
    bond_cash_value = Column(Float, nullable=True, default=0.0)  # BOND_CASH positions
    
    # Additional summary metrics (optional but useful)
    total_cost_basis = Column(Float, nullable=True)
    total_gain_loss = Column(Float, nullable=True)
    total_gain_loss_percent = Column(Float, nullable=True)
    num_positions = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="portfolio_summaries")
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_portfolio_summary_user_date', 'user_id', 'date', unique=True),
        Index('idx_portfolio_summary_date', 'date'),
    )
    
    def __repr__(self):
        return f"<PortfolioSummary(user_id={self.user_id}, date='{self.date}', value=${self.total_value:.2f})>"

# Additional utility models for enhanced functionality

class CashTransaction(Base):
    """Cash transactions for tracking deposits and withdrawals"""
    __tablename__ = "cash_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)  # Positive for deposits, negative for withdrawals
    transaction_date = Column(Date, nullable=False, index=True)
    type = Column(String(20), nullable=False)  # "deposit" or "withdrawal"
    description = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="cash_transactions")
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_cash_user_date', 'user_id', 'transaction_date'),
        Index('idx_cash_date', 'transaction_date'),
    )
    
    def __repr__(self):
        return f"<CashTransaction(user_id={self.user_id}, type='{self.type}', amount=${self.amount:.2f})>"

class AssetCategory(Base):
    """Asset categories for better organization"""
    __tablename__ = "asset_categories"
    
    category_id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), nullable=False, unique=True, index=True)
    category = Column(String(50), nullable=False)  # Stock, ETF, Bond, Crypto, Cash, etc.
    sector = Column(String(100), nullable=True)    # Technology, Healthcare, etc.
    industry = Column(String(100), nullable=True)  # Software, Pharmaceuticals, etc.
    
    def __repr__(self):
        return f"<AssetCategory(ticker='{self.ticker}', category='{self.category}')>"

class PortfolioTransaction(Base):
    """Transaction history for audit trail"""
    __tablename__ = "portfolio_transactions"
    
    transaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    transaction_type = Column(String(10), nullable=False)  # BUY, SELL, DIVIDEND
    units = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    transaction_date = Column(Date, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_transactions_user_date', 'user_id', 'transaction_date'),
        Index('idx_transactions_ticker_date', 'ticker', 'transaction_date'),
    )
    
    @hybrid_property
    def transaction_value(self) -> float:
        """Calculate transaction value"""
        return self.units * self.price
    
    def __repr__(self):
        return f"<PortfolioTransaction(ticker='{self.ticker}', type='{self.transaction_type}', units={self.units})>"

# Database utility functions
def create_all_tables(engine):
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def drop_all_tables(engine):
    """Drop all tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
