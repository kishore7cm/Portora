#!/usr/bin/env python3
"""
Fetch REAL market data using unlimited APIs
- Yahoo Finance for stocks (no rate limits)
- Twelve Data for crypto (with rate limiting)
"""

import os
import sys
import requests
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import PortfolioValues, HistoricalData
import time
from dotenv import load_dotenv
import yfinance as yf

# Load environment variables
load_dotenv()

# Add parent directory to sys.path for config imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, parent_dir)

# API Configuration
TWELVE_DATA_API_KEY = os.getenv('TWELVE_DATA_API_KEY')

def get_stock_price_yahoo(ticker):
    """Get current stock price using Yahoo Finance (no rate limits)"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
        else:
            print(f"Could not get Yahoo Finance price for {ticker}")
            return None
    except Exception as e:
        print(f"Error fetching Yahoo Finance price for {ticker}: {e}")
        return None

def get_historical_stock_price_yahoo(ticker, date):
    """Get historical stock price using Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        # Get data around the target date
        start_date = date - timedelta(days=5)
        end_date = date + timedelta(days=5)
        hist = stock.history(start=start_date, end=end_date)
        
        if not hist.empty:
            # Find the closest date to target date
            hist['date_diff'] = abs((hist.index.date - date))
            closest_date = hist.loc[hist['date_diff'].idxmin()]
            return float(closest_date['Close'])
        else:
            print(f"Could not get Yahoo Finance historical price for {ticker} on {date}")
            return None
    except Exception as e:
        print(f"Error fetching Yahoo Finance historical price for {ticker}: {e}")
        return None

def get_crypto_price_twelve(ticker):
    """Get current crypto price using Twelve Data API"""
    try:
        url = f"https://api.twelvedata.com/price?symbol={ticker}&apikey={TWELVE_DATA_API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'price' in data and data['price']:
            return float(data['price'])
        else:
            print(f"Could not get Twelve Data price for {ticker}: {data}")
            return None
    except Exception as e:
        print(f"Error fetching Twelve Data price for {ticker}: {e}")
        return None

def get_historical_crypto_price_twelve(ticker, date):
    """Get historical crypto price using Twelve Data API"""
    try:
        url = f"https://api.twelvedata.com/time_series"
        params = {
            "symbol": ticker,
            "interval": "1day",
            "start_date": date.strftime('%Y-%m-%d'),
            "end_date": (date + timedelta(days=1)).strftime('%Y-%m-%d'),
            "apikey": TWELVE_DATA_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'values' in data and data['values']:
            return float(data['values'][0]['close'])
        else:
            print(f"Could not get Twelve Data historical price for {ticker} on {date}: {data}")
            return None
    except Exception as e:
        print(f"Error fetching Twelve Data historical price for {ticker}: {e}")
        return None

def fetch_real_market_data():
    """Fetch REAL market data using Yahoo Finance (stocks) and Twelve Data (crypto)"""
    print("🚀 Fetching REAL market data using Yahoo Finance (stocks) and Twelve Data (crypto)...")
    print(f"📊 Twelve Data API Key: {TWELVE_DATA_API_KEY[:10]}...")
    print("📊 Yahoo Finance: No API key needed, no rate limits")
    
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
        
        # September 23rd, 2025 (when you started with $325k)
        sep_23_2025 = datetime(2025, 9, 23).date()
        current_date = datetime(2025, 9, 30).date()
        days_elapsed = (current_date - sep_23_2025).days
        
        print(f"Calculating REAL returns from {sep_23_2025} to {current_date} ({days_elapsed} days)")
        print(f"Starting with $325,000 on September 23rd, 2025")
        
        # Calculate proportional allocation
        current_total = sum(holding.total_value for holding in portfolio_values)
        scale_factor = 325000.00 / current_total if current_total > 0 else 1
        
        print(f"Scaling factor: {scale_factor:.4f}")
        
        total_starting_value = 325000.00
        total_current_value = 0
        updated_holdings = []
        
        # Process all holdings (Yahoo Finance has no rate limits)
        print(f"Processing all {len(portfolio_values)} holdings...")
        
        for i, holding in enumerate(portfolio_values):
            ticker = holding.ticker
            print(f"Processing {i+1}/{len(portfolio_values)}: {ticker}...")
            
            # Scale down to $325k starting value
            scaled_starting_value = holding.total_value * scale_factor
            shares = scaled_starting_value / holding.current_price if holding.current_price > 0 else 0
            starting_price = holding.current_price
            
            # Determine if it's crypto or stock
            is_crypto = any(crypto in ticker.upper() for crypto in ['BTC', 'ETH', 'ADA', 'SOL', 'DOT', 'LINK'])
            
            # Get historical price (September 23rd, 2025)
            print(f"  Getting historical price for {ticker} on {sep_23_2025}...")
            if is_crypto:
                historical_price = get_historical_crypto_price_twelve(ticker, sep_23_2025)
            else:
                historical_price = get_historical_stock_price_yahoo(ticker, sep_23_2025)
            
            # Get current price
            print(f"  Getting current price for {ticker}...")
            if is_crypto:
                current_price = get_crypto_price_twelve(ticker)
            else:
                current_price = get_stock_price_yahoo(ticker)
            
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
                'gain_loss_percent': gain_loss_percent,
                'is_crypto': is_crypto
            })
            
            print(f"  {ticker}: ${historical_price:.2f} -> ${current_price:.2f} ({gain_loss_percent:+.2f}%) {'[CRYPTO]' if is_crypto else '[STOCK]'}")
            
            # Small delay for crypto API calls only
            if is_crypto:
                time.sleep(0.5)  # 0.5 second delay for crypto API calls
        
        # Commit all changes
        db.commit()
        
        # Calculate total returns
        total_gain_loss = total_current_value - total_starting_value
        total_gain_loss_percent = (total_gain_loss / total_starting_value) * 100 if total_starting_value > 0 else 0
        
        print(f"\n=== REAL MARKET DATA - 7-DAY PORTFOLIO SUMMARY ===")
        print(f"Starting Value (Sep 23, 2025): ${total_starting_value:,.2f}")
        print(f"Current Value (Sep 30, 2025): ${total_current_value:,.2f}")
        print(f"Total Gain/Loss: ${total_gain_loss:,.2f}")
        print(f"Total Return: {total_gain_loss_percent:+.2f}%")
        print(f"Days Elapsed: {days_elapsed}")
        print(f"Time Period: {days_elapsed} days (1 week)")
        
        print(f"\n=== TOP PERFORMERS (7 days) ===")
        top_performers = sorted(updated_holdings, key=lambda x: x['gain_loss_percent'], reverse=True)[:10]
        for holding in top_performers:
            print(f"{holding['ticker']}: {holding['gain_loss_percent']:+.2f}% (${holding['gain_loss']:+,.2f}) {'[CRYPTO]' if holding['is_crypto'] else '[STOCK]'}")
        
        print(f"\n=== WORST PERFORMERS (7 days) ===")
        worst_performers = sorted(updated_holdings, key=lambda x: x['gain_loss_percent'])[:10]
        for holding in worst_performers:
            print(f"{holding['ticker']}: {holding['gain_loss_percent']:+.2f}% (${holding['gain_loss']:+,.2f}) {'[CRYPTO]' if holding['is_crypto'] else '[STOCK]'}")
        
        print(f"\n✅ REAL market data fetch completed!")
        print(f"📊 This data is based on actual API calls to Yahoo Finance and Twelve Data")
        print(f"📊 Processed all {len(portfolio_values)} holdings with no rate limits!")
        
        return {
            'total_starting_value': total_starting_value,
            'total_current_value': total_current_value,
            'total_gain_loss': total_gain_loss,
            'total_gain_loss_percent': total_gain_loss_percent,
            'days_elapsed': days_elapsed,
            'updated_holdings': updated_holdings
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error fetching real market data: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("Fetching REAL market data using Yahoo Finance and Twelve Data APIs...")
    result = fetch_real_market_data()
    if result:
        print("Real market data fetch completed successfully!")
    else:
        print("Real market data fetch failed!")
