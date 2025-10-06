"""
Pydantic Schemas - Perfect API Contracts
Type-safe, validated, documented
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class HoldingCategory(str, Enum):
    """Portfolio holding categories"""
    STOCK = "Stock"
    ETF = "ETF"
    BOND = "Bond"
    CRYPTO = "Crypto"
    CASH = "Cash"
    OTHER = "Other"

# Request schemas
class PriceUpdateRequest(BaseModel):
    """Request to update portfolio prices"""
    user_id: int = Field(default=1, ge=1, description="User ID")
    force_update: bool = Field(default=False, description="Force update even if recent")

class ReturnCalculationRequest(BaseModel):
    """Request to calculate returns"""
    ticker: str = Field(..., min_length=1, max_length=20, description="Stock ticker")
    start_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="End date (YYYY-MM-DD)")

# Response schemas
class HoldingResponse(BaseModel):
    """Portfolio holding response"""
    Ticker: str = Field(..., description="Stock ticker symbol")
    Current_Price: float = Field(..., ge=0, description="Current price per share")
    Total_Value: float = Field(..., ge=0, description="Total holding value")
    Cost_Basis: float = Field(..., ge=0, description="Original cost basis")
    Gain_Loss: float = Field(..., description="Absolute gain/loss")
    Gain_Loss_Percent: float = Field(..., description="Percentage gain/loss")
    Category: HoldingCategory = Field(default=HoldingCategory.STOCK, description="Asset category")
    
    class Config:
        schema_extra = {
            "example": {
                "Ticker": "GLDM",
                "Current_Price": 76.45,
                "Total_Value": 1848.54,
                "Cost_Basis": 2500.00,
                "Gain_Loss": -651.46,
                "Gain_Loss_Percent": -26.06,
                "Category": "Stock"
            }
        }

class PortfolioSummary(BaseModel):
    """Portfolio summary response"""
    Total_Value: float = Field(..., ge=0, description="Total portfolio value")
    Total_Cost_Basis: float = Field(..., ge=0, description="Total cost basis")
    Total_Gain_Loss: float = Field(..., description="Total gain/loss")
    Total_Gain_Loss_Percent: float = Field(..., description="Total percentage gain/loss")
    Total_Holdings: int = Field(..., ge=0, description="Number of holdings")
    User: str = Field(..., description="User name")
    
    class Config:
        schema_extra = {
            "example": {
                "Total_Value": 315991.61,
                "Total_Cost_Basis": 242190.15,
                "Total_Gain_Loss": 73801.46,
                "Total_Gain_Loss_Percent": 30.47,
                "Total_Holdings": 115,
                "User": "Kishore Chandramouli"
            }
        }

class PortfolioResponse(BaseModel):
    """Complete portfolio response"""
    portfolio: List[HoldingResponse] = Field(..., description="List of portfolio holdings")
    summary: PortfolioSummary = Field(..., description="Portfolio summary")
    status: str = Field(default="success", description="Response status")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Response timestamp")

class ReturnCalculationResponse(BaseModel):
    """Return calculation response"""
    ticker: str = Field(..., description="Stock ticker")
    start_date: str = Field(..., description="Start date")
    end_date: str = Field(..., description="End date")
    start_price: float = Field(..., ge=0, description="Starting price")
    end_price: float = Field(..., ge=0, description="Ending price")
    gain_loss: float = Field(..., description="Absolute gain/loss")
    return_percent: float = Field(..., description="Percentage return")
    
    class Config:
        schema_extra = {
            "example": {
                "ticker": "GLDM",
                "start_date": "2025-09-23",
                "end_date": "2025-09-30",
                "start_price": 74.54,
                "end_price": 76.45,
                "gain_loss": 1.91,
                "return_percent": 2.56
            }
        }

class GLDMDebugResponse(BaseModel):
    """GLDM debug information response"""
    database: Dict[str, Any] = Field(..., description="Database values")
    csv: Dict[str, Any] = Field(..., description="CSV values")
    expected_return: float = Field(default=2.56, description="Expected return percentage")
    status: str = Field(default="success", description="Response status")

class UpdatePricesResponse(BaseModel):
    """Price update response"""
    updated_count: int = Field(..., ge=0, description="Number of holdings updated")
    total_holdings: int = Field(..., ge=0, description="Total number of holdings")
    errors: List[str] = Field(default=[], description="List of errors encountered")
    status: str = Field(..., description="Update status")
    
    class Config:
        schema_extra = {
            "example": {
                "updated_count": 5,
                "total_holdings": 115,
                "errors": [],
                "status": "success"
            }
        }

# Error schemas
class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str = Field(..., description="Error message")
    status: str = Field(default="error", description="Response status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
