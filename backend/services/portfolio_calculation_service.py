"""
Portfolio Calculation Service - Canonical Implementation
Follows strict rules for asset classification, pricing, and calculations
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import os
import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from decimal import Decimal, ROUND_HALF_UP
import statistics
import math
import requests
import time
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, text

# Database imports
from core.database import SessionLocal
from domain.models_v2 import Portfolio, DailyPrice, PortfolioDailyValue, PortfolioSummary, CashTransaction, User

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Asset class constants
ASSET_CLASSES = {
    'STOCK': 'STOCK',
    'BOND_ETF': 'BOND_ETF', 
    'CRYPTO': 'CRYPTO',
    'CASH': 'CASH',
    'BOND_CASH': 'BOND_CASH'
}

@dataclass
class PositionSnapshot:
    portfolio_id: int
    ticker: str
    asset_class: str
    units: Decimal
    price: Optional[Decimal]
    position_val: Decimal
    missing_price: bool
    price_date: Optional[date] = None

@dataclass
class PortfolioSnapshot:
    date: date
    by_position: List[PositionSnapshot]
    by_class: Dict[str, Decimal]
    total_value: Decimal
    missing_prices: List[Dict[str, Any]]

class PortfolioCalculationService:
    """Canonical portfolio calculation service with strict rules"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # API credentials from environment
        self.alpaca_api_key = os.getenv('ALPACA_API_KEY')
        self.alpaca_secret_key = os.getenv('ALPACA_SECRET_KEY')
        self.twelve_data_api_key = os.getenv('TWELVE_DATA_API_KEY')
        
        # API endpoints
        self.alpaca_base_url = "https://paper-api.alpaca.markets"
        self.twelve_data_base_url = "https://api.twelvedata.com"
    
    def classify_asset(self, ticker: str, portfolio_asset_class: Optional[str] = None) -> str:
        """
        Classify asset type following canonical rules
        1. Check portfolio.asset_class first if available
        2. Fall back to ticker-based classification
        """
        if portfolio_asset_class and portfolio_asset_class in ASSET_CLASSES.values():
            return portfolio_asset_class
        
        # Known bond ETFs
        bond_etfs = {
            'BND', 'AGG', 'TLT', 'IEF', 'SHY', 'VGIT', 'VGLT', 'VTEB', 
            'MUB', 'HYG', 'JNK', 'LQD', 'VCIT', 'VCLT', 'BSV', 'BIV', 'BLV'
        }
        
        # Crypto symbols
        crypto_symbols = {
            'BTC-USD', 'ETH-USD', 'BTC', 'ETH', 'ADA-USD', 'SOL-USD', 
            'DOT-USD', 'AVAX-USD', 'MATIC-USD', 'LINK-USD'
        }
        
        if ticker.startswith('CASH') or ticker == 'CASH':
            return ASSET_CLASSES['CASH']
        elif ticker.startswith('BOND_CASH'):
            return ASSET_CLASSES['BOND_CASH']
        elif ticker in crypto_symbols or 'USD' in ticker:
            return ASSET_CLASSES['CRYPTO']
        elif ticker in bond_etfs:
            return ASSET_CLASSES['BOND_ETF']
        else:
            return ASSET_CLASSES['STOCK']
    
    def latest_price(self, ticker: str, as_of: date) -> Optional[Tuple[Decimal, date]]:
        """
        Get latest available price <= as_of_date
        Returns (price, price_date) or None if not found
        """
        result = (
            self.db.query(DailyPrice.close_price, DailyPrice.price_date)
            .filter(
                and_(
                    DailyPrice.ticker == ticker,
                    DailyPrice.price_date <= as_of
                )
            )
            .order_by(DailyPrice.price_date.desc())
            .first()
        )
        
        if result:
            return Decimal(str(result[0])), result[1]
        return None
    
    def cash_balance(self, user_id: int, as_of: date) -> Decimal:
        """Calculate cumulative cash balance from transactions <= as_of"""
        transactions = (
            self.db.query(CashTransaction)
            .filter(
                and_(
                    CashTransaction.user_id == user_id,
                    CashTransaction.transaction_date <= as_of
                )
            )
            .all()
        )
        
        balance = Decimal('0')
        for txn in transactions:
            if txn.type == 'deposit':
                balance += Decimal(str(txn.amount))
            elif txn.type == 'withdrawal':
                balance -= Decimal(str(txn.amount))
        
        return balance
    
    def bond_cash_value(self, user_id: int) -> Decimal:
        """Sum of units * avg_price for BOND_CASH positions (no daily repricing)"""
        positions = (
            self.db.query(Portfolio)
            .filter(
                and_(
                    Portfolio.user_id == user_id,
                    Portfolio.ticker.like('BOND_CASH%')
                )
            )
            .all()
        )
        
        total = Decimal('0')
        for pos in positions:
            asset_class = self.classify_asset(pos.ticker)
            if asset_class == ASSET_CLASSES['BOND_CASH']:
                total += Decimal(str(pos.units)) * Decimal(str(pos.avg_price))
        
        return total
    
    def fetch_alpaca_prices(self, ticker: str, start_date: date, end_date: date) -> List[Dict]:
        """Fetch daily prices from Alpaca API"""
        if not self.alpaca_api_key or not self.alpaca_secret_key:
            logger.warning(f"Alpaca credentials missing for {ticker}")
            return []
        
        headers = {
            'APCA-API-KEY-ID': self.alpaca_api_key,
            'APCA-API-SECRET-KEY': self.alpaca_secret_key
        }
        
        url = f"{self.alpaca_base_url}/v2/stocks/{ticker}/bars"
        params = {
            'start': start_date.isoformat(),
            'end': end_date.isoformat(),
            'timeframe': '1Day',
            'adjustment': 'raw',
            'feed': 'iex'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            prices = []
            for bar in data.get('bars', []):
                price_date = datetime.fromisoformat(bar['t'].replace('Z', '+00:00')).date()
                prices.append({
                    'ticker': ticker,
                    'price_date': price_date,
                    'close_price': Decimal(str(bar['c']))
                })
            
            return prices
            
        except Exception as e:
            logger.error(f"Alpaca API error for {ticker}: {e}")
            return []
    
    def fetch_twelve_data_prices(self, ticker: str, start_date: date, end_date: date) -> List[Dict]:
        """Fetch daily prices from Twelve Data API"""
        if not self.twelve_data_api_key:
            logger.warning(f"Twelve Data API key missing for {ticker}")
            return []
        
        url = f"{self.twelve_data_base_url}/time_series"
        params = {
            'symbol': ticker,
            'interval': '1day',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'apikey': self.twelve_data_api_key,
            'format': 'JSON'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            prices = []
            for item in data.get('values', []):
                price_date = datetime.strptime(item['datetime'], '%Y-%m-%d').date()
                prices.append({
                    'ticker': ticker,
                    'price_date': price_date,
                    'close_price': Decimal(str(item['close']))
                })
            
            return prices
            
        except Exception as e:
            logger.error(f"Twelve Data API error for {ticker}: {e}")
            return []
    
    def update_daily_prices(self, stock_tickers: List[str], bond_etf_tickers: List[str], 
                          crypto_tickers: List[str], as_of: Optional[date] = None) -> Dict[str, int]:
        """
        Update daily prices following canonical rules
        Returns counts inserted per ticker
        """
        if as_of is None:
            as_of = date.today()
        
        results = {}
        all_prices = []
        
        # Process equity tickers (stocks + bond ETFs) via Alpaca
        equity_tickers = stock_tickers + bond_etf_tickers
        for ticker in equity_tickers:
            try:
                # Get last saved date
                last_date = (
                    self.db.query(func.max(DailyPrice.price_date))
                    .filter(DailyPrice.ticker == ticker)
                    .scalar()
                )
                
                if last_date is None:
                    # Fetch 365 days of history
                    start_date = as_of - timedelta(days=365)
                else:
                    start_date = last_date + timedelta(days=1)
                
                if start_date > as_of:
                    results[ticker] = 0
                    continue
                
                prices = self.fetch_alpaca_prices(ticker, start_date, as_of)
                all_prices.extend(prices)
                results[ticker] = len(prices)
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error updating {ticker}: {e}")
                results[ticker] = 0
        
        # Process crypto tickers via Twelve Data
        for ticker in crypto_tickers:
            try:
                # Get last saved date
                last_date = (
                    self.db.query(func.max(DailyPrice.price_date))
                    .filter(DailyPrice.ticker == ticker)
                    .scalar()
                )
                
                if last_date is None:
                    # Fetch 365 days of history
                    start_date = as_of - timedelta(days=365)
                else:
                    start_date = last_date + timedelta(days=1)
                
                if start_date > as_of:
                    results[ticker] = 0
                    continue
                
                prices = self.fetch_twelve_data_prices(ticker, start_date, as_of)
                all_prices.extend(prices)
                results[ticker] = len(prices)
                
                # Rate limiting
                time.sleep(0.2)
                
            except Exception as e:
                logger.error(f"Error updating crypto {ticker}: {e}")
                results[ticker] = 0
        
        # Bulk upsert prices
        inserted_count = 0
        for price_data in all_prices:
            try:
                # Check if exists
                existing = (
                    self.db.query(DailyPrice)
                    .filter(
                        and_(
                            DailyPrice.ticker == price_data['ticker'],
                            DailyPrice.price_date == price_data['price_date']
                        )
                    )
                    .first()
                )
                
                if existing:
                    # Update
                    existing.close_price = float(price_data['close_price'])
                else:
                    # Insert
                    new_price = DailyPrice(
                        ticker=price_data['ticker'],
                        price_date=price_data['price_date'],
                        close_price=float(price_data['close_price'])
                    )
                    self.db.add(new_price)
                    inserted_count += 1
                    
            except Exception as e:
                logger.error(f"Error inserting price: {e}")
        
        self.db.commit()
        logger.info(f"Inserted {inserted_count} new price records")
        
        return results
    
    def compute_portfolio_snapshot(self, user_id: int, as_of: date) -> PortfolioSnapshot:
        """
        Compute portfolio snapshot following canonical rules
        """
        # Get all positions for user
        positions = (
            self.db.query(Portfolio)
            .filter(Portfolio.user_id == user_id)
            .all()
        )
        
        by_position = []
        by_class = {
            'equity_value': Decimal('0'),
            'bond_etf_value': Decimal('0'),
            'crypto_value': Decimal('0'),
            'bond_cash_value': Decimal('0'),
            'cash': Decimal('0')
        }
        missing_prices = []
        
        # Process each position
        for pos in positions:
            asset_class = self.classify_asset(pos.ticker, getattr(pos, 'asset_class', None))
            units = Decimal(str(pos.units))
            
            if asset_class in [ASSET_CLASSES['STOCK'], ASSET_CLASSES['BOND_ETF'], ASSET_CLASSES['CRYPTO']]:
                # Get latest price
                price_result = self.latest_price(pos.ticker, as_of)
                
                if price_result:
                    price, price_date = price_result
                    position_val = units * price
                    missing_price = False
                    
                    # Check if price is stale
                    days_old = (as_of - price_date).days
                    is_stale = (
                        (asset_class == ASSET_CLASSES['CRYPTO'] and days_old > 1) or
                        (asset_class in [ASSET_CLASSES['STOCK'], ASSET_CLASSES['BOND_ETF']] and days_old > 3)
                    )
                    
                    if is_stale:
                        missing_prices.append({
                            'ticker': pos.ticker,
                            'last_price_date': price_date.isoformat(),
                            'days_old': days_old,
                            'reason': 'stale'
                        })
                else:
                    price = None
                    price_date = None
                    position_val = Decimal('0')
                    missing_price = True
                    
                    missing_prices.append({
                        'ticker': pos.ticker,
                        'last_price_date': None,
                        'reason': 'missing'
                    })
                
                # Add to class totals
                if asset_class == ASSET_CLASSES['STOCK']:
                    by_class['equity_value'] += position_val
                elif asset_class == ASSET_CLASSES['BOND_ETF']:
                    by_class['bond_etf_value'] += position_val
                elif asset_class == ASSET_CLASSES['CRYPTO']:
                    by_class['crypto_value'] += position_val
                
            elif asset_class == ASSET_CLASSES['BOND_CASH']:
                # Use avg_price, no daily repricing
                price = Decimal(str(pos.avg_price))
                position_val = units * price
                missing_price = False
                price_date = None
                
                by_class['bond_cash_value'] += position_val
                
            elif asset_class == ASSET_CLASSES['CASH']:
                # Skip CASH positions, handled separately
                continue
            
            by_position.append(PositionSnapshot(
                portfolio_id=pos.portfolio_id,
                ticker=pos.ticker,
                asset_class=asset_class,
                units=units,
                price=price,
                position_val=position_val,
                missing_price=missing_price,
                price_date=price_date
            ))
        
        # Add cash from transactions
        by_class['cash'] = self.cash_balance(user_id, as_of)
        
        # Calculate total
        total_value = sum(by_class.values())
        
        return PortfolioSnapshot(
            date=as_of,
            by_position=by_position,
            by_class=by_class,
            total_value=total_value,
            missing_prices=missing_prices
        )
    
    def upsert_daily_snapshot(self, user_id: int, as_of: date) -> PortfolioSnapshot:
        """
        Compute and persist daily snapshot
        """
        snapshot = self.compute_portfolio_snapshot(user_id, as_of)
        
        # Upsert portfolio_daily_value for each position
        for pos in snapshot.by_position:
            existing = (
                self.db.query(PortfolioDailyValue)
                .filter(
                    and_(
                        PortfolioDailyValue.portfolio_id == pos.portfolio_id,
                        PortfolioDailyValue.date == as_of
                    )
                )
                .first()
            )
            
            if existing:
                existing.units = float(pos.units)
                existing.price = float(pos.price) if pos.price else None
                existing.position_val = float(pos.position_val)
            else:
                new_value = PortfolioDailyValue(
                    portfolio_id=pos.portfolio_id,
                    date=as_of,
                    units=float(pos.units),
                    price=float(pos.price) if pos.price else None,
                    position_val=float(pos.position_val)
                )
                self.db.add(new_value)
        
        # Upsert portfolio_summary
        existing_summary = (
            self.db.query(PortfolioSummary)
            .filter(
                and_(
                    PortfolioSummary.user_id == user_id,
                    PortfolioSummary.date == as_of
                )
            )
            .first()
        )
        
        if existing_summary:
            existing_summary.total_value = float(snapshot.total_value)
            existing_summary.equity_value = float(snapshot.by_class['equity_value'])
            existing_summary.bond_etf_value = float(snapshot.by_class['bond_etf_value'])
            existing_summary.crypto_value = float(snapshot.by_class['crypto_value'])
            existing_summary.cash_value = float(snapshot.by_class['cash'])
            existing_summary.bond_cash_value = float(snapshot.by_class['bond_cash_value'])
        else:
            new_summary = PortfolioSummary(
                user_id=user_id,
                date=as_of,
                total_value=float(snapshot.total_value),
                equity_value=float(snapshot.by_class['equity_value']),
                bond_etf_value=float(snapshot.by_class['bond_etf_value']),
                crypto_value=float(snapshot.by_class['crypto_value']),
                cash_value=float(snapshot.by_class['cash']),
                bond_cash_value=float(snapshot.by_class['bond_cash_value'])
            )
            self.db.add(new_summary)
        
        self.db.commit()
        return snapshot
    
    def portfolio_created_date(self, user_id: int) -> Optional[date]:
        """Return earliest buy_date for user's portfolio"""
        result = (
            self.db.query(func.min(Portfolio.buy_date))
            .filter(Portfolio.user_id == user_id)
            .scalar()
        )
        return result
    
    def starting_value(self, user_id: int) -> Decimal:
        """Get portfolio value at creation date"""
        created_date = self.portfolio_created_date(user_id)
        if not created_date:
            return Decimal('0')
        
        # Ensure snapshot exists
        snapshot = self.upsert_daily_snapshot(user_id, created_date)
        return snapshot.total_value
    
    def current_value(self, user_id: int, as_of: date) -> Decimal:
        """Get current portfolio value"""
        snapshot = self.upsert_daily_snapshot(user_id, as_of)
        return snapshot.total_value
    
    def net_worth(self, user_id: int, as_of: date) -> Decimal:
        """Alias to current_value"""
        return self.current_value(user_id, as_of)
    
    def total_gain_loss(self, user_id: int, as_of: date) -> Decimal:
        """Calculate total gain/loss"""
        return self.current_value(user_id, as_of) - self.starting_value(user_id)
    
    def return_pct(self, user_id: int, as_of: date) -> Optional[Decimal]:
        """Calculate return percentage"""
        v0 = self.starting_value(user_id)
        if v0 <= 0:
            return None
        
        vt = self.current_value(user_id, as_of)
        return (vt - v0) / v0 * Decimal('100')
    
    def allocation_breakdown(self, user_id: int, as_of: date) -> Dict[str, Decimal]:
        """Get allocation percentages"""
        snapshot = self.compute_portfolio_snapshot(user_id, as_of)
        
        if snapshot.total_value <= 0:
            return {'stock': Decimal('0'), 'bond': Decimal('0'), 'crypto': Decimal('0'), 'cash': Decimal('0')}
        
        return {
            'stock': (snapshot.by_class['equity_value'] / snapshot.total_value * Decimal('100')),
            'bond': (snapshot.by_class['bond_etf_value'] / snapshot.total_value * Decimal('100')),
            'crypto': (snapshot.by_class['crypto_value'] / snapshot.total_value * Decimal('100')),
            'cash': ((snapshot.by_class['cash'] + snapshot.by_class['bond_cash_value']) / snapshot.total_value * Decimal('100'))
        }
    
    def top_holdings(self, user_id: int, as_of: date, k: int = 3) -> List[Dict]:
        """Get top k holdings by value"""
        snapshot = self.compute_portfolio_snapshot(user_id, as_of)
        
        # Sort by position value and take top k
        sorted_positions = sorted(
            snapshot.by_position,
            key=lambda x: x.position_val,
            reverse=True
        )
        
        return [
            {
                'ticker': pos.ticker,
                'units': float(pos.units),
                'price': float(pos.price) if pos.price else None,
                'position_val': float(pos.position_val)
            }
            for pos in sorted_positions[:k]
        ]
    
    def round_decimal(self, value: Decimal, places: int = 2) -> float:
        """Round decimal to specified places for response boundary"""
        if value is None:
            return None
        quantizer = Decimal('0.01') if places == 2 else Decimal('0.0001')
        return float(value.quantize(quantizer, rounding=ROUND_HALF_UP))

# Create service instance
def get_portfolio_service(db: Session = None) -> PortfolioCalculationService:
    if db is None:
        db = SessionLocal()
    return PortfolioCalculationService(db)
