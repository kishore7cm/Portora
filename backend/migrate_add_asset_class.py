"""
Database migration to add asset_class column to portfolio table
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from core.database import SessionLocal, engine
from services.portfolio_calculation_service import PortfolioCalculationService

def migrate_add_asset_class():
    """Add asset_class column and populate it"""
    
    db = SessionLocal()
    
    try:
        # Check if column already exists
        result = db.execute(text("PRAGMA table_info(portfolio)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'asset_class' not in columns:
            print("Adding asset_class column to portfolio table...")
            
            # Add the column
            db.execute(text("ALTER TABLE portfolio ADD COLUMN asset_class VARCHAR(20)"))
            db.commit()
            
            print("✅ Added asset_class column")
            
            # Populate asset_class for existing records
            print("Populating asset_class for existing records...")
            
            service = PortfolioCalculationService(db)
            
            # Get all portfolio records
            result = db.execute(text("SELECT portfolio_id, ticker FROM portfolio"))
            records = result.fetchall()
            
            for portfolio_id, ticker in records:
                asset_class = service.classify_asset(ticker)
                db.execute(
                    text("UPDATE portfolio SET asset_class = :asset_class WHERE portfolio_id = :portfolio_id"),
                    {"asset_class": asset_class, "portfolio_id": portfolio_id}
                )
            
            db.commit()
            print(f"✅ Updated {len(records)} portfolio records with asset_class")
            
        else:
            print("✅ asset_class column already exists")
        
        # Check if PortfolioSummary needs new columns
        result = db.execute(text("PRAGMA table_info(portfolio_summary)"))
        summary_columns = [row[1] for row in result.fetchall()]
        
        new_columns = [
            ('equity_value', 'FLOAT DEFAULT 0.0'),
            ('bond_etf_value', 'FLOAT DEFAULT 0.0'), 
            ('crypto_value', 'FLOAT DEFAULT 0.0'),
            ('cash_value', 'FLOAT DEFAULT 0.0'),
            ('bond_cash_value', 'FLOAT DEFAULT 0.0')
        ]
        
        for col_name, col_def in new_columns:
            if col_name not in summary_columns:
                print(f"Adding {col_name} column to portfolio_summary table...")
                db.execute(text(f"ALTER TABLE portfolio_summary ADD COLUMN {col_name} {col_def}"))
                db.commit()
                print(f"✅ Added {col_name} column")
        
        print("🎉 Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_add_asset_class()
