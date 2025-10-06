#!/usr/bin/env python3
"""
Test GLDM prices using the user's exact code with 2025 dates
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

# Define request parameters
request_params = StockBarsRequest(
    symbol_or_symbols=["GLDM"],   # You can pass a list like ["AAPL", "MSFT", "TSLA"]
    timeframe=TimeFrame.Day,
    start=datetime.datetime(2025, 9, 23),
    end=datetime.datetime(2025, 9, 30)
)

# Fetch bars (OHLCV data)
bars = client.get_stock_bars(request_params)

# Convert to DataFrame for analysis
df = bars.df
print("GLDM Data for September 2025:")
print(df.tail())

# Calculate the return
if not df.empty:
    df.reset_index(inplace=True)
    
    # Find Sep 23, 2025 price
    sep_23_data = df[df['timestamp'].dt.date == datetime.datetime(2025, 9, 23).date()]
    if not sep_23_data.empty:
        sep_23_price = sep_23_data['close'].iloc[0]
        print(f"\nGLDM on Sep 23, 2025: ${sep_23_price:.2f}")
    
    # Find Sep 30, 2025 price
    sep_30_data = df[df['timestamp'].dt.date == datetime.datetime(2025, 9, 30).date()]
    if not sep_30_data.empty:
        sep_30_price = sep_30_data['close'].iloc[0]
        print(f"GLDM on Sep 30, 2025: ${sep_30_price:.2f}")
        
        if not sep_23_data.empty:
            return_pct = ((sep_30_price - sep_23_price) / sep_23_price) * 100
            print(f"7-day return: {return_pct:.2f}%")
            
            # Check if this matches your expected data
            if abs(sep_23_price - 74.54) < 0.1 and abs(sep_30_price - 76.45) < 0.1:
                print("✅ This matches your expected data!")
            else:
                print("❌ This doesn't match your expected data ($74.54 → $76.45)")
    else:
        print("No data for Sep 30, 2025")
else:
    print("No data returned from Alpaca API")
