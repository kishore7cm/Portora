"""
Migration Script - Convert to Normalized Database Structure
Migrate from old portfolio_values to new normalized schema
"""

import sys
import pandas as pd
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add current directory to path
sys.path.append('.')

from domain.models_v2 import (
    Base, User, Portfolio, DailyPrice, PortfolioDailyValue, 
    PortfolioSummary, AssetCategory, create_all_tables
)
from services.portfolio_service_v2 import PortfolioServiceV2
from core.logging import logger

def migrate_portfolio_data():
    """Migrate existing portfolio data to new normalized structure"""
    
    print("🔄 Starting migration to normalized database structure...")
    
    # Create new database
    new_engine = create_engine("sqlite:///./portfolio_v2.db", echo=False)
    create_all_tables(new_engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=new_engine)
    db = SessionLocal()
    
    try:
        # Initialize service
        portfolio_service = PortfolioServiceV2(db)
        
        # Step 1: Create user
        print("👤 Creating user...")
        user = portfolio_service.create_user(
            name="Kishore Chandramouli",
            email="demo@portora.com"
        )
        print(f"✅ Created user: {user.name} (ID: {user.user_id})")
        
        # Step 2: Load original CSV data
        print("📊 Loading original CSV data...")
        csv_path = "../Portfolio CSV files/master_portfolio_new.csv"
        df = pd.read_csv(csv_path)
        
        # Group duplicates
        grouped_df = df.groupby('symbol').agg({
            'shares': 'sum',
            'total_cost': 'sum', 
            'total_value': 'sum',
            'asset_type': 'first',
            'account_name': 'first',
            'purchase_price': 'mean'  # Average purchase price
        }).reset_index()
        
        print(f"📈 Loaded {len(grouped_df)} unique positions from CSV")
        
        # Step 3: Create portfolio positions
        print("💼 Creating portfolio positions...")
        positions_created = 0
        
        for _, row in grouped_df.iterrows():
            try:
                # Calculate average price (weighted by shares)
                avg_price = row['total_cost'] / row['shares'] if row['shares'] > 0 else row['purchase_price']
                
                # Create portfolio position
                position = portfolio_service.add_portfolio_position(
                    user_id=user.user_id,
                    ticker=row['symbol'],
                    units=row['shares'],
                    avg_price=avg_price,
                    buy_date=date(2025, 9, 23)  # Portfolio creation date
                )
                
                positions_created += 1
                
                # Add asset category
                category = AssetCategory(
                    ticker=row['symbol'],
                    category=row['asset_type']
                )
                db.add(category)
                
            except Exception as e:
                print(f"❌ Failed to create position for {row['symbol']}: {e}")
        
        db.commit()
        print(f"✅ Created {positions_created} portfolio positions")
        
        # Step 4: Load historical price data from CSV
        print("📈 Loading historical price data...")
        historical_csv = "../Portfolio CSV files/portfolio_history_10y.csv"
        
        try:
            hist_df = pd.read_csv(historical_csv)
            hist_df['date'] = pd.to_datetime(hist_df['date']).dt.date
            
            prices_added = 0
            unique_tickers = hist_df['ticker'].unique()
            
            print(f"📊 Processing {len(unique_tickers)} tickers from historical data...")
            
            for ticker in unique_tickers:
                ticker_data = hist_df[hist_df['ticker'] == ticker].sort_values('date')
                
                for _, price_row in ticker_data.iterrows():
                    try:
                        portfolio_service.add_daily_price(
                            ticker=price_row['ticker'],
                            price_date=price_row['date'],
                            close_price=price_row['close'],
                            open_price=price_row.get('open'),
                            high_price=price_row.get('high'),
                            low_price=price_row.get('low'),
                            volume=price_row.get('volume')
                        )
                        prices_added += 1
                        
                        if prices_added % 1000 == 0:
                            print(f"  📈 Added {prices_added} price records...")
                            
                    except Exception as e:
                        if "UNIQUE constraint failed" not in str(e):
                            print(f"❌ Failed to add price for {ticker} on {price_row['date']}: {e}")
            
            print(f"✅ Added {prices_added} historical price records")
            
        except Exception as e:
            print(f"⚠️  Could not load historical data: {e}")
        
        # Step 5: Calculate daily portfolio values for recent dates
        print("📊 Calculating daily portfolio values...")
        recent_dates = [
            date(2025, 9, 23),  # Portfolio start
            date(2025, 9, 24),
            date(2025, 9, 25),
            date(2025, 9, 26),
            date(2025, 9, 27),
            date(2025, 9, 30),  # Latest
        ]
        
        for target_date in recent_dates:
            try:
                updated = portfolio_service.update_daily_portfolio_values(user.user_id, target_date)
                portfolio_service.update_portfolio_summary(user.user_id, target_date)
                print(f"  📅 Updated {updated} positions for {target_date}")
            except Exception as e:
                print(f"❌ Failed to update values for {target_date}: {e}")
        
        # Step 6: Verify migration
        print("🔍 Verifying migration...")
        current_portfolio = portfolio_service.calculate_current_portfolio_value(user.user_id)
        
        print(f"✅ Migration Summary:")
        print(f"  👤 User: {current_portfolio['summary']['User']}")
        print(f"  💼 Holdings: {current_portfolio['summary']['Total_Holdings']}")
        print(f"  💰 Total Value: ${current_portfolio['summary']['Total_Value']:,.2f}")
        print(f"  📈 Total Gain/Loss: ${current_portfolio['summary']['Total_Gain_Loss']:,.2f}")
        print(f"  📊 Return %: {current_portfolio['summary']['Total_Gain_Loss_Percent']:.2f}%")
        
        # Check if total matches expected
        expected_total = 325850.92
        actual_total = current_portfolio['summary']['Total_Value']
        match = abs(actual_total - expected_total) < 100  # Allow small rounding differences
        
        print(f"🎯 Expected Total: ${expected_total:,.2f}")
        print(f"✅ Perfect Match: {match}")
        
        if match:
            print("🎉 Migration completed successfully!")
            return True
        else:
            print(f"⚠️  Total mismatch: ${actual_total - expected_total:,.2f}")
            return False
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

def create_api_v2():
    """Create API endpoints for the new structure"""
    
    api_code = '''"""
Perfect Portfolio API V2 - Normalized Database
Clean, efficient calculations with proper table structure
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from datetime import date, datetime

# Core imports
from core.database import get_db
from services.portfolio_service_v2 import PortfolioServiceV2

# Create FastAPI app
app = FastAPI(
    title="Perfect Portfolio API V2",
    description="Normalized database with efficient calculations",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection
def get_portfolio_service(db: Session = Depends(get_db)) -> PortfolioServiceV2:
    return PortfolioServiceV2(db)

@app.get("/")
def root():
    return {
        "name": "Perfect Portfolio API V2",
        "version": "2.0.0",
        "status": "running",
        "database": "normalized"
    }

@app.get("/api/v2/portfolio")
def get_portfolio(
    user_id: int = 1,
    service: PortfolioServiceV2 = Depends(get_portfolio_service)
):
    """Get current portfolio with normalized calculations"""
    try:
        result = service.calculate_current_portfolio_value(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/portfolio/{user_id}/performance")
def get_portfolio_performance(
    user_id: int,
    start_date: str = "2025-09-23",
    end_date: str = "2025-09-30",
    service: PortfolioServiceV2 = Depends(get_portfolio_service)
):
    """Get portfolio performance over time"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        performance = service.calculate_portfolio_performance(user_id, start, end)
        return {"performance": performance, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v2/portfolio/{user_id}/update-daily-values")
def update_daily_values(
    user_id: int,
    target_date: str = None,
    service: PortfolioServiceV2 = Depends(get_portfolio_service)
):
    """Update daily portfolio values"""
    try:
        if target_date:
            date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
        else:
            date_obj = date.today()
        
        updated_count = service.update_daily_portfolio_values(user_id, date_obj)
        summary = service.update_portfolio_summary(user_id, date_obj)
        
        return {
            "updated_positions": updated_count,
            "total_value": summary.total_value,
            "date": date_obj.isoformat(),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Legacy compatibility
@app.get("/portfolio")
def get_portfolio_legacy(
    user_id: int = 1,
    service: PortfolioServiceV2 = Depends(get_portfolio_service)
):
    """Legacy endpoint for backward compatibility"""
    return get_portfolio(user_id, service)

if __name__ == "__main__":
    print("🚀 Starting Perfect Portfolio API V2 - Normalized Database")
    uvicorn.run(app, host="127.0.0.1", port=8002, reload=True)
'''
    
    with open("api_v2_normalized.py", "w") as f:
        f.write(api_code)
    
    print("✅ Created api_v2_normalized.py")

if __name__ == "__main__":
    print("🚀 Portfolio Database Migration Tool")
    print("📊 Converting to normalized table structure...")
    
    success = migrate_portfolio_data()
    
    if success:
        create_api_v2()
        print("🎉 Migration completed! New API available at api_v2_normalized.py")
        print("💡 Run: python api_v2_normalized.py")
    else:
        print("❌ Migration failed. Please check the logs.")
