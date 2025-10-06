#!/usr/bin/env python3
"""
Update GLDM with correct current price from user's data
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import PortfolioValues, HistoricalData, User
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, parent_dir)
load_dotenv()

# Use your API keys
API_KEY = 'AKLE4VA1CEHBBHXNXCHZ'
API_SECRET = 'SQiQpXxbecEhS2p5z9l2olfhA135AuMktWUu12pm'

client = StockHistoricalDataClient(API_KEY, API_SECRET)

def update_gldm_with_correct_prices(db: Session, user_id: int):
    """Update GLDM with correct prices from user's data"""
    print("Updating GLDM with correct prices...")
    
    # Get GLDM holding
    gldm_holding = db.query(PortfolioValues).filter(
        PortfolioValues.user_id == user_id,
        PortfolioValues.ticker == 'GLDM'
    ).first()
    
    if not gldm_holding:
        print("GLDM holding not found")
        return
    
    print(f"Found GLDM holding: ${gldm_holding.total_value:.2f} at ${gldm_holding.current_price:.2f}")
    
    # Get historical data from Alpaca (Sep 23, 2025 onwards)
    try:
        request_params = StockBarsRequest(
            symbol_or_symbols=["GLDM"],
            timeframe=TimeFrame.Day,
            start=datetime(2025, 9, 23),
            end=datetime(2025, 9, 30)
        )
        
        bars = client.get_stock_bars(request_params)
        df = bars.df
        
        if not df.empty:
            df.reset_index(inplace=True)
            
            # Get Sep 23, 2025 price
            sep_23_data = df[df['timestamp'].dt.date == datetime(2025, 9, 23).date()]
            if not sep_23_data.empty:
                sep_23_price = sep_23_data['close'].iloc[0]
                print(f"GLDM on Sep 23, 2025: ${sep_23_price:.2f}")
                
                # Update the holding with correct current price
                # User says current price is $76.45
                current_price = 76.45
                
                # Calculate the return
                return_pct = ((current_price - sep_23_price) / sep_23_price) * 100
                print(f"GLDM current price: ${current_price:.2f}")
                print(f"GLDM return: {return_pct:.2f}%")
                
                # Calculate shares from total_value and current_price
                shares = gldm_holding.total_value / gldm_holding.current_price
                
                # Update the holding
                gldm_holding.current_price = current_price
                gldm_holding.total_value = shares * current_price
                
                db.commit()
                print("✅ GLDM updated with correct current price!")
                
                return {
                    "ticker": "GLDM",
                    "sep_23_price": sep_23_price,
                    "current_price": current_price,
                    "return_pct": return_pct
                }
            else:
                print("No data for Sep 23, 2025")
        else:
            print("No data returned from Alpaca API")
            
    except Exception as e:
        print(f"Error fetching Alpaca data: {e}")
        # Fallback: just update with the correct current price
        current_price = 76.45
        shares = gldm_holding.total_value / gldm_holding.current_price
        gldm_holding.current_price = current_price
        gldm_holding.total_value = shares * current_price
        db.commit()
        print("✅ GLDM updated with correct current price (fallback)!")

if __name__ == "__main__":
    db_session = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)
        update_gldm_with_correct_prices(db_session, user_id=1)
    finally:
        db_session.close()
