#!/usr/bin/env python3
"""
Test API response vs database directly
"""

import os
import sys
import requests
import json
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import PortfolioValues, User

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, parent_dir)

def test_api_vs_db():
    """Test API response vs database directly"""
    
    # Test API response
    print("=== API Response ===")
    try:
        response = requests.get("http://localhost:8001/portfolio")
        if response.status_code == 200:
            data = response.json()
            gldm_api = [h for h in data['portfolio'] if h['Ticker'] == 'GLDM']
            if gldm_api:
                gldm = gldm_api[0]
                print(f"GLDM from API:")
                print(f"  Current Price: ${gldm['Current_Price']:.2f}")
                print(f"  Total Value: ${gldm['Total_Value']:.2f}")
                print(f"  Gain/Loss %: {gldm['Gain_Loss_Percent']:.2f}%")
            else:
                print("No GLDM found in API response")
        else:
            print(f"API Error: {response.status_code}")
    except Exception as e:
        print(f"API Error: {e}")
    
    print("\n=== Database Direct Query ===")
    # Test database directly
    db = SessionLocal()
    try:
        gldm_db = db.query(PortfolioValues).filter(
            PortfolioValues.ticker == 'GLDM'
        ).first()
        
        if gldm_db:
            print(f"GLDM from DB:")
            print(f"  Current Price: ${gldm_db.current_price:.2f}")
            print(f"  Total Value: ${gldm_db.total_value:.2f}")
            print(f"  Gain/Loss %: {gldm_db.gain_loss_percent:.2f}%")
        else:
            print("No GLDM found in database")
    finally:
        db.close()
    
    print("\n=== Comparison ===")
    if gldm_api and gldm_db:
        price_match = abs(gldm_api[0]['Current_Price'] - gldm_db.current_price) < 0.01
        value_match = abs(gldm_api[0]['Total_Value'] - gldm_db.total_value) < 0.01
        print(f"Price matches: {price_match}")
        print(f"Value matches: {value_match}")
        if not price_match or not value_match:
            print("❌ API and DB data don't match!")
        else:
            print("✅ API and DB data match!")

if __name__ == "__main__":
    test_api_vs_db()
