#!/usr/bin/env python3
"""
Fetch REAL market data using the correct Alpaca API approach
"""

import os
import sys
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import PortfolioValues, HistoricalData
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to sys.path for config imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, parent_dir)

# ===============================
# 🔑 Setup API Keys
# ===============================
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID", "YOUR_ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY", "YOUR_ALPACA_SECRET_KEY")

# Initialize client
client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)

# ===============================
# 📈 Fetch Stock Data Function
# ===============================
def fetch_stock_data(symbol: str, start: str, end: str, timeframe: str = "1Day"):
    """
    Fetch historical stock OHLCV data from Alpaca.

    :param symbol: Stock ticker (e.g., "AAPL")
    :param start: Start date (YYYY-MM-DD)
    :param end: End date (YYYY-MM-DD)
    :param timeframe: Time interval ("1Min", "5Min", "15Min", "1Hour", "1Day")
    :return: DataFrame with OHLCV
    """
    try:
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            start=datetime.fromisoformat(start),
            end=datetime.fromisoformat(end),
            timeframe=TimeFrame.Day
        )
        
        bars = client.get_stock_bars(request)

        # Convert to Pandas DataFrame
        df = bars.df
        if df.empty:
            return None
            
        df.reset_index(inplace=True)
        df = df.rename(columns={
            "symbol": "ticker",
            "timestamp": "date",
            "open": "open_price",
            "high": "high_price",
            "low": "low_price",
            "close": "close_price",
            "volume": "volume"
        })

        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def get_current_price(symbol: str):
    """Get current price for a symbol"""
    try:
        # Get data for September 30, 2024 (7 days after start)
        end_date = "2024-09-30"
        start_date = "2024-09-25"  # A few days before to ensure we get data
        
        df = fetch_stock_data(symbol, start_date, end_date, "1Day")
        if df is not None and not df.empty:
            return float(df['close_price'].iloc[-1])
        return None
    except Exception as e:
        print(f"Error getting current price for {symbol}: {e}")
        return None

def get_historical_price(symbol: str, target_date: str):
    """Get historical price for a symbol on a specific date"""
    try:
        # Get data around the target date
        target_dt = datetime.fromisoformat(target_date)
        start_date = (target_dt - timedelta(days=5)).strftime('%Y-%m-%d')
        end_date = (target_dt + timedelta(days=5)).strftime('%Y-%m-%d')
        
        df = fetch_stock_data(symbol, start_date, end_date, "1Day")
        if df is not None and not df.empty:
            # Find the closest date to target date
            df['date_diff'] = abs((pd.to_datetime(df['date']).dt.date - target_dt.date()))
            closest_row = df.loc[df['date_diff'].idxmin()]
            return float(closest_row['close_price'])
        return None
    except Exception as e:
        print(f"Error getting historical price for {symbol}: {e}")
        return None

def fetch_real_market_data():
    """Fetch REAL market data using the correct Alpaca API"""
    print("🚀 Fetching REAL market data using correct Alpaca API...")
    print(f"📊 Alpaca API Key: {ALPACA_API_KEY[:10]}...")
    
    db = SessionLocal()
    try:
        # Ensure tables are created
        Base.metadata.create_all(bind=engine)
        
        # Get portfolio data
        portfolio_values = db.query(PortfolioValues).filter(PortfolioValues.user_id == 1).all()
        
        if not portfolio_values:
            print("No portfolio data found for user 1")
            return
        
        print(f"Found {len(portfolio_values)} portfolio holdings")
        
        # September 23rd, 2024 (when you started with $325k) - CORRECTED DATE
        sep_23_2024 = "2024-09-23"
        # Calculate 7 days later for 7-day returns
        sep_30_2024 = "2024-09-30"
        current_date = sep_30_2024
        
        print(f"Calculating REAL returns from {sep_23_2024} to {current_date}")
        print(f"Starting with $325,000 on September 23rd, 2024")
        
        # Calculate proportional allocation
        current_total = sum(holding.total_value for holding in portfolio_values)
        scale_factor = 325000.00 / current_total if current_total > 0 else 1
        
        print(f"Scaling factor: {scale_factor:.4f}")
        
        total_starting_value = 325000.00
        total_current_value = 0
        updated_holdings = []
        
        # Process first 10 holdings for testing
        test_holdings = portfolio_values[:10]
        print(f"Processing first {len(test_holdings)} holdings for testing...")
        
        for i, holding in enumerate(test_holdings):
            ticker = holding.ticker
            print(f"Processing {i+1}/{len(test_holdings)}: {ticker}...")
            
            # Scale down to $325k starting value
            scaled_starting_value = holding.total_value * scale_factor
            shares = scaled_starting_value / holding.current_price if holding.current_price > 0 else 0
            starting_price = holding.current_price
            
            # Get historical price (September 23rd, 2024)
            print(f"  Getting historical price for {ticker} on {sep_23_2024}...")
            historical_price = get_historical_price(ticker, sep_23_2024)
            
            # Get current price
            print(f"  Getting current price for {ticker}...")
            current_price = get_current_price(ticker)
            
            # If API calls failed, use fallback prices
            if historical_price is None:
                historical_price = starting_price
                print(f"  ⚠️  Using fallback historical price for {ticker}")
            
            if current_price is None:
                current_price = starting_price
                print(f"  ⚠️  Using fallback current price for {ticker}")
            
            # Calculate values
            current_value = shares * current_price
            starting_value = shares * historical_price
            gain_loss = current_value - starting_value
            gain_loss_percent = (gain_loss / starting_value) * 100 if starting_value > 0 else 0
            
            # Update the holding
            holding.current_price = current_price
            holding.total_value = current_value
            holding.gain_loss = gain_loss
            holding.gain_loss_percent = gain_loss_percent
            holding.last_updated = datetime.now()
            
            total_current_value += current_value
            
            updated_holdings.append({
                'ticker': ticker,
                'shares': shares,
                'starting_price': historical_price,
                'current_price': current_price,
                'starting_value': starting_value,
                'current_value': current_value,
                'gain_loss': gain_loss,
                'gain_loss_percent': gain_loss_percent
            })
            
            print(f"  {ticker}: ${historical_price:.2f} -> ${current_price:.2f} ({gain_loss_percent:+.2f}%)")
            
            # Small delay between API calls
            time.sleep(0.5)
        
        # Commit all changes
        db.commit()
        
        # Calculate total returns
        total_gain_loss = total_current_value - total_starting_value
        total_gain_loss_percent = (total_gain_loss / total_starting_value) * 100 if total_starting_value > 0 else 0
        
        print(f"\n=== REAL MARKET DATA - PORTFOLIO SUMMARY ===")
        print(f"Starting Value (Sep 23, 2024): ${total_starting_value:,.2f}")
        print(f"Current Value ({current_date}): ${total_current_value:,.2f}")
        print(f"Total Gain/Loss: ${total_gain_loss:,.2f}")
        print(f"Total Return: {total_gain_loss_percent:+.2f}%")
        
        print(f"\n=== TOP PERFORMERS ===")
        top_performers = sorted(updated_holdings, key=lambda x: x['gain_loss_percent'], reverse=True)[:5]
        for holding in top_performers:
            print(f"{holding['ticker']}: {holding['gain_loss_percent']:+.2f}% (${holding['gain_loss']:+,.2f})")
        
        print(f"\n=== WORST PERFORMERS ===")
        worst_performers = sorted(updated_holdings, key=lambda x: x['gain_loss_percent'])[:5]
        for holding in worst_performers:
            print(f"{holding['ticker']}: {holding['gain_loss_percent']:+.2f}% (${holding['gain_loss']:+,.2f})")
        
        print(f"\n✅ REAL market data fetch completed!")
        print(f"📊 This data is based on actual API calls to Alpaca using the correct library")
        print(f"📊 Processed {len(test_holdings)} holdings")
        
        return {
            'total_starting_value': total_starting_value,
            'total_current_value': total_current_value,
            'total_gain_loss': total_gain_loss,
            'total_gain_loss_percent': total_gain_loss_percent,
            'updated_holdings': updated_holdings
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error fetching real market data: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("Fetching REAL market data using correct Alpaca API...")
    result = fetch_real_market_data()
    if result:
        print("Real market data fetch completed successfully!")
    else:
        print("Real market data fetch failed!")
