#!/usr/bin/env python3
"""
Test correct Alpaca API endpoints based on current documentation
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

print(f"Testing correct Alpaca API endpoints...")

# Test the correct endpoints based on current Alpaca API v2 documentation
endpoints_to_test = [
    # Market data endpoints
    f"{ALPACA_BASE_URL}/v2/stocks/bars?symbols=AAPL&limit=1",
    f"{ALPACA_BASE_URL}/v2/stocks/bars?symbols=AAPL&start=2025-09-23&end=2025-09-24&timeframe=1Day",
    f"{ALPACA_BASE_URL}/v2/stocks/snapshots?symbols=AAPL",
    f"{ALPACA_BASE_URL}/v2/stocks/quotes?symbols=AAPL&limit=1",
    f"{ALPACA_BASE_URL}/v2/stocks/trades?symbols=AAPL&limit=1",
]

for endpoint in endpoints_to_test:
    try:
        print(f"\nTesting: {endpoint}")
        response = requests.get(endpoint, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Response: {str(data)[:300]}...")
        else:
            print(f"Error: {response.text[:200]}...")
    except Exception as e:
        print(f"Exception: {e}")

# Test account info to verify API keys work
print(f"\n=== Testing Account Info ===")
try:
    account_url = f"{ALPACA_BASE_URL}/v2/account"
    response = requests.get(account_url, headers=headers, timeout=10)
    print(f"Account Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Account Status: {data.get('status', 'Unknown')}")
        print(f"Account Number: {data.get('account_number', 'Unknown')}")
    else:
        print(f"Account Error: {response.text[:200]}...")
except Exception as e:
    print(f"Account Exception: {e}")

print("\n=== API Test Complete ===")
