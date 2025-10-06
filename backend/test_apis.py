#!/usr/bin/env python3
"""
Test the APIs to see what's working
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
ALPACA_API_KEY = os.getenv('APCA_API_KEY_ID')
ALPACA_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
TWELVE_DATA_API_KEY = os.getenv('TWELVE_DATA_API_KEY')
ALPACA_BASE_URL = os.getenv('APCA_API_BASE_URL', 'https://api.alpaca.markets')

print(f"Alpaca API Key: {ALPACA_API_KEY}")
print(f"Alpaca Secret: {ALPACA_SECRET_KEY[:10]}...")
print(f"Twelve Data API Key: {TWELVE_DATA_API_KEY}")
print(f"Alpaca Base URL: {ALPACA_BASE_URL}")

# Test Alpaca API
print("\n=== Testing Alpaca API ===")
try:
    # Test account info first
    url = f"{ALPACA_BASE_URL}/v2/account"
    headers = {
        "APCA-API-KEY-ID": ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Account API Status: {response.status_code}")
    print(f"Account API Response: {response.text[:200]}...")
    
    # Test stock quote
    url = f"{ALPACA_BASE_URL}/v2/stocks/AAPL/quotes/latest"
    response = requests.get(url, headers=headers, timeout=10)
    print(f"AAPL Quote Status: {response.status_code}")
    print(f"AAPL Quote Response: {response.text[:200]}...")
    
except Exception as e:
    print(f"Alpaca API Error: {e}")

# Test Twelve Data API
print("\n=== Testing Twelve Data API ===")
try:
    url = f"https://api.twelvedata.com/price?symbol=AAPL&apikey={TWELVE_DATA_API_KEY}"
    response = requests.get(url, timeout=10)
    print(f"AAPL Price Status: {response.status_code}")
    print(f"AAPL Price Response: {response.text}")
    
    # Test crypto
    url = f"https://api.twelvedata.com/price?symbol=BTC&apikey={TWELVE_DATA_API_KEY}"
    response = requests.get(url, timeout=10)
    print(f"BTC Price Status: {response.status_code}")
    print(f"BTC Price Response: {response.text}")
    
except Exception as e:
    print(f"Twelve Data API Error: {e}")

print("\n=== API Test Complete ===")
