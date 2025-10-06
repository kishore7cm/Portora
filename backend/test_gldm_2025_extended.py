#!/usr/bin/env python3
"""
Test GLDM prices with extended date range to find the latest available data
"""

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import pandas as pd
import datetime

# Replace with your actual Alpaca API keys
APCA_API_BASE_URL= 'https://api.alpaca.markets'
API_KEY = 'AKLE4VA1CEHBBHXNXCHZ'
API_SECRET = 'SQiQpXxbecEhS2p5z9l2olfhA135AuMktWUu12pm'

# Initialize the client
client = StockHistoricalDataClient(API_KEY, API_SECRET)

# Define request parameters - extended range to find latest data
request_params = StockBarsRequest(
    symbol_or_symbols=["GLDM"],
    timeframe=TimeFrame.Day,
    start=datetime.datetime(2025, 9, 23),
    end=datetime.datetime(2025, 10, 5)  # Extended to find latest data
)

# Fetch bars (OHLCV data)
bars = client.get_stock_bars(request_params)

# Convert to DataFrame for analysis
df = bars.df
print("GLDM Data for September-October 2025:")
print(df)

# Calculate the return
if not df.empty:
    df.reset_index(inplace=True)
    
    # Find Sep 23, 2025 price
    sep_23_data = df[df['timestamp'].dt.date == datetime.datetime(2025, 9, 23).date()]
    if not sep_23_data.empty:
        sep_23_price = sep_23_data['close'].iloc[0]
        print(f"\nGLDM on Sep 23, 2025: ${sep_23_price:.2f}")
    
    # Find the latest available price
    latest_data = df.iloc[-1]
    latest_price = latest_data['close']
    latest_date = latest_data['timestamp'].date()
    print(f"GLDM on {latest_date}: ${latest_price:.2f}")
    
    if not sep_23_data.empty:
        return_pct = ((latest_price - sep_23_price) / sep_23_price) * 100
        days_elapsed = (latest_date - datetime.datetime(2025, 9, 23).date()).days
        print(f"Return from Sep 23 to {latest_date}: {return_pct:.2f}% ({days_elapsed} days)")
        
        # Check if this matches your expected data
        if abs(sep_23_price - 74.54) < 0.1:
            print("✅ Sep 23 price matches your data!")
        else:
            print("❌ Sep 23 price doesn't match your data")
            
        # Check if latest price is close to your $76.45
        if abs(latest_price - 76.45) < 0.5:
            print("✅ Latest price is close to your expected $76.45!")
        else:
            print(f"❌ Latest price ${latest_price:.2f} doesn't match your expected $76.45")
    else:
        print("No data for Sep 23, 2025")
else:
    print("No data returned from Alpaca API")
