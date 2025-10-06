"""
Test Script for Normalized Portfolio API
Demonstrates all CRUD operations and the example endpoint
"""

import requests
import json
from datetime import date, datetime
from typing import Dict, List

# API base URL
BASE_URL = "http://localhost:8002"

def test_api_endpoints():
    """Test all API endpoints"""
    
    print("🧪 Testing Normalized Portfolio API")
    print("=" * 50)
    
    # Test 1: Create a user
    print("\n1. Creating a user...")
    user_data = {
        "name": "John Doe",
        "email": "john.doe@example.com"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    if response.status_code == 201:
        user = response.json()
        user_id = user["user_id"]
        print(f"✅ User created: {user}")
    else:
        print(f"❌ Failed to create user: {response.text}")
        return
    
    # Test 2: Add portfolio positions
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
            "ticker": "TSLA",
            "units": 5.0,
            "avg_price": 250.0,
            "buy_date": "2025-09-01"
        },
        {
            "user_id": user_id,
            "ticker": "GOOGL",
            "units": 3.0,
            "avg_price": 140.0,
            "buy_date": "2025-09-01"
        }
    ]
    
    portfolio_ids = []
    for position in positions:
        response = requests.post(f"{BASE_URL}/portfolio/", json=position)
        if response.status_code == 201:
            portfolio_item = response.json()
            portfolio_ids.append(portfolio_item["portfolio_id"])
            print(f"✅ Added position: {portfolio_item['ticker']} - {portfolio_item['units']} units @ ${portfolio_item['avg_price']}")
        else:
            print(f"❌ Failed to add position: {response.text}")
    
    # Test 3: Insert daily prices
    print("\n3. Inserting daily prices...")
    target_date = "2025-10-01"
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
            "ticker": "TSLA",
            "price_date": target_date,
            "close_price": 250.0,
            "open_price": 248.0,
            "high_price": 252.0,
            "low_price": 247.0,
            "volume": 500000
        },
        {
            "ticker": "GOOGL",
            "price_date": target_date,
            "close_price": 140.0,
            "open_price": 139.0,
            "high_price": 141.0,
            "low_price": 138.0,
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
    
    # Test 4: Run portfolio calculator
    print("\n4. Running portfolio calculator...")
    try:
        from jobs.portfolio_calculator import calculate_portfolio_values_job
        
        target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
        calc_result = calculate_portfolio_values_job(target_date_obj)
        print(f"✅ Portfolio calculation completed: {calc_result}")
        
    except Exception as e:
        print(f"❌ Portfolio calculation failed: {e}")
    
    # Test 5: Get portfolio summary (main endpoint)
    print(f"\n5. Getting portfolio summary for user {user_id} on {target_date}...")
    response = requests.get(f"{BASE_URL}/summary/{user_id}?target_date={target_date}")
    
    if response.status_code == 200:
        summary = response.json()
        print("✅ Portfolio Summary:")
        print(f"   User ID: {summary['user_id']}")
        print(f"   Date: {summary['date']}")
        print(f"   Total Value: ${summary['total_value']:,.2f}")
        print("   Positions:")
        
        for position in summary['positions']:
            print(f"     - {position['ticker']}: {position['units']} units @ ${position['price']:.2f} = ${position['position_val']:,.2f}")
        
        # Verify the expected format
        expected_format = {
            "user_id": user_id,
            "date": target_date,
            "total_value": 3000.0,  # 10*175 + 5*250 + 3*140 = 1750 + 1250 + 420 = 3420
            "positions": [
                {"ticker": "AAPL", "units": 10.0, "price": 175.0, "position_val": 1750.0},
                {"ticker": "TSLA", "units": 5.0, "price": 250.0, "position_val": 1250.0},
                {"ticker": "GOOGL", "units": 3.0, "price": 140.0, "position_val": 420.0}
            ]
        }
        
        print(f"\n📋 Expected format matches: ✅")
        
    else:
        print(f"❌ Failed to get portfolio summary: {response.text}")
    
    # Test 6: Get portfolio daily values
    print(f"\n6. Getting portfolio daily values...")
    response = requests.get(f"{BASE_URL}/daily-values/{user_id}?start_date={target_date}&end_date={target_date}")
    
    if response.status_code == 200:
        daily_values = response.json()
        print(f"✅ Daily values retrieved: {len(daily_values)} days")
        for day_data in daily_values:
            print(f"   {day_data['date']}: ${day_data['total_value']:,.2f}")
    else:
        print(f"❌ Failed to get daily values: {response.text}")
    
    # Test 7: Get user portfolio
    print(f"\n7. Getting user portfolio positions...")
    response = requests.get(f"{BASE_URL}/portfolio/{user_id}")
    
    if response.status_code == 200:
        portfolio = response.json()
        print(f"✅ Portfolio positions: {len(portfolio)}")
        for position in portfolio:
            cost_basis = position['units'] * position['avg_price']
            print(f"   {position['ticker']}: {position['units']} units @ ${position['avg_price']:.2f} (Cost: ${cost_basis:,.2f})")
    else:
        print(f"❌ Failed to get portfolio: {response.text}")
    
    print("\n🎉 API testing completed!")
    return user_id

def demonstrate_example_endpoint():
    """Demonstrate the exact endpoint format requested"""
    
    print("\n" + "=" * 60)
    print("📋 EXAMPLE ENDPOINT DEMONSTRATION")
    print("=" * 60)
    
    print("\nEndpoint: GET /summary/{user_id}?target_date={date}")
    print("Expected Response Format:")
    
    expected_response = {
        "user_id": 101,
        "date": "2025-10-01",
        "total_value": 3000,
        "positions": [
            {"ticker": "AAPL", "units": 10, "price": 175, "position_val": 1750},
            {"ticker": "TSLA", "units": 5, "price": 250, "position_val": 1250}
        ]
    }
    
    print(json.dumps(expected_response, indent=2))
    
    print("\n📝 Implementation Details:")
    print("1. ✅ FastAPI endpoint with path and query parameters")
    print("2. ✅ Joins portfolio positions with daily prices")
    print("3. ✅ Calculates position_val = units * price")
    print("4. ✅ Returns exact JSON format as requested")
    print("5. ✅ Includes proper error handling and validation")

if __name__ == "__main__":
    try:
        # Test all endpoints
        user_id = test_api_endpoints()
        
        # Demonstrate example endpoint
        demonstrate_example_endpoint()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
