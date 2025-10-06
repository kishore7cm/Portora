#!/usr/bin/env python3
"""
Calculate mock returns from September 23rd, 2024 and store historical data
This uses realistic market movements based on actual stock performance patterns
"""

import os
import sys
import random
import math
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Portfolio, HistoricalData, PortfolioValues
import time

# Add parent directory to sys.path for config imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, parent_dir)

def get_realistic_price_change(ticker, days_elapsed):
    """Generate realistic price changes based on ticker characteristics"""
    
    # Set random seed based on ticker for consistency
    random.seed(hash(ticker) % 1000)
    
    # Different volatility and growth patterns for different asset types
    if 'BTC' in ticker or 'ETH' in ticker:
        # Crypto: High volatility, potential high growth
        daily_volatility = 0.03
        trend_factor = 0.001
    elif ticker in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA']:
        # Tech stocks: Medium-high volatility, good growth
        daily_volatility = 0.02
        trend_factor = 0.0008
    elif ticker in ['FXAIX', 'FSPGX', 'VOO', 'SPY']:
        # Index funds: Lower volatility, steady growth
        daily_volatility = 0.015
        trend_factor = 0.0005
    elif 'Bond' in ticker or 'Treasury' in ticker:
        # Bonds: Low volatility, steady growth
        daily_volatility = 0.005
        trend_factor = 0.0002
    else:
        # Default: Medium volatility
        daily_volatility = 0.018
        trend_factor = 0.0006
    
    # Calculate cumulative return over the period
    total_return = 0
    for day in range(days_elapsed):
        # Daily random movement
        daily_change = random.gauss(0, daily_volatility)
        # Add trend
        daily_change += trend_factor
        total_return += daily_change
    
    return total_return

def calculate_mock_returns():
    """Calculate realistic mock returns from September 23rd, 2024"""
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
        
        # September 23rd, 2024
        sep_23_2024 = datetime(2024, 9, 23).date()
        current_date = datetime.now().date()
        days_elapsed = (current_date - sep_23_2024).days
        
        print(f"Calculating returns from {sep_23_2024} to {current_date} ({days_elapsed} days)")
        
        total_starting_value = 0
        total_current_value = 0
        updated_holdings = []
        
        for holding in portfolio_values:
            ticker = holding.ticker
            print(f"Processing {ticker}...")
            
            # Current stored price (this was the price on Sep 23rd)
            starting_price = holding.current_price
            
            # Calculate realistic price change
            price_change_factor = get_realistic_price_change(ticker, days_elapsed)
            current_price = starting_price * (1 + price_change_factor)
            
            # Calculate shares
            shares = holding.total_value / starting_price if starting_price > 0 else 0
            
            # Calculate values
            starting_value = shares * starting_price
            current_value = shares * current_price
            gain_loss = current_value - starting_value
            gain_loss_percent = (gain_loss / starting_value) * 100 if starting_value > 0 else 0
            
            # Update the holding
            holding.current_price = current_price
            holding.total_value = current_value
            holding.gain_loss = gain_loss
            holding.gain_loss_percent = gain_loss_percent
            holding.last_updated = datetime.now()
            
            total_starting_value += starting_value
            total_current_value += current_value
            
            updated_holdings.append({
                'ticker': ticker,
                'shares': shares,
                'starting_price': starting_price,
                'current_price': current_price,
                'starting_value': starting_value,
                'current_value': current_value,
                'gain_loss': gain_loss,
                'gain_loss_percent': gain_loss_percent
            })
            
            print(f"  {ticker}: ${starting_price:.2f} -> ${current_price:.2f} ({gain_loss_percent:+.2f}%)")
            
            # Store historical data for September 23rd
            historical_entry = HistoricalData(
                ticker=ticker,
                date=sep_23_2024,
                open_price=starting_price,
                high_price=starting_price * 1.01,
                low_price=starting_price * 0.99,
                close_price=starting_price,
                volume=1000000
            )
            
            # Check if entry already exists
            existing = db.query(HistoricalData).filter(
                HistoricalData.ticker == ticker,
                HistoricalData.date == sep_23_2024
            ).first()
            
            if not existing:
                db.add(historical_entry)
            
            # Store current date entry
            current_entry = HistoricalData(
                ticker=ticker,
                date=current_date,
                open_price=current_price,
                high_price=current_price * 1.01,
                low_price=current_price * 0.99,
                close_price=current_price,
                volume=1000000
            )
            
            # Check if current entry already exists
            existing_current = db.query(HistoricalData).filter(
                HistoricalData.ticker == ticker,
                HistoricalData.date == current_date
            ).first()
            
            if not existing_current:
                db.add(current_entry)
            
            # Generate historical data points between Sep 23 and now
            for i in range(1, min(days_elapsed, 30)):  # Add up to 30 data points
                random_date = sep_23_2024 + timedelta(days=i)
                
                # Calculate price for this date
                days_since_start = i
                price_change_factor = get_realistic_price_change(ticker, days_since_start)
                price_for_date = starting_price * (1 + price_change_factor)
                
                historical_data_entry = HistoricalData(
                    ticker=ticker,
                    date=random_date,
                    open_price=price_for_date,
                    high_price=price_for_date * (1 + abs(random.gauss(0, 0.01))),
                    low_price=price_for_date * (1 - abs(random.gauss(0, 0.01))),
                    close_price=price_for_date,
                    volume=1000000
                )
                
                # Check if entry already exists
                existing_historical = db.query(HistoricalData).filter(
                    HistoricalData.ticker == ticker,
                    HistoricalData.date == random_date
                ).first()
                
                if not existing_historical:
                    db.add(historical_data_entry)
        
        # Commit all changes
        db.commit()
        
        # Calculate total returns
        total_gain_loss = total_current_value - total_starting_value
        total_gain_loss_percent = (total_gain_loss / total_starting_value) * 100 if total_starting_value > 0 else 0
        
        # Calculate annualized return
        years_elapsed = days_elapsed / 365.25
        annualized_return = (total_current_value / total_starting_value) ** (1 / years_elapsed) - 1 if years_elapsed > 0 else 0
        
        print(f"\n=== PORTFOLIO SUMMARY ===")
        print(f"Starting Value (Sep 23, 2024): ${total_starting_value:,.2f}")
        print(f"Current Value: ${total_current_value:,.2f}")
        print(f"Total Gain/Loss: ${total_gain_loss:,.2f}")
        print(f"Total Return: {total_gain_loss_percent:+.2f}%")
        print(f"Annualized Return: {annualized_return * 100:+.2f}%")
        print(f"Days Elapsed: {days_elapsed}")
        
        print(f"\n=== TOP PERFORMERS ===")
        top_performers = sorted(updated_holdings, key=lambda x: x['gain_loss_percent'], reverse=True)[:5]
        for holding in top_performers:
            print(f"{holding['ticker']}: {holding['gain_loss_percent']:+.2f}% (${holding['gain_loss']:+,.2f})")
        
        print(f"\n=== WORST PERFORMERS ===")
        worst_performers = sorted(updated_holdings, key=lambda x: x['gain_loss_percent'])[:5]
        for holding in worst_performers:
            print(f"{holding['ticker']}: {holding['gain_loss_percent']:+.2f}% (${holding['gain_loss']:+,.2f})")
        
        return {
            'total_starting_value': total_starting_value,
            'total_current_value': total_current_value,
            'total_gain_loss': total_gain_loss,
            'total_gain_loss_percent': total_gain_loss_percent,
            'annualized_return': annualized_return,
            'days_elapsed': days_elapsed,
            'updated_holdings': updated_holdings
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error calculating mock returns: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting mock returns calculation...")
    result = calculate_mock_returns()
    if result:
        print("Mock returns calculation completed successfully!")
    else:
        print("Mock returns calculation failed!")
