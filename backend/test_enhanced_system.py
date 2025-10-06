"""
Enhanced System Test - Complete Asset Type Handling
Tests stocks, bond ETFs, crypto, bonds-as-cash, and cash transactions
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import requests
import json
from datetime import date, datetime, timedelta
from typing import Dict, List

# Import our enhanced services
from services.enhanced_price_updater import update_daily_prices, categorize_portfolio_tickers
from jobs.enhanced_daily_calculator import (
    calculate_enhanced_daily_portfolio_job, 
    add_bond_cash_position
)
from jobs.daily_portfolio_calculator import add_cash_transaction

# API base URL
BASE_URL = "http://localhost:8002"

def test_enhanced_workflow():
    """Test the complete enhanced workflow with all asset types"""
    
    print("🧪 Testing Enhanced Portfolio System")
    print("=" * 60)
    
    # Step 1: Create test user
    print("\n1. Setting up enhanced test data...")
    
    user_data = {
        "name": "Enhanced Test User",
        "email": "enhanced@portfolio.com"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    if response.status_code == 201:
        user = response.json()
        user_id = user["user_id"]
        print(f"✅ User created: {user}")
    else:
        print(f"❌ Failed to create user: {response.text}")
        return
    
    # Step 2: Add diverse portfolio positions
    print(f"\n2. Adding diverse portfolio positions for user {user_id}...")
    
    positions = [
        # Stocks
        {
            "user_id": user_id,
            "ticker": "AAPL",
            "units": 10.0,
            "avg_price": 175.0,
            "buy_date": "2025-09-01"
        },
        {
            "user_id": user_id,
            "ticker": "MSFT",
            "units": 5.0,
            "avg_price": 350.0,
            "buy_date": "2025-09-01"
        },
        # Bond ETFs
        {
            "user_id": user_id,
            "ticker": "BND",
            "units": 20.0,
            "avg_price": 80.0,
            "buy_date": "2025-09-01"
        },
        {
            "user_id": user_id,
            "ticker": "AGG",
            "units": 15.0,
            "avg_price": 100.0,
            "buy_date": "2025-09-01"
        },
        # Crypto
        {
            "user_id": user_id,
            "ticker": "BTC-USD",
            "units": 0.5,
            "avg_price": 50000.0,
            "buy_date": "2025-09-01"
        },
        {
            "user_id": user_id,
            "ticker": "ETH-USD",
            "units": 2.0,
            "avg_price": 3000.0,
            "buy_date": "2025-09-01"
        },
        # Cash position
        {
            "user_id": user_id,
            "ticker": "CASH_USD",
            "units": 1.0,
            "avg_price": 5000.0,  # $5000 cash
            "buy_date": "2025-09-01"
        }
    ]
    
    for position in positions:
        response = requests.post(f"{BASE_URL}/portfolio/", json=position)
        if response.status_code == 201:
            portfolio_item = response.json()
            print(f"✅ Added {portfolio_item['ticker']}: {portfolio_item['units']} units @ ${portfolio_item['avg_price']}")
        else:
            print(f"❌ Failed to add position: {response.text}")
    
    # Step 3: Add bond cash position (non-ETF bond)
    print(f"\n3. Adding bond cash position...")
    success = add_bond_cash_position(user_id, "Treasury_10Y", 10000.0)
    if success:
        print("✅ Added Treasury 10Y bond as cash position: $10,000")
    else:
        print("❌ Failed to add bond cash position")
    
    # Step 4: Add sample prices for market-traded assets
    print("\n4. Adding sample daily prices...")
    target_date = "2025-10-02"
    
    prices = [
        # Stock prices
        {
            "ticker": "AAPL",
            "price_date": target_date,
            "close_price": 180.0,  # +$5 gain
            "open_price": 179.0,
            "high_price": 181.0,
            "low_price": 178.0,
            "volume": 1000000
        },
        {
            "ticker": "MSFT",
            "price_date": target_date,
            "close_price": 360.0,  # +$10 gain
            "open_price": 358.0,
            "high_price": 362.0,
            "low_price": 357.0,
            "volume": 800000
        },
        # Bond ETF prices
        {
            "ticker": "BND",
            "price_date": target_date,
            "close_price": 82.0,  # +$2 gain
            "open_price": 81.5,
            "high_price": 82.5,
            "low_price": 81.0,
            "volume": 500000
        },
        {
            "ticker": "AGG",
            "price_date": target_date,
            "close_price": 102.0,  # +$2 gain
            "open_price": 101.5,
            "high_price": 102.5,
            "low_price": 101.0,
            "volume": 400000
        },
        # Crypto prices
        {
            "ticker": "BTC-USD",
            "price_date": target_date,
            "close_price": 55000.0,  # +$5000 gain
            "open_price": 54500.0,
            "high_price": 55500.0,
            "low_price": 54000.0,
            "volume": 100000
        },
        {
            "ticker": "ETH-USD",
            "price_date": target_date,
            "close_price": 3200.0,  # +$200 gain
            "open_price": 3150.0,
            "high_price": 3250.0,
            "low_price": 3100.0,
            "volume": 200000
        }
    ]
    
    for price_data in prices:
        response = requests.post(f"{BASE_URL}/prices/", json=price_data)
        if response.status_code == 201:
            price = response.json()
            print(f"✅ Added price: {price['ticker']} @ ${price['close_price']} on {price['price_date']}")
        else:
            print(f"❌ Failed to add price: {response.text}")
    
    # Step 5: Add cash transactions
    print(f"\n5. Adding cash transactions...")
    
    # Initial deposit
    success = add_cash_transaction(user_id, 3000.0, "deposit", 
                                 datetime.strptime("2025-09-01", "%Y-%m-%d").date(),
                                 "Initial cash deposit")
    if success:
        print("✅ Added initial cash deposit: $3,000")
    
    # Small withdrawal
    success = add_cash_transaction(user_id, 500.0, "withdrawal",
                                 datetime.strptime("2025-09-15", "%Y-%m-%d").date(),
                                 "ATM withdrawal")
    if success:
        print("✅ Added cash withdrawal: $500")
    
    # Step 6: Run enhanced portfolio calculator
    print("\n6. Running enhanced portfolio calculator...")
    try:
        target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
        calc_result = calculate_enhanced_daily_portfolio_job(target_date_obj)
        print(f"✅ Enhanced calculation completed: {calc_result}")
        
    except Exception as e:
        print(f"❌ Enhanced calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 7: Test the enhanced portfolio endpoint
    print(f"\n7. Testing enhanced portfolio endpoint...")
    response = requests.get(f"{BASE_URL}/portfolio/{user_id}/{target_date}")
    
    if response.status_code == 200:
        portfolio_data = response.json()
        print("✅ Enhanced Portfolio Response:")
        print(json.dumps(portfolio_data, indent=2))
        
        # Calculate expected values
        expected_values = {
            'AAPL': 10 * 180.0,      # 1800
            'MSFT': 5 * 360.0,       # 1800  
            'BND': 20 * 82.0,        # 1640
            'AGG': 15 * 102.0,       # 1530
            'BTC-USD': 0.5 * 55000.0, # 27500
            'ETH-USD': 2.0 * 3200.0,  # 6400
            'CASH_USD': 5000.0,       # 5000 (constant)
            'BOND_CASH': 10000.0,     # 10000 (constant)
        }
        
        expected_portfolio_total = sum(expected_values.values())  # 55670
        expected_cash_from_transactions = 3000 - 500  # 2500
        expected_total = expected_portfolio_total + expected_cash_from_transactions  # 58170
        
        print(f"\n📊 Enhanced Value Verification:")
        print(f"Expected Portfolio Total: ${expected_portfolio_total:,.2f}")
        print(f"Expected Cash from Transactions: ${expected_cash_from_transactions:,.2f}")
        print(f"Expected Grand Total: ${expected_total:,.2f}")
        print(f"Actual Total: ${portfolio_data['total_value']:,.2f}")
        print(f"Actual Cash: ${portfolio_data['cash']:,.2f}")
        
        # Verify position breakdown
        print(f"\n📋 Position Breakdown:")
        for position in portfolio_data['positions']:
            ticker = position['ticker']
            actual_val = position['position_val']
            if ticker in expected_values:
                expected_val = expected_values[ticker]
                print(f"  {ticker}: Expected ${expected_val:,.2f}, Actual ${actual_val:,.2f}")
        
    else:
        print(f"❌ Failed to get enhanced portfolio data: {response.text}")
    
    # Step 8: Test enhanced price updater categorization
    print(f"\n8. Testing enhanced price updater categorization...")
    try:
        stock_tickers, bond_etf_tickers, crypto_tickers, bond_cash_tickers, cash_tickers = categorize_portfolio_tickers()
        
        print(f"✅ Portfolio Categorization:")
        print(f"  📈 Stocks: {stock_tickers}")
        print(f"  🏦 Bond ETFs: {bond_etf_tickers}")
        print(f"  ₿ Crypto: {crypto_tickers}")
        print(f"  💰 Bond Cash: {bond_cash_tickers}")
        print(f"  💵 Cash: {cash_tickers}")
        
        # Test enhanced price updater (will show structure even without API keys)
        results = update_daily_prices(stock_tickers, bond_etf_tickers, crypto_tickers)
        print(f"✅ Enhanced price update results: {results}")
        
    except Exception as e:
        print(f"⚠️ Enhanced price updater test failed (expected without API keys): {e}")
    
    print("\n🎉 Enhanced system test completed!")
    return user_id

def demonstrate_enhanced_features():
    """Demonstrate the enhanced features and asset type handling"""
    
    print("\n" + "=" * 60)
    print("🚀 ENHANCED FEATURES DEMONSTRATION")
    print("=" * 60)
    
    print("\n📊 Asset Type Handling:")
    print("1. ✅ Stocks & ETFs: Fetch daily prices from Alpaca API")
    print("2. ✅ Bond ETFs: Fetch daily prices from Alpaca API (trade like stocks)")
    print("3. ✅ Crypto: Fetch daily prices from Twelve Data API")
    print("4. ✅ Bonds (non-ETF): Treated as cash, constant value until user updates")
    print("5. ✅ Cash: Managed via cash_transactions, carried forward daily")
    
    print("\n🔄 Enhanced Daily Job Process:")
    print("1. ✅ Categorize portfolio positions by asset type")
    print("2. ✅ Market assets: Join with daily_prices, calculate units × price")
    print("3. ✅ Bond cash: Carry forward value from portfolio table")
    print("4. ✅ Cash positions: Carry forward constant value")
    print("5. ✅ Transaction cash: Calculate from cash_transactions table")
    print("6. ✅ Aggregate all values for portfolio_summary")
    
    print("\n💡 Key Enhancements:")
    print("• Asset type auto-detection and categorization")
    print("• Separate handling for different price sources")
    print("• Bond cash positions (BOND_CASH_* tickers)")
    print("• Cash transaction tracking and carry-forward")
    print("• Bulk price insertion for efficiency")
    print("• Comprehensive error handling and logging")
    
    print("\n📋 Example Portfolio Composition:")
    example_portfolio = {
        "stocks": ["AAPL", "MSFT", "GOOGL"],
        "bond_etfs": ["BND", "AGG", "TLT"],
        "crypto": ["BTC-USD", "ETH-USD"],
        "bond_cash": ["BOND_CASH_TREASURY_10Y"],
        "cash_positions": ["CASH_USD"],
        "cash_transactions": [
            {"type": "deposit", "amount": 3000, "date": "2025-09-01"},
            {"type": "withdrawal", "amount": 500, "date": "2025-09-15"}
        ]
    }
    
    print(json.dumps(example_portfolio, indent=2))

if __name__ == "__main__":
    try:
        # Test the enhanced workflow
        user_id = test_enhanced_workflow()
        
        # Demonstrate enhanced features
        demonstrate_enhanced_features()
        
    except Exception as e:
        print(f"❌ Enhanced test failed: {e}")
        import traceback
        traceback.print_exc()
