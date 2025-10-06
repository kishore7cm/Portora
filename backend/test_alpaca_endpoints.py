#!/usr/bin/env python3
"""
Test different Alpaca API endpoints to find the correct one
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

print(f"Testing Alpaca API endpoints...")
print(f"API Key: {ALPACA_API_KEY}")
print(f"Base URL: {ALPACA_BASE_URL}")

# Test different endpoints
endpoints_to_test = [
    f"{ALPACA_BASE_URL}/v2/stocks/AAPL/latest/quote",
    f"{ALPACA_BASE_URL}/v2/stocks/AAPL/quotes/latest",
    f"{ALPACA_BASE_URL}/v2/stocks/AAPL/trades/latest",
    f"{ALPACA_BASE_URL}/v2/stocks/AAPL/snapshots",
    f"{ALPACA_BASE_URL}/v2/stocks/AAPL/bars/latest",
    f"{ALPACA_BASE_URL}/v2/stocks/AAPL/bars?symbols=AAPL&limit=1",
]

for endpoint in endpoints_to_test:
    try:
        print(f"\nTesting: {endpoint}")
        response = requests.get(endpoint, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Response: {str(data)[:200]}...")
        else:
            print(f"Error: {response.text[:200]}...")
    except Exception as e:
        print(f"Exception: {e}")

print("\n=== Testing Historical Data ===")
# Test historical data
historical_endpoints = [
    f"{ALPACA_BASE_URL}/v2/stocks/AAPL/bars?start=2025-09-23&end=2025-09-24&timeframe=1Day",
    f"{ALPACA_BASE_URL}/v2/stocks/bars?symbols=AAPL&start=2025-09-23&end=2025-09-24&timeframe=1Day",
]

for endpoint in historical_endpoints:
    try:
        print(f"\nTesting Historical: {endpoint}")
        response = requests.get(endpoint, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Response: {str(data)[:200]}...")
        else:
            print(f"Error: {response.text[:200]}...")
    except Exception as e:
        print(f"Exception: {e}")

print("\n=== API Test Complete ===")
