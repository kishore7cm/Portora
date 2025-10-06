#!/usr/bin/env python3
"""
Debug all GLDM entries in database
"""

import os
import sys
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import PortfolioValues, User

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, parent_dir)

def debug_gldm_all():
    """Debug all GLDM entries in database"""
    db = SessionLocal()
    try:
        # Check all GLDM holdings
        gldm_holdings = db.query(PortfolioValues).filter(
            PortfolioValues.ticker == 'GLDM'
        ).all()
        
        print(f"Found {len(gldm_holdings)} GLDM entries:")
        for i, holding in enumerate(gldm_holdings):
            print(f"  Entry {i+1}:")
            print(f"    ID: {holding.id}")
            print(f"    User ID: {holding.user_id}")
            print(f"    Current Price: ${holding.current_price:.2f}")
            print(f"    Total Value: ${holding.total_value:.2f}")
            print(f"    Cost Basis: ${holding.cost_basis:.2f}")
            print(f"    Gain/Loss: ${holding.gain_loss:.2f}")
            print(f"    Gain/Loss %: {holding.gain_loss_percent:.2f}%")
            print()
        
        # Update all GLDM entries to correct price
        print("Updating all GLDM entries to correct price...")
        for holding in gldm_holdings:
            holding.current_price = 76.45
            # Recalculate total value based on shares
            shares = holding.total_value / holding.current_price if holding.current_price > 0 else 0
            holding.total_value = shares * 76.45
            holding.gain_loss = holding.total_value - holding.cost_basis
            holding.gain_loss_percent = (holding.gain_loss / holding.cost_basis) * 100 if holding.cost_basis > 0 else 0
        
        db.commit()
        print("✅ All GLDM entries updated!")
        
        # Check again
        gldm_updated = db.query(PortfolioValues).filter(
            PortfolioValues.ticker == 'GLDM'
        ).all()
        print(f"\nAfter update - Found {len(gldm_updated)} GLDM entries:")
        for i, holding in enumerate(gldm_updated):
            print(f"  Entry {i+1}:")
            print(f"    Current Price: ${holding.current_price:.2f}")
            print(f"    Total Value: ${holding.total_value:.2f}")
            print(f"    Gain/Loss: ${holding.gain_loss:.2f}")
            print(f"    Gain/Loss %: {holding.gain_loss_percent:.2f}%")
            print()
            
    finally:
        db.close()

if __name__ == "__main__":
    debug_gldm_all()
