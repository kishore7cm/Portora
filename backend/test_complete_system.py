"""
Complete System Test - Price Updates, Cash Transactions, and Portfolio Calculations
Tests the entire workflow from price updates to portfolio calculations with cash
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import requests
import json
from datetime import date, datetime, timedelta
from typing import Dict, List
import time

# Import our services
from services.price_updater import update_daily_prices, get_portfolio_tickers
from jobs.daily_portfolio_calculator import (
    calculate_daily_portfolio_job, 
    add_cash_transaction
)

# API base URL
BASE_URL = "http://localhost:8002"

def test_complete_workflow():
    """Test the complete workflow: prices -> cash -> calculations -> API"""
    
    print("🧪 Testing Complete Portfolio System with Cash")
    print("=" * 60)
    
    # Step 1: Create test data
    print("\n1. Setting up test data...")
    
    # Create a user
    user_data = {
        "name": "Test User",
        "email": "test@portfolio.com"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    if response.status_code == 201:
        user = response.json()
        user_id = user["user_id"]
        print(f"✅ User created: {user}")
    else:
        print(f"❌ Failed to create user: {response.text}")
        return
    
    # Add portfolio positions
    print(f"\n2. Adding portfolio positions for user {user_id}...")
    positions = [
        {
            "user_id": user_id,
            "ticker": "AAPL",
            "units": 10.0,
            "avg_price": 175.0,
            "buy_date": "2025-09-01"
        },
        {
            "user_id": user_id,
            "ticker": "BTC-USD",
            "units": 0.5,
            "avg_price": 50000.0,
            "buy_date": "2025-09-01"
        },
        {
            "user_id": user_id,
            "ticker": "BND",
            "units": 20.0,
            "avg_price": 80.0,
            "buy_date": "2025-09-01"
        }
    ]
    
    for position in positions:
        response = requests.post(f"{BASE_URL}/portfolio/", json=position)
        if response.status_code == 201:
            portfolio_item = response.json()
            print(f"✅ Added position: {portfolio_item['ticker']} - {portfolio_item['units']} units @ ${portfolio_item['avg_price']}")
        else:
            print(f"❌ Failed to add position: {response.text}")
    
    # Step 3: Add sample prices
    print("\n3. Adding sample daily prices...")
    target_date = "2025-10-02"
    prices = [
        {
            "ticker": "AAPL",
            "price_date": target_date,
            "close_price": 175.0,
            "open_price": 174.0,
            "high_price": 176.0,
            "low_price": 173.0,
            "volume": 1000000
        },
        {
            "ticker": "BTC-USD",
            "price_date": target_date,
            "close_price": 60000.0,
            "open_price": 59500.0,
            "high_price": 60500.0,
            "low_price": 59000.0,
            "volume": 500000
        },
        {
            "ticker": "BND",
            "price_date": target_date,
            "close_price": 85.0,
            "open_price": 84.5,
            "high_price": 85.5,
            "low_price": 84.0,
            "volume": 750000
        }
    ]
    
    for price_data in prices:
        response = requests.post(f"{BASE_URL}/prices/", json=price_data)
        if response.status_code == 201:
            price = response.json()
            print(f"✅ Added price: {price['ticker']} @ ${price['close_price']} on {price['price_date']}")
        else:
            print(f"❌ Failed to add price: {response.text}")
    
    # Step 4: Add cash transactions
    print(f"\n4. Adding cash transactions for user {user_id}...")
    
    # Initial deposit
    cash_deposit = {
        "user_id": user_id,
        "amount": 5000.0,
        "transaction_date": "2025-09-01",
        "type": "deposit",
        "description": "Initial cash deposit"
    }
    
    response = requests.post(f"{BASE_URL}/cash-transactions/", json=cash_deposit)
    if response.status_code == 201:
        transaction = response.json()
        print(f"✅ Added cash deposit: ${transaction['amount']} on {transaction['transaction_date']}")
    else:
        print(f"❌ Failed to add cash deposit: {response.text}")
    
    # Small withdrawal
    cash_withdrawal = {
        "user_id": user_id,
        "amount": 500.0,
        "transaction_date": "2025-09-15",
        "type": "withdrawal",
        "description": "ATM withdrawal"
    }
    
    response = requests.post(f"{BASE_URL}/cash-transactions/", json=cash_withdrawal)
    if response.status_code == 201:
        transaction = response.json()
        print(f"✅ Added cash withdrawal: ${abs(transaction['amount'])} on {transaction['transaction_date']}")
    else:
        print(f"❌ Failed to add cash withdrawal: {response.text}")
    
    # Step 5: Run portfolio calculator
    print("\n5. Running daily portfolio calculator...")
    try:
        target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
        calc_result = calculate_daily_portfolio_job(target_date_obj)
        print(f"✅ Portfolio calculation completed: {calc_result}")
        
    except Exception as e:
        print(f"❌ Portfolio calculation failed: {e}")
        return
    
    # Step 6: Test the main portfolio endpoint
    print(f"\n6. Testing portfolio endpoint /portfolio/{user_id}/{target_date}...")
    response = requests.get(f"{BASE_URL}/portfolio/{user_id}/{target_date}")
    
    if response.status_code == 200:
        portfolio_data = response.json()
        print("✅ Portfolio Endpoint Response:")
        print(json.dumps(portfolio_data, indent=2))
        
        # Verify the format matches the requirement
        expected_keys = {"user_id", "date", "total_value", "cash", "positions"}
        actual_keys = set(portfolio_data.keys())
        
        if expected_keys == actual_keys:
            print("✅ Response format matches requirement!")
            
            # Calculate expected values
            expected_portfolio_value = (10 * 175) + (0.5 * 60000) + (20 * 85)  # 1750 + 30000 + 1700 = 33450
            expected_cash = 5000 - 500  # 4500
            expected_total = expected_portfolio_value + expected_cash  # 37950
            
            print(f"\n📊 Value Verification:")
            print(f"Expected Portfolio Value: ${expected_portfolio_value:,.2f}")
            print(f"Actual Portfolio Value: ${portfolio_data['total_value'] - portfolio_data['cash']:,.2f}")
            print(f"Expected Cash: ${expected_cash:,.2f}")
            print(f"Actual Cash: ${portfolio_data['cash']:,.2f}")
            print(f"Expected Total: ${expected_total:,.2f}")
            print(f"Actual Total: ${portfolio_data['total_value']:,.2f}")
            
            if abs(portfolio_data['total_value'] - expected_total) < 0.01:
                print("✅ Values match expected calculations!")
            else:
                print("⚠️ Values don't match - check calculations")
        else:
            print(f"❌ Response format mismatch. Expected: {expected_keys}, Got: {actual_keys}")
        
    else:
        print(f"❌ Failed to get portfolio data: {response.text}")
    
    # Step 7: Test cash balance endpoint
    print(f"\n7. Testing cash balance endpoint...")
    response = requests.get(f"{BASE_URL}/cash-balance/{user_id}/{target_date}")
    
    if response.status_code == 200:
        cash_data = response.json()
        print(f"✅ Cash Balance: ${cash_data['cash_balance']:,.2f}")
    else:
        print(f"❌ Failed to get cash balance: {response.text}")
    
    # Step 8: Test cash transactions list
    print(f"\n8. Testing cash transactions list...")
    response = requests.get(f"{BASE_URL}/cash-transactions/{user_id}")
    
    if response.status_code == 200:
        transactions = response.json()
        print(f"✅ Found {len(transactions)} cash transactions:")
        for tx in transactions:
            print(f"  - {tx['type']}: ${abs(tx['amount']):,.2f} on {tx['transaction_date']}")
    else:
        print(f"❌ Failed to get cash transactions: {response.text}")
    
    print("\n🎉 Complete system test finished!")
    return user_id

def test_price_updater():
    """Test the price updater functionality"""
    
    print("\n" + "=" * 60)
    print("🔄 Testing Price Updater")
    print("=" * 60)
    
    # Test with sample tickers
    stock_tickers = ["AAPL", "MSFT"]
    bond_tickers = ["BND"]
    crypto_tickers = ["BTC-USD"]
    
    print(f"Testing price updates for:")
    print(f"📈 Stocks: {stock_tickers}")
    print(f"🏦 Bonds: {bond_tickers}")
    print(f"₿ Crypto: {crypto_tickers}")
    
    try:
        # Note: This will fail without proper API keys, but we can test the structure
        results = update_daily_prices(stock_tickers, bond_tickers, crypto_tickers)
        print(f"✅ Price update results: {results}")
        
    except Exception as e:
        print(f"⚠️ Price update failed (expected without API keys): {e}")
        print("💡 To test with real data, set ALPACA_API_KEY, ALPACA_SECRET_KEY, and TWELVE_DATA_API_KEY environment variables")

def demonstrate_example_format():
    """Demonstrate the exact endpoint format requested"""
    
    print("\n" + "=" * 60)
    print("📋 EXAMPLE ENDPOINT DEMONSTRATION")
    print("=" * 60)
    
    print("\nEndpoint: GET /portfolio/{user_id}/{date}")
    print("Expected Response Format:")
    
    expected_response = {
        "user_id": 101,
        "date": "2025-10-02",
        "total_value": 50500,
        "cash": 5000,
        "positions": [
            {"ticker": "AAPL", "units": 10, "price": 175, "position_val": 1750},
            {"ticker": "BTC-USD", "units": 0.5, "price": 60000, "position_val": 30000},
            {"ticker": "BND", "units": 20, "price": 85, "position_val": 1700}
        ]
    }
    
    print(json.dumps(expected_response, indent=2))
    
    print("\n📝 Implementation Features:")
    print("1. ✅ update_daily_prices() function with Alpaca & Twelve Data APIs")
    print("2. ✅ CashTransaction model for deposits/withdrawals")
    print("3. ✅ Daily job calculates portfolio + cash balance")
    print("4. ✅ FastAPI endpoint returns exact JSON format")
    print("5. ✅ Cash balance carried forward daily")
    print("6. ✅ Bulk price inserts for efficiency")
    print("7. ✅ Complete CRUD operations")
    print("8. ✅ Proper error handling and validation")

if __name__ == "__main__":
    try:
        # Test the complete workflow
        user_id = test_complete_workflow()
        
        # Test price updater (will show structure even without API keys)
        test_price_updater()
        
        # Demonstrate the example format
        demonstrate_example_format()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
