#!/usr/bin/env python3
"""
Import real portfolio data from CSV files into the database
"""

import sys
import os
import csv
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from models import Portfolio, User
from sqlalchemy.orm import Session

def import_real_portfolio():
    """Import real portfolio data from CSV"""
    
    # Get database session
    db = next(get_db())
    
    # Clear existing portfolio data for user 1
    print("Clearing existing portfolio data...")
    db.query(Portfolio).filter(Portfolio.user_id == 1).delete()
    db.commit()
    
    # Read the real portfolio CSV
    csv_path = "/Users/kishorecm/Documents/EaseLi/Portfolio CSV files/master_portfolio_new.csv"
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return
    
    print(f"Reading portfolio data from {csv_path}...")
    
    total_value = 0
    holdings_count = 0
    
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            try:
                # Extract data from CSV
                symbol = row['symbol']
                
                # Handle cash entries that have empty shares
                if row['shares'] == '' or row['shares'] == '0':
                    shares = 1.0  # Cash is treated as 1 share at $1
                    purchase_price = float(row['purchase_price'])
                else:
                    shares = float(row['shares'])
                    purchase_price = float(row['purchase_price'])
                
                total_cost = float(row['total_cost'])
                total_value_csv = float(row['total_value'])
                asset_type = row['asset_type']
                
                # Calculate current price (total_value / shares)
                current_price = total_value_csv / shares if shares > 0 else 0
                
                # Determine category based on asset_type
                if asset_type == 'ETF':
                    category = 'ETF'
                elif asset_type == 'Bond':
                    category = 'Bond'
                elif asset_type == 'Stock':
                    category = 'Stock'
                else:
                    category = 'Other'
                
                # Create portfolio entry (only using fields that exist in the model)
                portfolio_entry = Portfolio(
                    user_id=1,
                    ticker=symbol,
                    shares=shares,
                    avg_price=purchase_price
                )
                
                db.add(portfolio_entry)
                total_value += total_value_csv
                holdings_count += 1
                
                print(f"  {symbol}: {shares:.2f} shares @ ${purchase_price:.2f} = ${total_value_csv:,.2f}")
                
            except Exception as e:
                print(f"Error processing row {row}: {e}")
                continue
    
    # Commit all changes
    db.commit()
    
    print(f"\n✅ Successfully imported {holdings_count} holdings")
    print(f"💰 Total Portfolio Value: ${total_value:,.2f}")
    
    # Verify the import
    print("\nVerifying import...")
    imported_holdings = db.query(Portfolio).filter(Portfolio.user_id == 1).all()
    print(f"Database now contains {len(imported_holdings)} holdings")
    
    # Show top 10 holdings by shares
    print("\nTop 10 holdings by shares:")
    top_holdings = sorted(imported_holdings, key=lambda x: x.shares, reverse=True)[:10]
    for holding in top_holdings:
        print(f"  {holding.ticker}: {holding.shares:.2f} shares @ ${holding.avg_price:.2f}")

if __name__ == "__main__":
    import_real_portfolio()
