from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
import hashlib

class TransactionType(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    logins = relationship("Login", back_populates="user")
    portfolios = relationship("Portfolio", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

class Login(Base):
    __tablename__ = "logins"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="logins")

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticker = Column(String(20), nullable=False)
    shares = Column(Float, nullable=False, default=0.0)
    avg_price = Column(Float, nullable=False, default=0.0)
    
    # Relationships
    user = relationship("User", back_populates="portfolios")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticker = Column(String(20), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")

class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    sector = Column(String(100), nullable=True)
    last_price = Column(Float, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class HistoricalData(Base):
    __tablename__ = "historical_data"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=True)
    adjusted_close = Column(Float, nullable=True)
    asset_type = Column(String(20), nullable=False, default="stock")  # stock, crypto, etf
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Composite index for efficient queries
    __table_args__ = (
        {"extend_existing": True}
    )

class PortfolioSummary(Base):
    __tablename__ = "portfolio_summary"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    total_value = Column(Float, nullable=False)
    total_cost_basis = Column(Float, nullable=False)
    total_gain_loss = Column(Float, nullable=False)
    total_gain_loss_percent = Column(Float, nullable=False)
    one_year_cagr = Column(Float, nullable=True)
    total_holdings = Column(Integer, nullable=False)
    stock_value = Column(Float, nullable=False, default=0)
    crypto_value = Column(Float, nullable=False, default=0)
    etf_value = Column(Float, nullable=False, default=0)
    bond_value = Column(Float, nullable=False, default=0)
    cash_value = Column(Float, nullable=False, default=0)
    latest_date = Column(DateTime(timezone=True), nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        {"extend_existing": True}
    )

class PortfolioProjections(Base):
    __tablename__ = "portfolio_projections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    period = Column(String(20), nullable=False, index=True)  # 1Week, 1Month, YTD, 1Year
    projected_value = Column(Float, nullable=False)
    projected_return = Column(Float, nullable=False)  # percentage
    projected_gain_loss = Column(Float, nullable=False)
    confidence_level = Column(Float, nullable=False, default=0.95)  # 95% confidence
    volatility = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    calculation_date = Column(DateTime(timezone=True), server_default=func.now())
    projection_date = Column(DateTime(timezone=True), nullable=False)  # target date
    
    __table_args__ = (
        {"extend_existing": True}
    )

class PortfolioPerformance(Base):
    __tablename__ = "portfolio_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    period = Column(String(20), nullable=False, index=True)  # 1Week, 1Month, YTD, 1Year
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    start_value = Column(Float, nullable=False)
    end_value = Column(Float, nullable=False)
    total_return = Column(Float, nullable=False)  # percentage
    total_gain_loss = Column(Float, nullable=False)
    annualized_return = Column(Float, nullable=True)
    volatility = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    calculation_date = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        {"extend_existing": True}
    )

class PortfolioChartData(Base):
    __tablename__ = "portfolio_chart_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    period = Column(String(20), nullable=False, index=True)  # 1Week, 1Month, YTD, 1Year
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    total_value = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        {"extend_existing": True}
    )

class PortfolioValues(Base):
    __tablename__ = "portfolio_values"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    current_price = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    cost_basis = Column(Float, nullable=False)
    gain_loss = Column(Float, nullable=False)
    gain_loss_percent = Column(Float, nullable=False)
    category = Column(String(50), nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        {"extend_existing": True}
    )

class TopHoldings(Base):
    __tablename__ = "top_holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    type = Column(String(20), nullable=False, index=True)  # 'holdings' or 'movers'
    rank = Column(Integer, nullable=False)  # 1, 2, 3
    ticker = Column(String(20), nullable=False)
    shares = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    gain_loss = Column(Float, nullable=False)
    gain_loss_percent = Column(Float, nullable=False)
    calculation_date = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        {"extend_existing": True}
    )

class InsightsCache(Base):
    __tablename__ = "insights_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metrics_hash = Column(String(64), nullable=False, index=True)  # SHA-256 hash of metrics
    insights_text = Column(Text, nullable=False)
    is_ai_generated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    
    __table_args__ = (
        {"extend_existing": True}
    )
