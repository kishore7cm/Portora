"""
Enhanced Daily Portfolio Calculator
Handles different asset types: stocks, bond ETFs, crypto, bonds-as-cash, and cash
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
    PortfolioSummary, User, CashTransaction
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedDailyCalculator:
    """Enhanced portfolio calculator with asset type handling"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_cash_balance(self, user_id: int, target_date: date) -> float:
        """Calculate cumulative cash balance up to target date"""
        
        transactions = (
            self.db.query(CashTransaction)
            .filter(
                and_(
                    CashTransaction.user_id == user_id,
                    CashTransaction.transaction_date <= target_date
                )
            )
            .order_by(CashTransaction.transaction_date)
            .all()
        )
        
        cash_balance = 0.0
        
        for transaction in transactions:
            if transaction.type == 'deposit':
                cash_balance += transaction.amount
            elif transaction.type == 'withdrawal':
                cash_balance -= transaction.amount
        
        logger.debug(f"Cash balance for user {user_id} on {target_date}: ${cash_balance:,.2f}")
        return cash_balance
    
    def get_latest_cash_balance_before_date(self, user_id: int, target_date: date) -> float:
        """Get the latest cash balance before target date (for carrying forward)"""
        
        # Get the most recent portfolio summary before target date
        latest_summary = (
            self.db.query(PortfolioSummary)
            .filter(
                and_(
                    PortfolioSummary.user_id == user_id,
                    PortfolioSummary.date < target_date
                )
            )
            .order_by(PortfolioSummary.date.desc())
            .first()
        )
        
        if latest_summary and hasattr(latest_summary, 'cash_balance') and latest_summary.cash_balance is not None:
            return latest_summary.cash_balance
        
        # Fallback to calculating from transactions
        return self.get_cash_balance(user_id, target_date - timedelta(days=1))
    
    def categorize_portfolio_positions(self, user_id: int) -> Dict[str, List]:
        """Categorize portfolio positions by asset type"""
        
        positions = (
            self.db.query(Portfolio)
            .filter(Portfolio.user_id == user_id)
            .all()
        )
        
        # Common bond ETFs
        known_bond_etfs = {
            'BND', 'AGG', 'TLT', 'IEF', 'SHY', 'VGIT', 'VGLT', 'VTEB', 
            'MUB', 'HYG', 'JNK', 'LQD', 'VCIT', 'VCLT', 'BSV', 'BIV', 'BLV'
        }
        
        # Common crypto symbols
        crypto_symbols = {
            'BTC-USD', 'ETH-USD', 'BTC', 'ETH', 'ADA-USD', 'SOL-USD', 
            'DOT-USD', 'AVAX-USD', 'MATIC-USD', 'LINK-USD'
        }
        
        categorized = {
            'stocks': [],
            'bond_etfs': [],
            'crypto': [],
            'bond_cash': [],
            'cash': []
        }
        
        for position in positions:
            ticker = position.ticker
            
            if ticker.startswith('CASH') or ticker.startswith('Cash'):
                categorized['cash'].append(position)
            elif ticker.startswith('BOND_CASH'):
                categorized['bond_cash'].append(position)
            elif ticker in crypto_symbols or 'USD' in ticker:
                categorized['crypto'].append(position)
            elif ticker in known_bond_etfs:
                categorized['bond_etfs'].append(position)
            else:
                # Default to stock
                categorized['stocks'].append(position)
        
        logger.info(f"Portfolio categorization for user {user_id}:")
        logger.info(f"  📈 Stocks: {len(categorized['stocks'])}")
        logger.info(f"  🏦 Bond ETFs: {len(categorized['bond_etfs'])}")
        logger.info(f"  ₿ Crypto: {len(categorized['crypto'])}")
        logger.info(f"  💰 Bond Cash: {len(categorized['bond_cash'])}")
        logger.info(f"  💵 Cash: {len(categorized['cash'])}")
        
        return categorized
    
    def calculate_daily_portfolio_values(self, target_date: date) -> Dict[str, any]:
        """
        Enhanced daily portfolio calculation with asset type handling
        
        Process:
        1. Stocks, bond ETFs, crypto: Join with daily_prices and calculate units * close_price
        2. Bond cash: Carry forward value from portfolio table (no price lookup)
        3. Cash: Calculate from cash_transactions or carry forward latest balance
        4. Aggregate all values for portfolio_summary
        """
        
        logger.info(f"🔄 Enhanced portfolio calculation for {target_date}")
        
        try:
            # Get all users with portfolios
            users_with_portfolios = (
                self.db.query(User.user_id)
                .join(Portfolio, User.user_id == Portfolio.user_id)
                .distinct()
                .all()
            )
            
            total_processed_positions = 0
            updated_users = 0
            
            for (user_id,) in users_with_portfolios:
                try:
                    # Categorize this user's positions
                    categorized_positions = self.categorize_portfolio_positions(user_id)
                    
                    user_total_value = 0.0
                    user_cost_basis = 0.0
                    user_positions_count = 0
                    
                    # Process stocks, bond ETFs, and crypto (need price lookups)
                    market_positions = (
                        categorized_positions['stocks'] + 
                        categorized_positions['bond_etfs'] + 
                        categorized_positions['crypto']
                    )
                    
                    for position in market_positions:
                        # Get price for this date
                        daily_price = (
                            self.db.query(DailyPrice)
                            .filter(
                                and_(
                                    DailyPrice.ticker == position.ticker,
                                    DailyPrice.price_date == target_date
                                )
                            )
                            .first()
                        )
                        
                        if daily_price:
                            # Calculate position value
                            position_val = position.units * daily_price.close_price
                            
                            # Insert/update portfolio daily value
                            self._upsert_portfolio_daily_value(
                                position.portfolio_id, target_date, 
                                position.units, daily_price.close_price, position_val
                            )
                            
                            user_total_value += position_val
                            user_cost_basis += (position.units * position.avg_price)
                            user_positions_count += 1
                            total_processed_positions += 1
                            
                            logger.debug(f"  📊 {position.ticker}: {position.units} × ${daily_price.close_price} = ${position_val:,.2f}")
                        else:
                            logger.warning(f"No price data for {position.ticker} on {target_date}")
                    
                    # Process bond cash positions (carry forward from portfolio)
                    for position in categorized_positions['bond_cash']:
                        # For bond cash, use the avg_price as the constant value
                        position_val = position.units * position.avg_price
                        
                        # Insert/update portfolio daily value
                        self._upsert_portfolio_daily_value(
                            position.portfolio_id, target_date,
                            position.units, position.avg_price, position_val
                        )
                        
                        user_total_value += position_val
                        user_cost_basis += position_val  # Cost basis equals current value for bonds
                        user_positions_count += 1
                        total_processed_positions += 1
                        
                        logger.debug(f"  💰 {position.ticker} (bond cash): ${position_val:,.2f}")
                    
                    # Process cash positions (carry forward from portfolio)
                    for position in categorized_positions['cash']:
                        # For cash positions, use the avg_price as the constant value
                        position_val = position.units * position.avg_price
                        
                        # Insert/update portfolio daily value
                        self._upsert_portfolio_daily_value(
                            position.portfolio_id, target_date,
                            position.units, position.avg_price, position_val
                        )
                        
                        user_total_value += position_val
                        user_cost_basis += position_val  # Cost basis equals current value for cash
                        user_positions_count += 1
                        total_processed_positions += 1
                        
                        logger.debug(f"  💵 {position.ticker} (cash): ${position_val:,.2f}")
                    
                    # Calculate actual cash balance from transactions
                    cash_balance = self.get_cash_balance(user_id, target_date)
                    
                    # If no new transactions today, carry forward previous balance
                    if cash_balance == 0:
                        cash_balance = self.get_latest_cash_balance_before_date(user_id, target_date)
                    
                    # Add cash balance to total value
                    final_total_value = user_total_value + cash_balance
                    
                    # Update portfolio summary
                    self._upsert_portfolio_summary(
                        user_id, target_date, final_total_value, user_cost_basis,
                        user_positions_count, cash_balance
                    )
                    
                    updated_users += 1
                    logger.info(f"📊 User {user_id}: Portfolio ${user_total_value:,.2f} + Cash ${cash_balance:,.2f} = Total ${final_total_value:,.2f}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process user {user_id}: {e}")
            
            # Commit all changes
            self.db.commit()
            
            return {
                "processed_positions": total_processed_positions,
                "updated_users": updated_users,
                "target_date": target_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed enhanced portfolio calculation: {e}")
            self.db.rollback()
            raise
    
    def _upsert_portfolio_daily_value(self, portfolio_id: int, target_date: date, 
                                     units: float, price: float, position_val: float):
        """Insert or update portfolio daily value"""
        
        existing = (
            self.db.query(PortfolioDailyValue)
            .filter(
                and_(
                    PortfolioDailyValue.portfolio_id == portfolio_id,
                    PortfolioDailyValue.date == target_date
                )
            )
            .first()
        )
        
        if existing:
            # Update existing record
            existing.units = units
            existing.price = price
            existing.position_val = position_val
        else:
            # Create new record
            daily_value = PortfolioDailyValue(
                portfolio_id=portfolio_id,
                date=target_date,
                units=units,
                price=price,
                position_val=position_val
            )
            self.db.add(daily_value)
    
    def _upsert_portfolio_summary(self, user_id: int, target_date: date, total_value: float,
                                 total_cost_basis: float, num_positions: int, cash_balance: float):
        """Insert or update portfolio summary"""
        
        total_gain_loss = total_value - total_cost_basis
        total_gain_loss_percent = (
            (total_gain_loss / total_cost_basis * 100) 
            if total_cost_basis > 0 else 0
        )
        
        existing = (
            self.db.query(PortfolioSummary)
            .filter(
                and_(
                    PortfolioSummary.user_id == user_id,
                    PortfolioSummary.date == target_date
                )
            )
            .first()
        )
        
        if existing:
            # Update existing summary
            existing.total_value = total_value
            existing.total_cost_basis = total_cost_basis
            existing.total_gain_loss = total_gain_loss
            existing.total_gain_loss_percent = total_gain_loss_percent
            existing.num_positions = num_positions
            existing.cash_balance = cash_balance
            existing.updated_at = datetime.now()
        else:
            # Create new summary
            summary = PortfolioSummary(
                user_id=user_id,
                date=target_date,
                total_value=total_value,
                total_cost_basis=total_cost_basis,
                total_gain_loss=total_gain_loss,
                total_gain_loss_percent=total_gain_loss_percent,
                num_positions=num_positions,
                cash_balance=cash_balance
            )
            self.db.add(summary)
    
    def calculate_date_range(self, start_date: date, end_date: date) -> Dict[str, any]:
        """Calculate portfolio values for a date range"""
        
        logger.info(f"🔄 Enhanced calculation from {start_date} to {end_date}")
        
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
        
        logger.info(f"✅ Completed enhanced date range calculation: {len(results['daily_results'])} days")
        return results

# Standalone functions for scheduled jobs
def calculate_enhanced_daily_portfolio_job(target_date: Optional[date] = None) -> Dict[str, any]:
    """
    Enhanced daily scheduled job function
    Handles all asset types with proper categorization
    """
    
    if target_date is None:
        target_date = date.today()
    
    db = SessionLocal()
    try:
        calculator = EnhancedDailyCalculator(db)
        result = calculator.calculate_daily_portfolio_values(target_date)
        
        logger.info(f"🎉 Enhanced daily portfolio calculation completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Enhanced daily portfolio calculation failed: {e}")
        raise
    finally:
        db.close()

def backfill_enhanced_portfolio_values(start_date: date, end_date: date) -> Dict[str, any]:
    """
    Backfill portfolio values with enhanced asset type handling
    """
    
    db = SessionLocal()
    try:
        calculator = EnhancedDailyCalculator(db)
        result = calculator.calculate_date_range(start_date, end_date)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Enhanced backfill failed: {e}")
        raise
    finally:
        db.close()

def add_bond_cash_position(user_id: int, bond_name: str, value: float, 
                          buy_date: Optional[date] = None) -> bool:
    """
    Add a bond treated as cash position
    
    Args:
        user_id: User ID
        bond_name: Name/identifier for the bond
        value: Current value of the bond
        buy_date: Purchase date (defaults to today)
        
    Returns:
        True if successful, False otherwise
    """
    
    if buy_date is None:
        buy_date = date.today()
    
    db = SessionLocal()
    try:
        # Verify user exists
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return False
        
        # Create bond cash position with special ticker format
        ticker = f"BOND_CASH_{bond_name.upper().replace(' ', '_')}"
        
        # Create portfolio position (units=1, avg_price=value for simplicity)
        bond_position = Portfolio(
            user_id=user_id,
            ticker=ticker,
            units=1.0,  # Always 1 unit
            avg_price=value,  # Value stored as price
            buy_date=buy_date
        )
        
        db.add(bond_position)
        db.commit()
        
        logger.info(f"✅ Added bond cash position for user {user_id}: {ticker} = ${value:,.2f}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to add bond cash position: {e}")
        return False
    finally:
        db.close()

# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Daily Portfolio Calculator")
    parser.add_argument("--date", type=str, help="Target date (YYYY-MM-DD)")
    parser.add_argument("--start-date", type=str, help="Start date for range (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="End date for range (YYYY-MM-DD)")
    parser.add_argument("--backfill", action="store_true", help="Backfill missing dates")
    parser.add_argument("--add-bond", nargs=3, metavar=('USER_ID', 'BOND_NAME', 'VALUE'),
                       help="Add bond cash position: user_id bond_name value")
    
    args = parser.parse_args()
    
    if args.add_bond:
        user_id, bond_name, value = args.add_bond
        success = add_bond_cash_position(int(user_id), bond_name, float(value))
        print(f"Bond cash position {'added successfully' if success else 'failed'}")
    
    elif args.backfill and args.start_date and args.end_date:
        start = datetime.strptime(args.start_date, "%Y-%m-%d").date()
        end = datetime.strptime(args.end_date, "%Y-%m-%d").date()
        result = backfill_enhanced_portfolio_values(start, end)
        print(f"Enhanced backfill result: {result}")
    
    elif args.date:
        target = datetime.strptime(args.date, "%Y-%m-%d").date()
        result = calculate_enhanced_daily_portfolio_job(target)
        print(f"Enhanced calculation result: {result}")
    
    else:
        # Default: calculate for today
        result = calculate_enhanced_daily_portfolio_job()
        print(f"Today's enhanced calculation result: {result}")
