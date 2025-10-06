"""
Enhanced Daily Price Updater Service
Handles different asset types: stocks, bond ETFs, crypto, bonds-as-cash, and cash
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import os
import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple
import requests
import time
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

# Database imports
from core.database import SessionLocal
from domain.models_v2 import DailyPrice, Portfolio, User
from core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedPriceUpdater:
    """Enhanced service for updating daily prices with asset type handling"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # API credentials from environment
        self.alpaca_api_key = os.getenv('ALPACA_API_KEY')
        self.alpaca_secret_key = os.getenv('ALPACA_SECRET_KEY')
        self.twelve_data_api_key = os.getenv('TWELVE_DATA_API_KEY')
        
        # API endpoints
        self.alpaca_base_url = "https://paper-api.alpaca.markets"  # or "https://api.alpaca.markets" for live
        self.twelve_data_base_url = "https://api.twelvedata.com"
        
        # Rate limiting
        self.alpaca_rate_limit = 200  # requests per minute
        self.twelve_data_rate_limit = 8  # requests per minute for free tier
        
    def get_latest_price_date(self, ticker: str) -> Optional[date]:
        """Get the latest date we have price data for a ticker"""
        
        latest_record = (
            self.db.query(func.max(DailyPrice.price_date))
            .filter(DailyPrice.ticker == ticker)
            .scalar()
        )
        
        return latest_record
    
    def get_missing_dates(self, ticker: str, start_date: date, end_date: date) -> List[date]:
        """Get list of missing dates for a ticker between start and end dates"""
        
        # Get existing dates for this ticker
        existing_dates = (
            self.db.query(DailyPrice.price_date)
            .filter(
                and_(
                    DailyPrice.ticker == ticker,
                    DailyPrice.price_date >= start_date,
                    DailyPrice.price_date <= end_date
                )
            )
            .all()
        )
        
        existing_date_set = {d[0] for d in existing_dates}
        
        # Generate all business days in range (excluding weekends)
        missing_dates = []
        current_date = start_date
        while current_date <= end_date:
            # Skip weekends (0=Monday, 6=Sunday)
            if current_date.weekday() < 5 and current_date not in existing_date_set:
                missing_dates.append(current_date)
            current_date += timedelta(days=1)
        
        return missing_dates
    
    def fetch_alpaca_prices(self, ticker: str, start_date: date, end_date: date) -> List[Dict]:
        """Fetch daily prices from Alpaca API for stocks and bond ETFs"""
        
        if not self.alpaca_api_key or not self.alpaca_secret_key:
            logger.error("Alpaca API credentials not found")
            return []
        
        headers = {
            'APCA-API-KEY-ID': self.alpaca_api_key,
            'APCA-API-SECRET-KEY': self.alpaca_secret_key
        }
        
        # Format dates for Alpaca API
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        url = f"{self.alpaca_base_url}/v2/stocks/{ticker}/bars"
        params = {
            'start': start_str,
            'end': end_str,
            'timeframe': '1Day',
            'adjustment': 'raw',
            'feed': 'iex',  # Use IEX feed for better reliability
            'sort': 'asc'
        }
        
        try:
            logger.info(f"Fetching Alpaca data for {ticker} from {start_str} to {end_str}")
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'bars' not in data or not data['bars']:
                logger.warning(f"No Alpaca data found for {ticker}")
                return []
            
            prices = []
            for bar in data['bars']:
                price_date = datetime.fromisoformat(bar['t'].replace('Z', '+00:00')).date()
                
                prices.append({
                    'ticker': ticker,
                    'price_date': price_date,
                    'close_price': float(bar['c']),
                    'open_price': float(bar['o']),
                    'high_price': float(bar['h']),
                    'low_price': float(bar['l']),
                    'volume': int(bar['v']) if bar['v'] else None
                })
            
            logger.info(f"✅ Fetched {len(prices)} Alpaca price records for {ticker}")
            return prices
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Alpaca API error for {ticker}: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error fetching Alpaca data for {ticker}: {e}")
            return []
    
    def fetch_twelve_data_prices(self, ticker: str, start_date: date, end_date: date) -> List[Dict]:
        """Fetch daily prices from Twelve Data API for crypto"""
        
        if not self.twelve_data_api_key:
            logger.error("Twelve Data API key not found")
            return []
        
        # Format dates for Twelve Data API
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        url = f"{self.twelve_data_base_url}/time_series"
        params = {
            'symbol': ticker,
            'interval': '1day',
            'start_date': start_str,
            'end_date': end_str,
            'apikey': self.twelve_data_api_key,
            'format': 'JSON',
            'order': 'ASC'
        }
        
        try:
            logger.info(f"Fetching Twelve Data for {ticker} from {start_str} to {end_str}")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'values' not in data or not data['values']:
                logger.warning(f"No Twelve Data found for {ticker}")
                return []
            
            prices = []
            for item in data['values']:
                price_date = datetime.strptime(item['datetime'], '%Y-%m-%d').date()
                
                prices.append({
                    'ticker': ticker,
                    'price_date': price_date,
                    'close_price': float(item['close']),
                    'open_price': float(item['open']),
                    'high_price': float(item['high']),
                    'low_price': float(item['low']),
                    'volume': int(float(item['volume'])) if item.get('volume') else None
                })
            
            logger.info(f"✅ Fetched {len(prices)} Twelve Data price records for {ticker}")
            return prices
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Twelve Data API error for {ticker}: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error fetching Twelve Data for {ticker}: {e}")
            return []
    
    def bulk_insert_prices(self, all_prices: List[Dict]) -> int:
        """Bulk insert all prices for efficiency"""
        
        if not all_prices:
            return 0
        
        inserted_count = 0
        
        try:
            for price_data in all_prices:
                # Check if price already exists
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
                
                if not existing:
                    # Insert new price
                    daily_price = DailyPrice(
                        ticker=price_data['ticker'],
                        price_date=price_data['price_date'],
                        close_price=price_data['close_price'],
                        open_price=price_data.get('open_price'),
                        high_price=price_data.get('high_price'),
                        low_price=price_data.get('low_price'),
                        volume=price_data.get('volume')
                    )
                    self.db.add(daily_price)
                    inserted_count += 1
                else:
                    # Update existing price if needed
                    existing.close_price = price_data['close_price']
                    existing.open_price = price_data.get('open_price')
                    existing.high_price = price_data.get('high_price')
                    existing.low_price = price_data.get('low_price')
                    existing.volume = price_data.get('volume')
            
            logger.info(f"✅ Prepared {inserted_count} new price records for bulk insert")
            return inserted_count
            
        except Exception as e:
            logger.error(f"❌ Failed to prepare prices for bulk insert: {e}")
            return 0

def update_daily_prices(stock_tickers: List[str], bond_etf_tickers: List[str], crypto_tickers: List[str]) -> Dict[str, any]:
    """
    Enhanced function to update daily prices for different asset types
    
    Args:
        stock_tickers: List of stock ticker symbols
        bond_etf_tickers: List of bond ETF ticker symbols  
        crypto_tickers: List of crypto ticker symbols
        
    Returns:
        Dictionary with update statistics
    
    Note:
        - Bonds (non-ETF) are treated as cash positions and skipped
        - Cash positions are skipped (handled via cash_transactions)
        - Only stocks, bond ETFs, and crypto get daily price updates
    """
    
    logger.info("🔄 Starting enhanced daily price update process")
    
    db = SessionLocal()
    updater = EnhancedPriceUpdater(db)
    
    results = {
        'stocks_updated': 0,
        'bond_etfs_updated': 0,
        'crypto_updated': 0,
        'total_new_records': 0,
        'skipped_bonds': 0,
        'skipped_cash': 0,
        'errors': []
    }
    
    all_prices_to_insert = []  # Collect all prices for bulk insert
    today = date.today()
    
    try:
        # Process stock tickers
        logger.info(f"📈 Processing {len(stock_tickers)} stock tickers")
        for ticker in stock_tickers:
            try:
                # Skip cash positions
                if ticker.startswith('CASH') or ticker.startswith('Cash'):
                    results['skipped_cash'] += 1
                    logger.info(f"⏭️  Skipped cash position: {ticker}")
                    continue
                
                # Skip bond cash positions
                if ticker.startswith('BOND_CASH'):
                    results['skipped_bonds'] += 1
                    logger.info(f"⏭️  Skipped bond cash position: {ticker}")
                    continue
                
                # Get latest date and determine missing dates
                latest_date = updater.get_latest_price_date(ticker)
                
                if latest_date is None:
                    # No data exists, fetch last 30 days
                    start_date = today - timedelta(days=30)
                    logger.info(f"No existing data for {ticker}, fetching last 30 days")
                elif latest_date >= today:
                    # We're up to date
                    logger.info(f"✅ {ticker} is up to date (latest: {latest_date})")
                    results['stocks_updated'] += 1
                    continue
                else:
                    # Fetch missing data from last date + 1 until today
                    start_date = latest_date + timedelta(days=1)
                    logger.info(f"Updating {ticker} from {start_date} to {today}")
                
                # Fetch prices from Alpaca
                prices = updater.fetch_alpaca_prices(ticker, start_date, today)
                all_prices_to_insert.extend(prices)
                results['stocks_updated'] += 1
                
                # Rate limiting for Alpaca
                time.sleep(60 / updater.alpaca_rate_limit)
                
            except Exception as e:
                error_msg = f"Failed to update stock {ticker}: {e}"
                logger.error(f"❌ {error_msg}")
                results['errors'].append(error_msg)
        
        # Process bond ETF tickers
        logger.info(f"🏦 Processing {len(bond_etf_tickers)} bond ETF tickers")
        for ticker in bond_etf_tickers:
            try:
                # Get latest date and determine missing dates
                latest_date = updater.get_latest_price_date(ticker)
                
                if latest_date is None:
                    # No data exists, fetch last 30 days
                    start_date = today - timedelta(days=30)
                    logger.info(f"No existing data for bond ETF {ticker}, fetching last 30 days")
                elif latest_date >= today:
                    # We're up to date
                    logger.info(f"✅ Bond ETF {ticker} is up to date (latest: {latest_date})")
                    results['bond_etfs_updated'] += 1
                    continue
                else:
                    # Fetch missing data from last date + 1 until today
                    start_date = latest_date + timedelta(days=1)
                    logger.info(f"Updating bond ETF {ticker} from {start_date} to {today}")
                
                # Fetch prices from Alpaca (bond ETFs trade like stocks)
                prices = updater.fetch_alpaca_prices(ticker, start_date, today)
                all_prices_to_insert.extend(prices)
                results['bond_etfs_updated'] += 1
                
                # Rate limiting for Alpaca
                time.sleep(60 / updater.alpaca_rate_limit)
                
            except Exception as e:
                error_msg = f"Failed to update bond ETF {ticker}: {e}"
                logger.error(f"❌ {error_msg}")
                results['errors'].append(error_msg)
        
        # Process crypto tickers
        logger.info(f"₿ Processing {len(crypto_tickers)} crypto tickers")
        for ticker in crypto_tickers:
            try:
                # Get latest date and determine missing dates
                latest_date = updater.get_latest_price_date(ticker)
                
                if latest_date is None:
                    # No data exists, fetch last 30 days
                    start_date = today - timedelta(days=30)
                    logger.info(f"No existing data for crypto {ticker}, fetching last 30 days")
                elif latest_date >= today:
                    # We're up to date
                    logger.info(f"✅ Crypto {ticker} is up to date (latest: {latest_date})")
                    results['crypto_updated'] += 1
                    continue
                else:
                    # Fetch missing data from last date + 1 until today
                    start_date = latest_date + timedelta(days=1)
                    logger.info(f"Updating crypto {ticker} from {start_date} to {today}")
                
                # Fetch prices from Twelve Data
                prices = updater.fetch_twelve_data_prices(ticker, start_date, today)
                all_prices_to_insert.extend(prices)
                results['crypto_updated'] += 1
                
                # Rate limiting for Twelve Data (more restrictive)
                time.sleep(60 / updater.twelve_data_rate_limit)
                
            except Exception as e:
                error_msg = f"Failed to update crypto {ticker}: {e}"
                logger.error(f"❌ {error_msg}")
                results['errors'].append(error_msg)
        
        # Bulk insert all collected prices
        logger.info(f"💾 Bulk inserting {len(all_prices_to_insert)} price records")
        inserted_count = updater.bulk_insert_prices(all_prices_to_insert)
        results['total_new_records'] = inserted_count
        
        # Commit all changes at once
        db.commit()
        logger.info("✅ All price updates committed successfully")
        
        logger.info("✅ Enhanced daily price update completed")
        logger.info(f"📊 Summary: {results}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Critical error in enhanced price update process: {e}")
        db.rollback()
        results['errors'].append(f"Critical error: {e}")
        return results
        
    finally:
        db.close()

def categorize_portfolio_tickers() -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
    """
    Categorize all portfolio tickers by asset type
    
    Returns:
        Tuple of (stock_tickers, bond_etf_tickers, crypto_tickers, bond_cash_tickers, cash_tickers)
    """
    
    db = SessionLocal()
    
    try:
        # Get all unique tickers from portfolio
        tickers = db.query(Portfolio.ticker).distinct().all()
        ticker_list = [t[0] for t in tickers]
        
        # Categorize tickers
        stock_tickers = []
        bond_etf_tickers = []
        crypto_tickers = []
        bond_cash_tickers = []
        cash_tickers = []
        
        # Common bond ETFs
        known_bond_etfs = {
            'BND', 'AGG', 'TLT', 'IEF', 'SHY', 'VGIT', 'VGLT', 'VTEB', 
            'MUB', 'HYG', 'JNK', 'LQD', 'VCIT', 'VCLT', 'BSV', 'BIV', 'BLV'
        }
        
        # Common crypto symbols
        crypto_symbols = {
            'BTC-USD', 'ETH-USD', 'BTC', 'ETH', 'ADA-USD', 'SOL-USD', 
            'DOT-USD', 'AVAX-USD', 'MATIC-USD', 'LINK-USD'
        }
        
        for ticker in ticker_list:
            if ticker.startswith('CASH') or ticker.startswith('Cash'):
                cash_tickers.append(ticker)
            elif ticker.startswith('BOND_CASH'):
                bond_cash_tickers.append(ticker)
            elif ticker in crypto_symbols or 'USD' in ticker:
                crypto_tickers.append(ticker)
            elif ticker in known_bond_etfs:
                bond_etf_tickers.append(ticker)
            else:
                # Default to stock
                stock_tickers.append(ticker)
        
        logger.info(f"📊 Portfolio categorization:")
        logger.info(f"  📈 Stocks: {len(stock_tickers)}")
        logger.info(f"  🏦 Bond ETFs: {len(bond_etf_tickers)}")
        logger.info(f"  ₿ Crypto: {len(crypto_tickers)}")
        logger.info(f"  💰 Bond Cash: {len(bond_cash_tickers)}")
        logger.info(f"  💵 Cash: {len(cash_tickers)}")
        
        return stock_tickers, bond_etf_tickers, crypto_tickers, bond_cash_tickers, cash_tickers
        
    finally:
        db.close()

# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Daily Price Updater")
    parser.add_argument("--stocks", nargs="*", help="Stock tickers to update")
    parser.add_argument("--bond-etfs", nargs="*", help="Bond ETF tickers to update")
    parser.add_argument("--crypto", nargs="*", help="Crypto tickers to update")
    parser.add_argument("--auto", action="store_true", help="Auto-categorize tickers from portfolio")
    
    args = parser.parse_args()
    
    if args.auto:
        # Auto-categorize tickers from portfolio
        stock_tickers, bond_etf_tickers, crypto_tickers, _, _ = categorize_portfolio_tickers()
    else:
        # Use provided tickers
        stock_tickers = args.stocks or []
        bond_etf_tickers = args.bond_etfs or []
        crypto_tickers = args.crypto or []
    
    if not (stock_tickers or bond_etf_tickers or crypto_tickers):
        print("❌ No tickers specified. Use --auto or provide --stocks/--bond-etfs/--crypto")
        exit(1)
    
    # Run the enhanced update
    results = update_daily_prices(stock_tickers, bond_etf_tickers, crypto_tickers)
    
    print("\n🎉 Enhanced Price Update Results:")
    print(f"📈 Stocks updated: {results['stocks_updated']}")
    print(f"🏦 Bond ETFs updated: {results['bond_etfs_updated']}")
    print(f"₿ Crypto updated: {results['crypto_updated']}")
    print(f"💰 Bond cash skipped: {results['skipped_bonds']}")
    print(f"💵 Cash skipped: {results['skipped_cash']}")
    print(f"📊 Total new records: {results['total_new_records']}")
    
    if results['errors']:
        print(f"\n❌ Errors ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"  - {error}")
