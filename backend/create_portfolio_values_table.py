#!/usr/bin/env python3
"""
Create the portfolio_values table
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from models import PortfolioValues

def create_table():
    """Create the portfolio_values table"""
    try:
        # Create the table
        PortfolioValues.__table__.create(engine, checkfirst=True)
        print("✅ Successfully created portfolio_values table")
    except Exception as e:
        print(f"Error creating table: {e}")

if __name__ == "__main__":
    create_table()
