"""
Portfolio Daily Value Calculator - Scheduled Job
Calculates daily portfolio values and summaries
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional
import logging

from core.database import SessionLocal
from domain.models_v2 import (
    Portfolio, DailyPrice, PortfolioDailyValue, 
    PortfolioSummary, User
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioCalculator:
    """Portfolio daily value calculator"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_daily_portfolio_values(self, target_date: date) -> Dict[str, int]:
        """
        Main function: Calculate portfolio values for all users on a specific date
        
        Process:
        1. Read all portfolio positions
        2. Join with daily_prices table on ticker and date
        3. Calculate units * close_price as position_val
        4. Insert into portfolio_daily_value
        5. Aggregate by user_id to store in portfolio_summary
        """
        
        logger.info(f"🔄 Calculating portfolio values for {target_date}")
        
        try:
            # Step 1 & 2: Get all portfolio positions with prices for target date
            positions_with_prices = (
                self.db.query(Portfolio, DailyPrice)
                .join(
                    DailyPrice,
                    and_(
                        Portfolio.ticker == DailyPrice.ticker,
                        DailyPrice.price_date == target_date
                    )
                )
                .all()
            )
            
            if not positions_with_prices:
                logger.warning(f"No price data found for {target_date}")
                return {"processed_positions": 0, "updated_users": 0}
            
            logger.info(f"Found {len(positions_with_prices)} positions with price data")
            
            # Step 3 & 4: Calculate and insert daily values
            processed_positions = 0
            user_totals = {}  # Track totals by user for summary
            
            for portfolio, daily_price in positions_with_prices:
                # Calculate position value
                position_val = portfolio.units * daily_price.close_price
                
                # Check if daily value already exists
                existing_daily_value = (
                    self.db.query(PortfolioDailyValue)
                    .filter(
                        and_(
                            PortfolioDailyValue.portfolio_id == portfolio.portfolio_id,
                            PortfolioDailyValue.date == target_date
                        )
                    )
                    .first()
                )
                
                if existing_daily_value:
                    # Update existing record
                    existing_daily_value.units = portfolio.units
                    existing_daily_value.price = daily_price.close_price
                    existing_daily_value.position_val = position_val
                else:
                    # Create new record
                    daily_value = PortfolioDailyValue(
                        portfolio_id=portfolio.portfolio_id,
                        date=target_date,
                        units=portfolio.units,
                        price=daily_price.close_price,
                        position_val=position_val
                    )
                    self.db.add(daily_value)
                
                # Track user totals for summary
                user_id = portfolio.user_id
                if user_id not in user_totals:
                    user_totals[user_id] = {
                        'total_value': 0,
                        'total_cost_basis': 0,
                        'positions_count': 0
                    }
                
                user_totals[user_id]['total_value'] += position_val
                user_totals[user_id]['total_cost_basis'] += (portfolio.units * portfolio.avg_price)
                user_totals[user_id]['positions_count'] += 1
                
                processed_positions += 1
            
            # Commit daily values
            self.db.commit()
            logger.info(f"✅ Inserted/updated {processed_positions} daily portfolio values")
            
            # Step 5: Aggregate and store portfolio summaries
            updated_users = self._update_portfolio_summaries(target_date, user_totals)
            
            return {
                "processed_positions": processed_positions,
                "updated_users": updated_users,
                "target_date": target_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate portfolio values: {e}")
            self.db.rollback()
            raise
    
    def _update_portfolio_summaries(self, target_date: date, user_totals: Dict) -> int:
        """Update portfolio summaries for all users"""
        
        updated_users = 0
        
        for user_id, totals in user_totals.items():
            try:
                # Calculate summary metrics
                total_value = totals['total_value']
                total_cost_basis = totals['total_cost_basis']
                total_gain_loss = total_value - total_cost_basis
                total_gain_loss_percent = (
                    (total_gain_loss / total_cost_basis * 100) 
                    if total_cost_basis > 0 else 0
                )
                
                # Check if summary already exists
                existing_summary = (
                    self.db.query(PortfolioSummary)
                    .filter(
                        and_(
                            PortfolioSummary.user_id == user_id,
                            PortfolioSummary.date == target_date
                        )
                    )
                    .first()
                )
                
                if existing_summary:
                    # Update existing summary
                    existing_summary.total_value = total_value
                    existing_summary.total_cost_basis = total_cost_basis
                    existing_summary.total_gain_loss = total_gain_loss
                    existing_summary.total_gain_loss_percent = total_gain_loss_percent
                    existing_summary.num_positions = totals['positions_count']
                    existing_summary.updated_at = datetime.now()
                else:
                    # Create new summary
                    summary = PortfolioSummary(
                        user_id=user_id,
                        date=target_date,
                        total_value=total_value,
                        total_cost_basis=total_cost_basis,
                        total_gain_loss=total_gain_loss,
                        total_gain_loss_percent=total_gain_loss_percent,
                        num_positions=totals['positions_count']
                    )
                    self.db.add(summary)
                
                updated_users += 1
                logger.info(f"📊 Updated summary for user {user_id}: ${total_value:,.2f}")
                
            except Exception as e:
                logger.error(f"❌ Failed to update summary for user {user_id}: {e}")
        
        # Commit summaries
        self.db.commit()
        logger.info(f"✅ Updated summaries for {updated_users} users")
        
        return updated_users
    
    def calculate_date_range(self, start_date: date, end_date: date) -> Dict[str, any]:
        """Calculate portfolio values for a date range"""
        
        logger.info(f"🔄 Calculating portfolio values from {start_date} to {end_date}")
        
        results = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily_results": [],
            "total_positions": 0,
            "total_users": 0
        }
        
        current_date = start_date
        while current_date <= end_date:
            try:
                daily_result = self.calculate_daily_portfolio_values(current_date)
                daily_result["date"] = current_date.isoformat()
                results["daily_results"].append(daily_result)
                results["total_positions"] += daily_result["processed_positions"]
                results["total_users"] = max(results["total_users"], daily_result["updated_users"])
                
            except Exception as e:
                logger.error(f"❌ Failed for {current_date}: {e}")
                results["daily_results"].append({
                    "date": current_date.isoformat(),
                    "error": str(e),
                    "processed_positions": 0,
                    "updated_users": 0
                })
            
            current_date += timedelta(days=1)
        
        logger.info(f"✅ Completed date range calculation: {len(results['daily_results'])} days")
        return results
    
    def get_missing_calculation_dates(self, start_date: date, end_date: date) -> List[date]:
        """Find dates that need portfolio calculations"""
        
        # Get dates that already have portfolio summaries
        existing_dates = (
            self.db.query(PortfolioSummary.date)
            .filter(
                and_(
                    PortfolioSummary.date >= start_date,
                    PortfolioSummary.date <= end_date
                )
            )
            .distinct()
            .all()
        )
        
        existing_date_set = {d[0] for d in existing_dates}
        
        # Generate all dates in range
        missing_dates = []
        current_date = start_date
        while current_date <= end_date:
            if current_date not in existing_date_set:
                # Check if we have price data for this date
                price_count = (
                    self.db.query(func.count(DailyPrice.price_id))
                    .filter(DailyPrice.price_date == current_date)
                    .scalar()
                )
                
                if price_count > 0:
                    missing_dates.append(current_date)
            
            current_date += timedelta(days=1)
        
        return missing_dates

# Standalone functions for scheduled jobs
def calculate_portfolio_values_job(target_date: Optional[date] = None) -> Dict[str, any]:
    """
    Scheduled job function to calculate portfolio values
    Can be called by cron, celery, or other schedulers
    """
    
    if target_date is None:
        target_date = date.today()
    
    db = SessionLocal()
    try:
        calculator = PortfolioCalculator(db)
        result = calculator.calculate_daily_portfolio_values(target_date)
        
        logger.info(f"🎉 Portfolio calculation job completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Portfolio calculation job failed: {e}")
        raise
    finally:
        db.close()

def backfill_portfolio_values(start_date: date, end_date: date) -> Dict[str, any]:
    """
    Backfill portfolio values for a date range
    Useful for historical data processing
    """
    
    db = SessionLocal()
    try:
        calculator = PortfolioCalculator(db)
        
        # Find missing dates
        missing_dates = calculator.get_missing_calculation_dates(start_date, end_date)
        
        if not missing_dates:
            logger.info("✅ No missing dates found - all calculations up to date")
            return {"message": "No missing calculations", "missing_dates": 0}
        
        logger.info(f"🔄 Backfilling {len(missing_dates)} missing dates")
        
        # Process missing dates
        results = []
        for missing_date in missing_dates:
            try:
                result = calculator.calculate_daily_portfolio_values(missing_date)
                results.append(result)
                logger.info(f"✅ Backfilled {missing_date}")
            except Exception as e:
                logger.error(f"❌ Failed to backfill {missing_date}: {e}")
        
        return {
            "backfilled_dates": len(results),
            "total_missing": len(missing_dates),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Backfill job failed: {e}")
        raise
    finally:
        db.close()

# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Portfolio Calculator")
    parser.add_argument("--date", type=str, help="Target date (YYYY-MM-DD)")
    parser.add_argument("--start-date", type=str, help="Start date for range (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="End date for range (YYYY-MM-DD)")
    parser.add_argument("--backfill", action="store_true", help="Backfill missing dates")
    
    args = parser.parse_args()
    
    if args.backfill and args.start_date and args.end_date:
        start = datetime.strptime(args.start_date, "%Y-%m-%d").date()
        end = datetime.strptime(args.end_date, "%Y-%m-%d").date()
        result = backfill_portfolio_values(start, end)
        print(f"Backfill result: {result}")
    
    elif args.date:
        target = datetime.strptime(args.date, "%Y-%m-%d").date()
        result = calculate_portfolio_values_job(target)
        print(f"Calculation result: {result}")
    
    else:
        # Default: calculate for today
        result = calculate_portfolio_values_job()
        print(f"Today's calculation result: {result}")
