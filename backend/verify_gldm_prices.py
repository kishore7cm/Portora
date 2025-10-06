#!/usr/bin/env python3
"""
Verify GLDM prices from Alpaca API
"""

import os
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")

# Initialize client
client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)

def fetch_gldm_data():
    """Fetch GLDM data to verify prices"""
    try:
        # Get data for September 2024
        request = StockBarsRequest(
            symbol_or_symbols="GLDM",
            start=datetime(2024, 9, 20),
            end=datetime(2024, 10, 5),
            timeframe=TimeFrame.Day
        )
        
        bars = client.get_stock_bars(request)
        df = bars.df
        
        if not df.empty:
            df.reset_index(inplace=True)
            print("GLDM Historical Data:")
            print(df[['timestamp', 'close']].to_string())
            
            # Find Sep 23, 2024 price
            sep_23_data = df[df['timestamp'].dt.date == datetime(2024, 9, 23).date()]
            if not sep_23_data.empty:
                sep_23_price = sep_23_data['close'].iloc[0]
                print(f"\nGLDM on Sep 23, 2024: ${sep_23_price:.2f}")
            
            # Find Sep 30, 2024 price
            sep_30_data = df[df['timestamp'].dt.date == datetime(2024, 9, 30).date()]
            if not sep_30_data.empty:
                sep_30_price = sep_30_data['close'].iloc[0]
                print(f"GLDM on Sep 30, 2024: ${sep_30_price:.2f}")
                
                if not sep_23_data.empty:
                    return_pct = ((sep_30_price - sep_23_price) / sep_23_price) * 100
                    print(f"7-day return: {return_pct:.2f}%")
            else:
                print("No data for Sep 30, 2024")
        else:
            print("No data returned from Alpaca API")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Verifying GLDM prices from Alpaca API...")
    fetch_gldm_data()
