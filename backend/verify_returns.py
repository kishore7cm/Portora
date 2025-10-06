#!/usr/bin/env python3
"""
Verify the calculated returns from September 23rd, 2024
"""

import os
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal
from models import PortfolioValues, HistoricalData

# Add parent directory to sys.path for config imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, parent_dir)

def verify_returns():
    """Verify the calculated returns"""
    db = SessionLocal()
    try:
        # Get current portfolio values
        portfolio_values = db.query(PortfolioValues).filter(PortfolioValues.user_id == 1).all()
        
        if not portfolio_values:
            print("No portfolio data found")
            return
        
        print(f"Found {len(portfolio_values)} portfolio holdings")
        
        # September 23rd, 2024
        sep_23_2024 = datetime(2024, 9, 23).date()
        current_date = datetime.now().date()
        days_elapsed = (current_date - sep_23_2024).days
        
        print(f"Verifying returns from {sep_23_2024} to {current_date} ({days_elapsed} days)")
        
        total_current_value = 0
        total_starting_value = 0
        
        print(f"\n=== VERIFICATION DETAILS ===")
        
        for holding in portfolio_values:
            ticker = holding.ticker
            current_value = holding.total_value
            current_price = holding.current_price
            gain_loss = holding.gain_loss
            gain_loss_percent = holding.gain_loss_percent
            
            # Calculate starting value
            shares = current_value / current_price if current_price > 0 else 0
            starting_value = current_value - gain_loss
            
            total_current_value += current_value
            total_starting_value += starting_value
            
            print(f"{ticker}: ${starting_value:.2f} → ${current_value:.2f} ({gain_loss_percent:+.2f}%)")
        
        # Calculate total returns
        total_gain_loss = total_current_value - total_starting_value
        total_gain_loss_percent = (total_gain_loss / total_starting_value) * 100 if total_starting_value > 0 else 0
        
        # Calculate annualized return
        years_elapsed = days_elapsed / 365.25
        annualized_return = (total_current_value / total_starting_value) ** (1 / years_elapsed) - 1 if years_elapsed > 0 else 0
        
        print(f"\n=== VERIFICATION RESULTS ===")
        print(f"Total Starting Value: ${total_starting_value:,.2f}")
        print(f"Total Current Value: ${total_current_value:,.2f}")
        print(f"Total Gain/Loss: ${total_gain_loss:,.2f}")
        print(f"Total Return: {total_gain_loss_percent:+.2f}%")
        print(f"Annualized Return: {annualized_return * 100:+.2f}%")
        print(f"Days Elapsed: {days_elapsed}")
        
        # Check if the numbers match what we calculated
        expected_starting = 325850.92
        expected_current = 382017.16
        expected_gain = 56166.24
        expected_percent = 17.24
        
        print(f"\n=== COMPARISON ===")
        print(f"Expected Starting: ${expected_starting:,.2f}")
        print(f"Actual Starting:   ${total_starting_value:,.2f}")
        print(f"Match: {'✅' if abs(total_starting_value - expected_starting) < 1 else '❌'}")
        
        print(f"Expected Current: ${expected_current:,.2f}")
        print(f"Actual Current:   ${total_current_value:,.2f}")
        print(f"Match: {'✅' if abs(total_current_value - expected_current) < 1 else '❌'}")
        
        print(f"Expected Gain: ${expected_gain:,.2f}")
        print(f"Actual Gain:   ${total_gain_loss:,.2f}")
        print(f"Match: {'✅' if abs(total_gain_loss - expected_gain) < 1 else '❌'}")
        
        print(f"Expected Return: {expected_percent:.2f}%")
        print(f"Actual Return:   {total_gain_loss_percent:.2f}%")
        print(f"Match: {'✅' if abs(total_gain_loss_percent - expected_percent) < 0.1 else '❌'}")
        
        return {
            'total_starting_value': total_starting_value,
            'total_current_value': total_current_value,
            'total_gain_loss': total_gain_loss,
            'total_gain_loss_percent': total_gain_loss_percent,
            'annualized_return': annualized_return,
            'days_elapsed': days_elapsed
        }
        
    except Exception as e:
        print(f"Error verifying returns: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("Verifying calculated returns...")
    result = verify_returns()
    if result:
        print("Verification completed!")
    else:
        print("Verification failed!")
