#!/usr/bin/env python3
"""
Test direct database query to see what's actually in the database
"""

import os
import sys
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import PortfolioValues, User

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, parent_dir)

def test_direct_db():
    """Test direct database query"""
    db = SessionLocal()
    try:
        # Get all GLDM entries
        gldm_holdings = db.query(PortfolioValues).filter(
            PortfolioValues.ticker == 'GLDM'
        ).all()
        
        print(f"Direct DB Query - Found {len(gldm_holdings)} GLDM entries:")
        for i, holding in enumerate(gldm_holdings):
            print(f"  Entry {i+1}:")
            print(f"    ID: {holding.id}")
            print(f"    User ID: {holding.user_id}")
            print(f"    Ticker: {holding.ticker}")
            print(f"    Current Price: ${holding.current_price:.2f}")
            print(f"    Total Value: ${holding.total_value:.2f}")
            print(f"    Cost Basis: ${holding.cost_basis:.2f}")
            print(f"    Gain/Loss: ${holding.gain_loss:.2f}")
            print(f"    Gain/Loss %: {holding.gain_loss_percent:.2f}%")
            print()
        
        # Test the exact query the API uses
        print("Testing API query...")
        portfolio_values = db.query(PortfolioValues).filter(PortfolioValues.user_id == 1).all()
        gldm_api = [v for v in portfolio_values if v.ticker == 'GLDM']
        print(f"API Query - Found {len(gldm_api)} GLDM entries:")
        for i, holding in enumerate(gldm_api):
            print(f"  Entry {i+1}:")
            print(f"    Current Price: ${holding.current_price:.2f}")
            print(f"    Total Value: ${holding.total_value:.2f}")
            print(f"    Gain/Loss %: {holding.gain_loss_percent:.2f}%")
            print()
            
    finally:
        db.close()

if __name__ == "__main__":
    test_direct_db()
