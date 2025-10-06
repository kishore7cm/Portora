#!/usr/bin/env python3
"""
Import actual portfolio values from CSV files into the PortfolioValues table
"""

import sys
import os
import csv
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from models import PortfolioValues, Portfolio
from sqlalchemy.orm import Session

def import_portfolio_values():
    """Import actual portfolio values from CSV"""
    
    # Get database session
    db = next(get_db())
    
    # Clear existing portfolio values for user 1
    print("Clearing existing portfolio values...")
    db.query(PortfolioValues).filter(PortfolioValues.user_id == 1).delete()
    db.commit()
    
    # Read the real portfolio CSV
    csv_path = "/Users/kishorecm/Documents/EaseLi/Portfolio CSV files/master_portfolio_new.csv"
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return
    
    print(f"Reading portfolio values from {csv_path}...")
    
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
                elif asset_type == 'Crypto':
                    category = 'Crypto'
                elif asset_type == 'Cash':
                    category = 'Cash'
                else:
                    category = 'Other'
                
                # Calculate gain/loss
                gain_loss = total_value_csv - total_cost
                gain_loss_percent = (gain_loss / total_cost * 100) if total_cost > 0 else 0
                
                # Create portfolio values entry
                portfolio_value = PortfolioValues(
                    user_id=1,
                    ticker=symbol,
                    current_price=current_price,
                    total_value=total_value_csv,
                    cost_basis=total_cost,
                    gain_loss=gain_loss,
                    gain_loss_percent=gain_loss_percent,
                    category=category
                )
                
                db.add(portfolio_value)
                total_value += total_value_csv
                holdings_count += 1
                
                print(f"  {symbol}: {shares:.2f} shares @ ${current_price:.2f} = ${total_value_csv:,.2f}")
                
            except Exception as e:
                print(f"Error processing row {row}: {e}")
                continue
    
    # Commit all changes
    db.commit()
    
    print(f"\n✅ Successfully imported {holdings_count} portfolio values")
    print(f"💰 Total Portfolio Value: ${total_value:,.2f}")
    
    # Verify the import
    print("\nVerifying import...")
    imported_values = db.query(PortfolioValues).filter(PortfolioValues.user_id == 1).all()
    print(f"Database now contains {len(imported_values)} portfolio values")
    
    # Show top 10 holdings by value
    print("\nTop 10 holdings by value:")
    top_holdings = sorted(imported_values, key=lambda x: x.total_value, reverse=True)[:10]
    for holding in top_holdings:
        print(f"  {holding.ticker}: ${holding.total_value:,.2f} ({holding.category})")

if __name__ == "__main__":
    import_portfolio_values()
