"""
Perfect Portfolio Service V2 - Normalized Database
Efficient calculations with proper table structure
"""

from typing import Dict, List, Optional, Tuple
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from domain.models_v2 import (
    User, Portfolio, DailyPrice, PortfolioDailyValue, 
    PortfolioSummary, AssetCategory, PortfolioTransaction
)
from core.logging import logger

class PortfolioServiceV2:
    """Perfect portfolio service with normalized database"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # User operations
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.user_id == user_id).first()
    
    def create_user(self, name: str, email: str) -> User:
        """Create new user"""
        user = User(name=name, email=email)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        logger.info(f"Created user: {user.name}")
        return user
    
    # Portfolio operations
    def get_user_portfolio(self, user_id: int) -> List[Portfolio]:
        """Get all portfolio positions for user"""
        return (
            self.db.query(Portfolio)
            .filter(Portfolio.user_id == user_id)
            .order_by(desc(Portfolio.units * Portfolio.avg_price))  # Order by cost basis
            .all()
        )
    
    def add_portfolio_position(
        self, 
        user_id: int, 
        ticker: str, 
        units: float, 
        avg_price: float, 
        buy_date: date
    ) -> Portfolio:
        """Add new portfolio position"""
        position = Portfolio(
            user_id=user_id,
            ticker=ticker,
            units=units,
            avg_price=avg_price,
            buy_date=buy_date
        )
        self.db.add(position)
        self.db.commit()
        self.db.refresh(position)
        logger.info(f"Added position: {ticker} ({units} units @ ${avg_price:.2f})")
        return position
    
    # Price operations
    def get_latest_price(self, ticker: str) -> Optional[float]:
        """Get latest price for ticker"""
        latest_price = (
            self.db.query(DailyPrice)
            .filter(DailyPrice.ticker == ticker)
            .order_by(desc(DailyPrice.price_date))
            .first()
        )
        return latest_price.close_price if latest_price else None
    
    def get_price_on_date(self, ticker: str, target_date: date) -> Optional[float]:
        """Get price for ticker on specific date"""
        price_record = (
            self.db.query(DailyPrice)
            .filter(
                and_(
                    DailyPrice.ticker == ticker,
                    DailyPrice.price_date == target_date
                )
            )
            .first()
        )
        return price_record.close_price if price_record else None
    
    def add_daily_price(
        self, 
        ticker: str, 
        price_date: date, 
        close_price: float,
        open_price: Optional[float] = None,
        high_price: Optional[float] = None,
        low_price: Optional[float] = None,
        volume: Optional[int] = None
    ) -> DailyPrice:
        """Add daily price data"""
        # Check if price already exists
        existing = (
            self.db.query(DailyPrice)
            .filter(
                and_(
                    DailyPrice.ticker == ticker,
                    DailyPrice.price_date == price_date
                )
            )
            .first()
        )
        
        if existing:
            # Update existing price
            existing.close_price = close_price
            existing.open_price = open_price
            existing.high_price = high_price
            existing.low_price = low_price
            existing.volume = volume
            price_record = existing
        else:
            # Create new price record
            price_record = DailyPrice(
                ticker=ticker,
                price_date=price_date,
                close_price=close_price,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                volume=volume
            )
            self.db.add(price_record)
        
        self.db.commit()
        self.db.refresh(price_record)
        return price_record
    
    # Portfolio calculations
    def calculate_current_portfolio_value(self, user_id: int) -> Dict:
        """Calculate current portfolio value with latest prices"""
        positions = self.get_user_portfolio(user_id)
        user = self.get_user(user_id)
        
        if not positions:
            return self._empty_portfolio_response(user.name if user else "Unknown")
        
        portfolio_data = []
        total_value = 0.0
        total_cost_basis = 0.0
        total_gain_loss = 0.0
        
        for position in positions:
            # Get latest price
            current_price = self.get_latest_price(position.ticker)
            if current_price is None:
                logger.warning(f"No price data for {position.ticker}")
                current_price = position.avg_price  # Fallback to avg price
            
            # Calculate metrics
            current_value = position.current_value(current_price)
            cost_basis = position.cost_basis
            gain_loss = position.gain_loss(current_price)
            gain_loss_percent = position.gain_loss_percent(current_price)
            
            # Get category
            category = self.get_asset_category(position.ticker)
            
            portfolio_item = {
                "Ticker": position.ticker,
                "Units": position.units,
                "Avg_Price": position.avg_price,
                "Current_Price": current_price,
                "Total_Value": current_value,
                "Cost_Basis": cost_basis,
                "Gain_Loss": gain_loss,
                "Gain_Loss_Percent": gain_loss_percent,
                "Category": category,
                "Buy_Date": position.buy_date.isoformat()
            }
            
            portfolio_data.append(portfolio_item)
            
            # Accumulate totals
            total_value += current_value
            total_cost_basis += cost_basis
            total_gain_loss += gain_loss
        
        # Calculate summary
        total_gain_loss_percent = (
            (total_gain_loss / total_cost_basis * 100) 
            if total_cost_basis > 0 else 0.0
        )
        
        summary = {
            "Total_Value": total_value,
            "Total_Cost_Basis": total_cost_basis,
            "Total_Gain_Loss": total_gain_loss,
            "Total_Gain_Loss_Percent": total_gain_loss_percent,
            "Total_Holdings": len(portfolio_data),
            "User": user.name if user else "Unknown"
        }
        
        return {
            "portfolio": portfolio_data,
            "summary": summary,
            "status": "success"
        }
    
    def calculate_portfolio_performance(
        self, 
        user_id: int, 
        start_date: date, 
        end_date: date
    ) -> List[Dict]:
        """Calculate portfolio performance over time"""
        # Get all portfolio daily values in date range
        daily_values = (
            self.db.query(PortfolioDailyValue)
            .join(Portfolio)
            .filter(
                and_(
                    Portfolio.user_id == user_id,
                    PortfolioDailyValue.date >= start_date,
                    PortfolioDailyValue.date <= end_date
                )
            )
            .order_by(PortfolioDailyValue.date)
            .all()
        )
        
        # Group by date and sum values
        performance_data = {}
        for daily_value in daily_values:
            date_key = daily_value.date
            if date_key not in performance_data:
                performance_data[date_key] = 0.0
            performance_data[date_key] += daily_value.position_val
        
        # Convert to list format
        performance_list = [
            {
                "date": date_key.isoformat(),
                "total_value": total_value
            }
            for date_key, total_value in sorted(performance_data.items())
        ]
        
        return performance_list
    
    def update_daily_portfolio_values(self, user_id: int, target_date: date) -> int:
        """Update daily portfolio values for all positions"""
        positions = self.get_user_portfolio(user_id)
        updated_count = 0
        
        for position in positions:
            # Get price for target date
            price = self.get_price_on_date(position.ticker, target_date)
            if price is None:
                logger.warning(f"No price data for {position.ticker} on {target_date}")
                continue
            
            # Check if daily value already exists
            existing = (
                self.db.query(PortfolioDailyValue)
                .filter(
                    and_(
                        PortfolioDailyValue.portfolio_id == position.portfolio_id,
                        PortfolioDailyValue.date == target_date
                    )
                )
                .first()
            )
            
            position_val = position.units * price
            
            if existing:
                # Update existing record
                existing.units = position.units
                existing.price = price
                existing.position_val = position_val
            else:
                # Create new record
                daily_value = PortfolioDailyValue(
                    portfolio_id=position.portfolio_id,
                    date=target_date,
                    units=position.units,
                    price=price,
                    position_val=position_val
                )
                self.db.add(daily_value)
            
            updated_count += 1
        
        self.db.commit()
        logger.info(f"Updated {updated_count} daily portfolio values for {target_date}")
        return updated_count
    
    def update_portfolio_summary(self, user_id: int, target_date: date) -> PortfolioSummary:
        """Update portfolio summary for specific date"""
        # Calculate total value from daily values
        total_value = (
            self.db.query(func.sum(PortfolioDailyValue.position_val))
            .join(Portfolio)
            .filter(
                and_(
                    Portfolio.user_id == user_id,
                    PortfolioDailyValue.date == target_date
                )
            )
            .scalar()
        ) or 0.0
        
        # Calculate additional metrics
        positions = self.get_user_portfolio(user_id)
        total_cost_basis = sum(pos.cost_basis for pos in positions)
        total_gain_loss = total_value - total_cost_basis
        total_gain_loss_percent = (
            (total_gain_loss / total_cost_basis * 100) 
            if total_cost_basis > 0 else 0.0
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
            existing_summary.num_positions = len(positions)
            summary = existing_summary
        else:
            # Create new summary
            summary = PortfolioSummary(
                user_id=user_id,
                date=target_date,
                total_value=total_value,
                total_cost_basis=total_cost_basis,
                total_gain_loss=total_gain_loss,
                total_gain_loss_percent=total_gain_loss_percent,
                num_positions=len(positions)
            )
            self.db.add(summary)
        
        self.db.commit()
        self.db.refresh(summary)
        logger.info(f"Updated portfolio summary for {target_date}: ${total_value:,.2f}")
        return summary
    
    # Utility methods
    def get_asset_category(self, ticker: str) -> str:
        """Get asset category for ticker"""
        category_record = (
            self.db.query(AssetCategory)
            .filter(AssetCategory.ticker == ticker)
            .first()
        )
        return category_record.category if category_record else "Other"
    
    def _empty_portfolio_response(self, user_name: str = "Unknown") -> Dict:
        """Create empty portfolio response"""
        return {
            "portfolio": [],
            "summary": {
                "Total_Value": 0.0,
                "Total_Cost_Basis": 0.0,
                "Total_Gain_Loss": 0.0,
                "Total_Gain_Loss_Percent": 0.0,
                "Total_Holdings": 0,
                "User": user_name
            },
            "status": "success"
        }
    
    # Bulk operations for data migration
    def migrate_from_old_structure(self, old_portfolio_data: List[Dict]) -> int:
        """Migrate data from old portfolio_values structure"""
        migrated_count = 0
        
        for item in old_portfolio_data:
            try:
                # Calculate units from total_value and current_price
                units = item['total_value'] / item['current_price'] if item['current_price'] > 0 else 0
                avg_price = item['cost_basis'] / units if units > 0 else item['current_price']
                
                # Create portfolio position
                position = Portfolio(
                    user_id=item.get('user_id', 1),
                    ticker=item['ticker'],
                    units=units,
                    avg_price=avg_price,
                    buy_date=date.today()  # Default to today, can be updated later
                )
                
                self.db.add(position)
                migrated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to migrate {item.get('ticker', 'unknown')}: {e}")
        
        self.db.commit()
        logger.info(f"Migrated {migrated_count} portfolio positions")
        return migrated_count
