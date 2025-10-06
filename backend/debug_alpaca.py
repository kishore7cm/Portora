#!/usr/bin/env python3
"""
Debug Alpaca API to see what's actually happening
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
ALPACA_API_KEY = os.getenv('APCA_API_KEY_ID')
ALPACA_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
ALPACA_BASE_URL = os.getenv('APCA_API_BASE_URL', 'https://api.alpaca.markets')

headers = {
    "APCA-API-KEY-ID": ALPACA_API_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY
}

print(f"Debugging Alpaca API...")
print(f"API Key: {ALPACA_API_KEY}")
print(f"Base URL: {ALPACA_BASE_URL}")

# Test account info first
print(f"\n=== Testing Account Info ===")
try:
    account_url = f"{ALPACA_BASE_URL}/v2/account"
    response = requests.get(account_url, headers=headers, timeout=10)
    print(f"Account Status: {response.status_code}")
    print(f"Account Response: {response.text[:500]}...")
except Exception as e:
    print(f"Account Error: {e}")

# Test different market data endpoints
print(f"\n=== Testing Market Data Endpoints ===")

endpoints = [
    f"{ALPACA_BASE_URL}/v2/stocks/bars/latest?symbols=AAPL&timeframe=1Min",
    f"{ALPACA_BASE_URL}/v2/stocks/bars?symbols=AAPL&start=2024-09-23&end=2024-09-24&timeframe=1Day",
    f"{ALPACA_BASE_URL}/v2/stocks/snapshots?symbols=AAPL",
    f"{ALPACA_BASE_URL}/v2/stocks/quotes?symbols=AAPL&limit=1",
]

for endpoint in endpoints:
    try:
        print(f"\nTesting: {endpoint}")
        response = requests.get(endpoint, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON Data: {data}")
            except:
                print("Response is not valid JSON")
    except Exception as e:
        print(f"Error: {e}")

print(f"\n=== Debug Complete ===")
