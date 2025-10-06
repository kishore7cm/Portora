#!/usr/bin/env python3
"""
Compare CSV data vs Database data to see if they match
"""

import pandas as pd
import os
import sys
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import PortfolioValues, User

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, parent_dir)

def compare_csv_vs_db():
    """Compare CSV data vs Database data"""
    
    print("=== COMPARING CSV vs DATABASE ===\n")
    
    # 1. Read CSV data
    csv_path = "/Users/kishorecm/Documents/EaseLi/Portfolio CSV files/portfolio_history_10y.csv"
    df = pd.read_csv(csv_path)
    
    print("📊 CSV Data:")
    print(f"Total records: {len(df)}")
    
    # Get GLDM data from CSV
    gldm_csv = df[df['ticker'] == 'GLDM'].tail(5)
    print(f"\nGLDM in CSV (last 5 records):")
    for _, row in gldm_csv.iterrows():
        print(f"  {row['date']}: ${row['close']:.2f}")
    
    # Get Sep 23 and Sep 30 prices
    gldm_sep23_csv = df[(df['ticker'] == 'GLDM') & (df['date'] == '2025-09-23')]['close'].iloc[0]
    gldm_sep30_csv = df[(df['ticker'] == 'GLDM') & (df['date'] == '2025-09-30')]['close'].iloc[0]
    csv_return = ((gldm_sep30_csv - gldm_sep23_csv) / gldm_sep23_csv) * 100
    
    print(f"\nCSV GLDM Calculation:")
    print(f"Sep 23: ${gldm_sep23_csv:.2f}")
    print(f"Sep 30: ${gldm_sep30_csv:.2f}")
    print(f"Return: {csv_return:.2f}%")
    
    # 2. Read Database data
    print(f"\n💾 Database Data:")
    db = SessionLocal()
    try:
        # Get all portfolio values
        portfolio_values = db.query(PortfolioValues).all()
        print(f"Total portfolio holdings: {len(portfolio_values)}")
        
        # Get GLDM from database
        gldm_db = db.query(PortfolioValues).filter(PortfolioValues.ticker == 'GLDM').first()
        
        if gldm_db:
            print(f"\nGLDM in Database:")
            print(f"  Current Price: ${gldm_db.current_price:.2f}")
            print(f"  Total Value: ${gldm_db.total_value:.2f}")
            print(f"  Cost Basis: ${gldm_db.cost_basis:.2f}")
            print(f"  Gain/Loss: ${gldm_db.gain_loss:.2f}")
            print(f"  Gain/Loss %: {gldm_db.gain_loss_percent:.2f}%")
        else:
            print("❌ GLDM not found in database")
        
        # Check a few other tickers for comparison
        print(f"\nOther holdings in Database (first 5):")
        for holding in portfolio_values[:5]:
            print(f"  {holding.ticker}: ${holding.current_price:.2f}")
            
    finally:
        db.close()
    
    # 3. Compare the data
    print(f"\n🔍 COMPARISON:")
    if gldm_db:
        print(f"CSV GLDM (Sep 30): ${gldm_sep30_csv:.2f}")
        print(f"DB GLDM Current:   ${gldm_db.current_price:.2f}")
        
        price_match = abs(gldm_sep30_csv - gldm_db.current_price) < 0.01
        print(f"Prices match: {'✅' if price_match else '❌'}")
        
        if not price_match:
            print(f"❌ DATABASE DOES NOT MATCH CSV!")
            print(f"   CSV has correct price: ${gldm_sep30_csv:.2f}")
            print(f"   DB has wrong price: ${gldm_db.current_price:.2f}")
        else:
            print(f"✅ Database matches CSV data")
    
    print(f"\n📈 Expected Return from CSV: {csv_return:.2f}%")
    print(f"🎯 Your calculation: 2.56%")
    print(f"Match: {'✅' if abs(csv_return - 2.56) < 0.01 else '❌'}")

if __name__ == "__main__":
    compare_csv_vs_db()
