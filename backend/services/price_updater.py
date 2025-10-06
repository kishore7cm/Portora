"""
Daily Price Updater Service
Fetches and updates daily prices from Alpaca (stocks/bonds) and Twelve Data (crypto)
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

class PriceUpdater:
    """Service for updating daily prices from multiple APIs"""
    
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
    
    def fetch_alpaca_prices(self, ticker: str, start_date: date, end_date: date) -> List[Dict]:
        """Fetch daily prices from Alpaca API for stocks and bonds"""
        
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
    
    def insert_prices_bulk(self, prices: List[Dict]) -> int:
        """Insert prices in bulk for efficiency"""
        
        if not prices:
            return 0
        
        inserted_count = 0
        
        try:
            for price_data in prices:
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
            
            # Commit all changes
            self.db.commit()
            logger.info(f"✅ Inserted {inserted_count} new price records")
            
            return inserted_count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Failed to insert prices: {e}")
            return 0
    
    def update_ticker_prices(self, ticker: str, ticker_type: str) -> int:
        """Update prices for a single ticker"""
        
        # Get latest date we have data for
        latest_date = self.get_latest_price_date(ticker)
        today = date.today()
        
        if latest_date is None:
            # No data exists, fetch 1 year of historical data
            start_date = today - timedelta(days=365)
            logger.info(f"No existing data for {ticker}, fetching 1 year of history")
        elif latest_date >= today:
            # We're up to date
            logger.info(f"✅ {ticker} is up to date (latest: {latest_date})")
            return 0
        else:
            # Fetch missing data from last date + 1 until today
            start_date = latest_date + timedelta(days=1)
            logger.info(f"Updating {ticker} from {start_date} to {today}")
        
        # Fetch prices based on ticker type
        if ticker_type in ['stock', 'bond', 'etf']:
            prices = self.fetch_alpaca_prices(ticker, start_date, today)
        elif ticker_type == 'crypto':
            prices = self.fetch_twelve_data_prices(ticker, start_date, today)
        else:
            logger.warning(f"Unknown ticker type '{ticker_type}' for {ticker}")
            return 0
        
        # Insert prices
        return self.insert_prices_bulk(prices)

def update_daily_prices(stock_tickers: List[str], bond_tickers: List[str], crypto_tickers: List[str]) -> Dict[str, int]:
    """
    Main function to update daily prices for all tickers
    
    Args:
        stock_tickers: List of stock ticker symbols
        bond_tickers: List of bond ticker symbols  
        crypto_tickers: List of crypto ticker symbols
        
    Returns:
        Dictionary with update statistics
    """
    
    logger.info("🔄 Starting daily price update process")
    
    db = SessionLocal()
    updater = PriceUpdater(db)
    
    results = {
        'stocks_updated': 0,
        'bonds_updated': 0,
        'crypto_updated': 0,
        'total_new_records': 0,
        'errors': []
    }
    
    try:
        # Update stock prices
        logger.info(f"📈 Updating {len(stock_tickers)} stock tickers")
        for ticker in stock_tickers:
            try:
                count = updater.update_ticker_prices(ticker, 'stock')
                results['stocks_updated'] += 1
                results['total_new_records'] += count
                
                # Rate limiting for Alpaca
                time.sleep(60 / updater.alpaca_rate_limit)
                
            except Exception as e:
                error_msg = f"Failed to update stock {ticker}: {e}"
                logger.error(f"❌ {error_msg}")
                results['errors'].append(error_msg)
        
        # Update bond prices
        logger.info(f"🏦 Updating {len(bond_tickers)} bond tickers")
        for ticker in bond_tickers:
            try:
                count = updater.update_ticker_prices(ticker, 'bond')
                results['bonds_updated'] += 1
                results['total_new_records'] += count
                
                # Rate limiting for Alpaca
                time.sleep(60 / updater.alpaca_rate_limit)
                
            except Exception as e:
                error_msg = f"Failed to update bond {ticker}: {e}"
                logger.error(f"❌ {error_msg}")
                results['errors'].append(error_msg)
        
        # Update crypto prices
        logger.info(f"₿ Updating {len(crypto_tickers)} crypto tickers")
        for ticker in crypto_tickers:
            try:
                count = updater.update_ticker_prices(ticker, 'crypto')
                results['crypto_updated'] += 1
                results['total_new_records'] += count
                
                # Rate limiting for Twelve Data (more restrictive)
                time.sleep(60 / updater.twelve_data_rate_limit)
                
            except Exception as e:
                error_msg = f"Failed to update crypto {ticker}: {e}"
                logger.error(f"❌ {error_msg}")
                results['errors'].append(error_msg)
        
        logger.info("✅ Daily price update completed")
        logger.info(f"📊 Summary: {results['total_new_records']} new records, {len(results['errors'])} errors")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Critical error in price update process: {e}")
        results['errors'].append(f"Critical error: {e}")
        return results
        
    finally:
        db.close()

def get_portfolio_tickers() -> Tuple[List[str], List[str], List[str]]:
    """Get all unique tickers from portfolio, categorized by type"""
    
    db = SessionLocal()
    
    try:
        # Get all unique tickers from portfolio
        tickers = db.query(Portfolio.ticker).distinct().all()
        ticker_list = [t[0] for t in tickers]
        
        # Simple categorization (you can enhance this with AssetCategory table)
        stock_tickers = []
        bond_tickers = []
        crypto_tickers = []
        
        for ticker in ticker_list:
            if ticker.startswith('CASH'):
                continue  # Skip cash entries
            elif ticker in ['BTC-USD', 'ETH-USD', 'BTC', 'ETH'] or 'USD' in ticker:
                crypto_tickers.append(ticker)
            elif ticker in ['BND', 'AGG', 'TLT', 'IEF', 'SHY']:  # Common bond ETFs
                bond_tickers.append(ticker)
            else:
                stock_tickers.append(ticker)
        
        logger.info(f"📊 Found {len(stock_tickers)} stocks, {len(bond_tickers)} bonds, {len(crypto_tickers)} crypto")
        
        return stock_tickers, bond_tickers, crypto_tickers
        
    finally:
        db.close()

# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Update Daily Prices")
    parser.add_argument("--stocks", nargs="*", help="Stock tickers to update")
    parser.add_argument("--bonds", nargs="*", help="Bond tickers to update")
    parser.add_argument("--crypto", nargs="*", help="Crypto tickers to update")
    parser.add_argument("--auto", action="store_true", help="Auto-detect tickers from portfolio")
    
    args = parser.parse_args()
    
    if args.auto:
        # Auto-detect tickers from portfolio
        stock_tickers, bond_tickers, crypto_tickers = get_portfolio_tickers()
    else:
        # Use provided tickers
        stock_tickers = args.stocks or []
        bond_tickers = args.bonds or []
        crypto_tickers = args.crypto or []
    
    if not (stock_tickers or bond_tickers or crypto_tickers):
        print("❌ No tickers specified. Use --auto or provide --stocks/--bonds/--crypto")
        exit(1)
    
    # Run the update
    results = update_daily_prices(stock_tickers, bond_tickers, crypto_tickers)
    
    print("\n🎉 Price Update Results:")
    print(f"📈 Stocks updated: {results['stocks_updated']}")
    print(f"🏦 Bonds updated: {results['bonds_updated']}")
    print(f"₿ Crypto updated: {results['crypto_updated']}")
    print(f"📊 Total new records: {results['total_new_records']}")
    
    if results['errors']:
        print(f"\n❌ Errors ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"  - {error}")
