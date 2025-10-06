#!/usr/bin/env python3
"""
Check GLDM data in database
"""

import os
import sys
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import PortfolioValues, User

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, parent_dir)

def check_gldm_database():
    """Check GLDM data in database"""
    db = SessionLocal()
    try:
        # Check GLDM holding
        gldm_holding = db.query(PortfolioValues).filter(
            PortfolioValues.ticker == 'GLDM'
        ).first()
        
        if gldm_holding:
            print(f"GLDM in database:")
            print(f"  Current Price: ${gldm_holding.current_price:.2f}")
            print(f"  Total Value: ${gldm_holding.total_value:.2f}")
            print(f"  Cost Basis: ${gldm_holding.cost_basis:.2f}")
            print(f"  Gain/Loss: ${gldm_holding.gain_loss:.2f}")
            print(f"  Gain/Loss %: {gldm_holding.gain_loss_percent:.2f}%")
            
            # Update to correct price
            print("\nUpdating GLDM to correct price...")
            gldm_holding.current_price = 76.45
            gldm_holding.total_value = gldm_holding.total_value / gldm_holding.current_price * 76.45  # Recalculate total value
            gldm_holding.gain_loss = gldm_holding.total_value - gldm_holding.cost_basis
            gldm_holding.gain_loss_percent = (gldm_holding.gain_loss / gldm_holding.cost_basis) * 100
            
            db.commit()
            print("✅ GLDM updated in database!")
            
            # Check again
            gldm_updated = db.query(PortfolioValues).filter(
                PortfolioValues.ticker == 'GLDM'
            ).first()
            print(f"\nGLDM after update:")
            print(f"  Current Price: ${gldm_updated.current_price:.2f}")
            print(f"  Total Value: ${gldm_updated.total_value:.2f}")
            print(f"  Gain/Loss: ${gldm_updated.gain_loss:.2f}")
            print(f"  Gain/Loss %: {gldm_updated.gain_loss_percent:.2f}%")
        else:
            print("GLDM not found in database")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_gldm_database()
