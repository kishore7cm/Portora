#!/usr/bin/env python3
"""
Test the new API v2 architecture
"""

import sys
sys.path.append('.')

from database import SessionLocal
from services.data_service import DataService
from services.portfolio_service import PortfolioService

def test_api_v2():
    """Test the new API v2 services"""
    print("🧪 Testing API v2 Architecture...")
    
    # Test database connection
    db = SessionLocal()
    
    try:
        # Test DataService
        print("\n1. Testing DataService...")
        data_service = DataService(db)
        
        user = data_service.get_user(1)
        print(f"✅ User: {user.name if user else 'Not found'}")
        
        holdings = data_service.get_portfolio_holdings(1)
        print(f"✅ Holdings: {len(holdings)}")
        
        gldm = data_service.get_holding_by_ticker(1, "GLDM")
        if gldm:
            print(f"✅ GLDM DB: ${gldm.current_price:.2f}, {gldm.gain_loss_percent:.2f}%")
        
        # Test CSV data
        csv_path = "/Users/kishorecm/Documents/EaseLi/Portfolio CSV files/portfolio_history_10y.csv"
        gldm_csv_price = data_service.get_latest_price("GLDM", csv_path)
        print(f"✅ GLDM CSV: ${gldm_csv_price:.2f}" if gldm_csv_price else "❌ GLDM CSV: Not found")
        
        # Test PortfolioService
        print("\n2. Testing PortfolioService...")
        portfolio_service = PortfolioService(data_service)
        
        summary = portfolio_service.get_portfolio_summary(1)
        print(f"✅ Portfolio Summary: {summary['status']}")
        print(f"✅ Total Holdings: {summary['summary']['Total_Holdings']}")
        print(f"✅ Total Value: ${summary['summary']['Total_Value']:.2f}")
        
        # Test GLDM specifically
        gldm_items = [item for item in summary["portfolio"] if item["Ticker"] == "GLDM"]
        if gldm_items:
            gldm_item = gldm_items[0]
            print(f"✅ GLDM in Portfolio: ${gldm_item['Current_Price']:.2f}, {gldm_item['Gain_Loss_Percent']:.2f}%")
        
        # Test GLDM debug
        gldm_debug = portfolio_service.get_gldm_debug_info(1)
        print(f"✅ GLDM Debug: {gldm_debug['status']}")
        print(f"   DB Price: ${gldm_debug['database']['current_price']:.2f}")
        print(f"   CSV Latest: ${gldm_debug['csv']['latest_price']:.2f}")
        print(f"   CSV Return: {gldm_debug['csv']['calculated_return']:.2f}%")
        
        print("\n✅ All API v2 tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_api_v2()
