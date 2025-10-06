"""
Portfolio Service - Perfect Business Logic
Clean, focused, efficient
"""

from typing import Dict, List, Optional, Tuple
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

from services.data_service import DataService
from domain.schemas import (
    PortfolioResponse, HoldingResponse, PortfolioSummary,
    ReturnCalculationResponse, GLDMDebugResponse, UpdatePricesResponse
)
from core.logging import logger

class PortfolioService:
    """Perfect portfolio service - business logic layer"""
    
    def __init__(self, data_service: DataService):
        self.data_service = data_service
    
    def get_portfolio_summary(self, user_id: int) -> PortfolioResponse:
        """Get complete portfolio summary with perfect data"""
        logger.info(f"Getting portfolio summary for user {user_id}")
        
        # Get user and holdings
        user = self.data_service.get_user(user_id)
        if not user:
            logger.warning(f"User {user_id} not found")
            return self._empty_portfolio_response("User not found")
        
        holdings = self.data_service.get_portfolio_holdings(user_id)
        if not holdings:
            logger.info(f"No holdings found for user {user_id}")
            return self._empty_portfolio_response(user.name)
        
        # Convert to response format
        portfolio_items = []
        total_value = Decimal('0')
        total_cost_basis = Decimal('0')
        total_gain_loss = Decimal('0')
        
        for holding in holdings:
            # Create holding response
            holding_response = HoldingResponse(
                Ticker=holding.ticker,
                Current_Price=self._round_currency(holding.current_price),
                Total_Value=self._round_currency(holding.total_value),
                Cost_Basis=self._round_currency(holding.cost_basis),
                Gain_Loss=self._round_currency(holding.gain_loss),
                Gain_Loss_Percent=self._round_percentage(holding.gain_loss_percent),
                Category=holding.category
            )
            
            portfolio_items.append(holding_response)
            
            # Accumulate totals with precision
            total_value += Decimal(str(holding.total_value))
            total_cost_basis += Decimal(str(holding.cost_basis))
            total_gain_loss += Decimal(str(holding.gain_loss))
        
        # Calculate summary
        total_gain_loss_percent = (
            (total_gain_loss / total_cost_basis * 100) 
            if total_cost_basis > 0 else Decimal('0')
        )
        
        summary = PortfolioSummary(
            Total_Value=self._round_currency(float(total_value)),
            Total_Cost_Basis=self._round_currency(float(total_cost_basis)),
            Total_Gain_Loss=self._round_currency(float(total_gain_loss)),
            Total_Gain_Loss_Percent=self._round_percentage(float(total_gain_loss_percent)),
            Total_Holdings=len(portfolio_items),
            User=user.name
        )
        
        # Log key metrics
        logger.info(f"Portfolio summary: {len(holdings)} holdings, ${float(total_value):,.2f} total value")
        
        # Debug GLDM specifically
        gldm_items = [item for item in portfolio_items if item.Ticker == "GLDM"]
        if gldm_items:
            gldm = gldm_items[0]
            logger.info(f"🔍 GLDM: ${gldm.Current_Price:.2f}, {gldm.Gain_Loss_Percent:.2f}%")
        
        return PortfolioResponse(
            portfolio=portfolio_items,
            summary=summary,
            status="success"
        )
    
    def update_prices_from_csv(self, user_id: int, force_update: bool = False) -> UpdatePricesResponse:
        """Update all portfolio prices from CSV data"""
        logger.info(f"Updating prices for user {user_id} (force={force_update})")
        
        holdings = self.data_service.get_portfolio_holdings(user_id)
        if not holdings:
            return UpdatePricesResponse(
                updated_count=0,
                total_holdings=0,
                errors=["No holdings found"],
                status="error"
            )
        
        updated_count = 0
        errors = []
        
        for holding in holdings:
            try:
                # Get latest price from CSV
                latest_price = self.data_service.get_latest_price(holding.ticker)
                
                if latest_price is None:
                    errors.append(f"No price data for {holding.ticker}")
                    continue
                
                # Update if price changed or force update
                price_diff = abs(latest_price - holding.current_price)
                if force_update or price_diff > 0.01:  # Update if difference > 1 cent
                    success = self.data_service.update_holding_price(
                        user_id, holding.ticker, latest_price
                    )
                    
                    if success:
                        updated_count += 1
                        logger.debug(f"✅ Updated {holding.ticker}: ${holding.current_price:.2f} → ${latest_price:.2f}")
                    else:
                        errors.append(f"Failed to update {holding.ticker}")
                
            except Exception as e:
                error_msg = f"Error updating {holding.ticker}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        status = "success" if not errors else ("partial_success" if updated_count > 0 else "error")
        
        logger.info(f"Price update complete: {updated_count}/{len(holdings)} updated, {len(errors)} errors")
        
        return UpdatePricesResponse(
            updated_count=updated_count,
            total_holdings=len(holdings),
            errors=errors,
            status=status
        )
    
    def calculate_return(
        self, 
        user_id: int, 
        ticker: str, 
        start_date: date, 
        end_date: date
    ) -> Optional[ReturnCalculationResponse]:
        """Calculate return for specific ticker between dates"""
        logger.info(f"Calculating return for {ticker} from {start_date} to {end_date}")
        
        # Get prices from CSV
        start_price = self.data_service.get_price_on_date(ticker, start_date)
        end_price = self.data_service.get_price_on_date(ticker, end_date)
        
        if start_price is None or end_price is None:
            logger.warning(f"Missing price data for {ticker}: start={start_price}, end={end_price}")
            return None
        
        # Calculate return with precision
        gain_loss = end_price - start_price
        return_percent = (gain_loss / start_price) * 100
        
        result = ReturnCalculationResponse(
            ticker=ticker,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            start_price=self._round_currency(start_price),
            end_price=self._round_currency(end_price),
            gain_loss=self._round_currency(gain_loss),
            return_percent=self._round_percentage(return_percent)
        )
        
        logger.info(f"{ticker} return: {return_percent:.2f}% (${start_price:.2f} → ${end_price:.2f})")
        return result
    
    def get_gldm_debug_info(self, user_id: int) -> GLDMDebugResponse:
        """Get comprehensive GLDM debug information"""
        logger.info("Getting GLDM debug information")
        
        # Database data
        gldm_db = self.data_service.get_holding_by_ticker(user_id, "GLDM")
        db_data = {
            "current_price": gldm_db.current_price if gldm_db else None,
            "total_value": gldm_db.total_value if gldm_db else None,
            "gain_loss_percent": gldm_db.gain_loss_percent if gldm_db else None,
            "last_updated": gldm_db.last_updated.isoformat() if gldm_db and gldm_db.last_updated else None
        }
        
        # CSV data
        latest_price = self.data_service.get_latest_price("GLDM")
        sep_23_price = self.data_service.get_price_on_date("GLDM", date(2025, 9, 23))
        sep_30_price = self.data_service.get_price_on_date("GLDM", date(2025, 9, 30))
        
        # Calculate CSV return
        csv_return = None
        if sep_23_price and sep_30_price:
            csv_return = ((sep_30_price - sep_23_price) / sep_23_price) * 100
        
        csv_data = {
            "latest_price": latest_price,
            "sep_23_price": sep_23_price,
            "sep_30_price": sep_30_price,
            "calculated_return": self._round_percentage(csv_return) if csv_return else None,
            "csv_path": self.data_service.csv_path
        }
        
        logger.info(f"GLDM debug - DB: ${db_data['current_price']}, CSV: ${csv_data['latest_price']}, Return: {csv_data['calculated_return']}%")
        
        return GLDMDebugResponse(
            database=db_data,
            csv=csv_data,
            expected_return=2.56,
            status="success"
        )
    
    def get_top_holdings(self, user_id: int, limit: int = 10) -> List[HoldingResponse]:
        """Get top holdings by value"""
        holdings = self.data_service.get_portfolio_holdings(user_id)
        top_holdings = sorted(holdings, key=lambda h: h.total_value, reverse=True)[:limit]
        
        return [
            HoldingResponse(
                Ticker=h.ticker,
                Current_Price=self._round_currency(h.current_price),
                Total_Value=self._round_currency(h.total_value),
                Cost_Basis=self._round_currency(h.cost_basis),
                Gain_Loss=self._round_currency(h.gain_loss),
                Gain_Loss_Percent=self._round_percentage(h.gain_loss_percent),
                Category=h.category
            )
            for h in top_holdings
        ]
    
    def get_top_movers(self, user_id: int, limit: int = 10) -> List[HoldingResponse]:
        """Get top movers by percentage gain/loss"""
        holdings = self.data_service.get_portfolio_holdings(user_id)
        top_movers = sorted(holdings, key=lambda h: abs(h.gain_loss_percent), reverse=True)[:limit]
        
        return [
            HoldingResponse(
                Ticker=h.ticker,
                Current_Price=self._round_currency(h.current_price),
                Total_Value=self._round_currency(h.total_value),
                Cost_Basis=self._round_currency(h.cost_basis),
                Gain_Loss=self._round_currency(h.gain_loss),
                Gain_Loss_Percent=self._round_percentage(h.gain_loss_percent),
                Category=h.category
            )
            for h in top_movers
        ]
    
    # Helper methods
    def _empty_portfolio_response(self, user_name: str = "Unknown") -> PortfolioResponse:
        """Create empty portfolio response"""
        return PortfolioResponse(
            portfolio=[],
            summary=PortfolioSummary(
                Total_Value=0.0,
                Total_Cost_Basis=0.0,
                Total_Gain_Loss=0.0,
                Total_Gain_Loss_Percent=0.0,
                Total_Holdings=0,
                User=user_name
            ),
            status="success"
        )
    
    def _round_currency(self, value: float) -> float:
        """Round currency values to 2 decimal places"""
        return float(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    def _round_percentage(self, value: float) -> float:
        """Round percentage values to 2 decimal places"""
        return float(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))