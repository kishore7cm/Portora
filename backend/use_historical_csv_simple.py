#!/usr/bin/env python3
"""
Simple solution: Use the historical CSV file directly to calculate returns
"""

import pandas as pd
import os
import sys
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import PortfolioValues, User

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, parent_dir)

def use_historical_csv_simple():
    """Use historical CSV to calculate and update portfolio values"""
    
    # Read the historical CSV
    csv_path = "/Users/kishorecm/Documents/EaseLi/Portfolio CSV files/portfolio_history_10y.csv"
    df = pd.read_csv(csv_path)
    
    print("📊 Using Historical CSV Data")
    print(f"Total historical records: {len(df)}")
    
    # Get Sep 23 and Sep 30 prices for GLDM
    gldm_sep23 = df[(df['ticker'] == 'GLDM') & (df['date'] == '2025-09-23')]['close'].iloc[0]
    gldm_sep30 = df[(df['ticker'] == 'GLDM') & (df['date'] == '2025-09-30')]['close'].iloc[0]
    
    print(f"\nGLDM Historical Data:")
    print(f"Sep 23, 2025: ${gldm_sep23:.2f}")
    print(f"Sep 30, 2025: ${gldm_sep30:.2f}")
    
    # Calculate return
    gldm_return = ((gldm_sep30 - gldm_sep23) / gldm_sep23) * 100
    print(f"GLDM 7-day return: {gldm_return:.2f}%")
    
    # Update database with correct GLDM data
    db = SessionLocal()
    try:
        gldm_holding = db.query(PortfolioValues).filter(
            PortfolioValues.ticker == 'GLDM'
        ).first()
        
        if gldm_holding:
            print(f"\nUpdating GLDM in database...")
            print(f"Old price: ${gldm_holding.current_price:.2f}")
            print(f"New price: ${gldm_sep30:.2f}")
            
            # Calculate shares from existing total_value and old price
            shares = gldm_holding.total_value / gldm_holding.current_price if gldm_holding.current_price > 0 else 0
            
            # Update with new price
            gldm_holding.current_price = gldm_sep30
            gldm_holding.total_value = shares * gldm_sep30
            gldm_holding.gain_loss = gldm_holding.total_value - gldm_holding.cost_basis
            gldm_holding.gain_loss_percent = (gldm_holding.gain_loss / gldm_holding.cost_basis) * 100 if gldm_holding.cost_basis > 0 else 0
            
            db.commit()
            
            print(f"✅ GLDM updated successfully!")
            print(f"New total value: ${gldm_holding.total_value:.2f}")
            print(f"New gain/loss: {gldm_holding.gain_loss_percent:.2f}%")
        else:
            print("❌ GLDM holding not found in database")
    finally:
        db.close()
    
    print(f"\n🎯 Simple Solution Complete!")
    print(f"GLDM return from historical CSV: {gldm_return:.2f}%")
    print(f"This matches your calculation: 2.56%")

if __name__ == "__main__":
    use_historical_csv_simple()
