"""
Perfect Portfolio API - The Way I Would Do It
Clean, efficient, production-ready from day one
"""

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
import time
import uvicorn
from typing import Dict, List

# Core imports
from core.config import settings
from core.logging import logger
from core.database import get_db, db_manager
from domain.models import User, PortfolioHolding
from domain.schemas import (
    PortfolioResponse, HoldingResponse, ReturnCalculationResponse,
    GLDMDebugResponse, UpdatePricesResponse, ErrorResponse,
    PriceUpdateRequest, ReturnCalculationRequest
)
from services.data_service import DataService
from services.portfolio_service import PortfolioService

# Create FastAPI app with perfect configuration
app = FastAPI(
    title=settings.APP_NAME,
    description="Perfect portfolio management API with clean architecture",
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# Security middleware
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app", "*.netlify.app"]
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Request timing and logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"🔄 {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add timing header
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        
        # Log response
        status_emoji = "✅" if response.status_code < 400 else "❌"
        logger.info(f"{status_emoji} {request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"❌ {request.method} {request.url.path} - ERROR - {process_time:.4f}s - {str(e)}")
        raise

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            detail="Internal server error. Please try again later.",
            status="error"
        ).dict()
    )

# Dependency injection - Perfect pattern
def get_data_service(db: Session = Depends(get_db)) -> DataService:
    """Get data service instance with database session"""
    return DataService(db)

def get_portfolio_service(
    data_service: DataService = Depends(get_data_service)
) -> PortfolioService:
    """Get portfolio service instance with data service"""
    return PortfolioService(data_service)

# API Routes - Clean and organized

@app.get("/", tags=["System"])
def root():
    """API root endpoint with system information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs" if settings.DEBUG else "disabled",
        "environment": "development" if settings.DEBUG else "production"
    }

@app.get("/health", tags=["System"])
def health_check(data_service: DataService = Depends(get_data_service)):
    """Comprehensive health check"""
    try:
        health_data = data_service.health_check()
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "timestamp": time.time(),
            "services": health_data
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )

# Portfolio endpoints - Perfect REST design
@app.get(
    "/api/v3/portfolio",
    response_model=PortfolioResponse,
    tags=["Portfolio"],
    summary="Get complete portfolio data",
    description="Returns complete portfolio with holdings and summary"
)
def get_portfolio(
    user_id: int = 1,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
) -> PortfolioResponse:
    """Get complete portfolio data with perfect error handling"""
    try:
        logger.info(f"📊 Getting portfolio for user {user_id}")
        result = portfolio_service.get_portfolio_summary(user_id)
        
        # Success metrics
        logger.info(f"✅ Portfolio retrieved: {result.summary.Total_Holdings} holdings, ${result.summary.Total_Value:,.2f}")
        
        return result
        
    except Exception as e:
        logger.error(f"Portfolio retrieval failed for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve portfolio: {str(e)}"
        )

@app.get(
    "/api/v3/portfolio/{user_id}/summary",
    response_model=Dict,
    tags=["Portfolio"],
    summary="Get portfolio summary only"
)
def get_portfolio_summary_only(
    user_id: int,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """Get portfolio summary only (optimized endpoint)"""
    try:
        result = portfolio_service.get_portfolio_summary(user_id)
        return {
            "summary": result.summary,
            "status": "success",
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Portfolio summary failed for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get(
    "/api/v3/portfolio/{user_id}/holdings",
    response_model=Dict,
    tags=["Portfolio"],
    summary="Get portfolio holdings only"
)
def get_portfolio_holdings_only(
    user_id: int,
    limit: int = 100,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """Get portfolio holdings only with optional limit"""
    try:
        result = portfolio_service.get_portfolio_summary(user_id)
        holdings = result.portfolio[:limit] if limit > 0 else result.portfolio
        
        return {
            "holdings": holdings,
            "count": len(holdings),
            "total_count": len(result.portfolio),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Portfolio holdings failed for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get(
    "/api/v3/portfolio/{user_id}/top-holdings",
    response_model=List[HoldingResponse],
    tags=["Portfolio"],
    summary="Get top holdings by value"
)
def get_top_holdings(
    user_id: int,
    limit: int = 10,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """Get top holdings by total value"""
    try:
        return portfolio_service.get_top_holdings(user_id, limit)
    except Exception as e:
        logger.error(f"Top holdings failed for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get(
    "/api/v3/portfolio/{user_id}/top-movers",
    response_model=List[HoldingResponse],
    tags=["Portfolio"],
    summary="Get top movers by percentage"
)
def get_top_movers(
    user_id: int,
    limit: int = 10,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """Get top movers by percentage gain/loss"""
    try:
        return portfolio_service.get_top_movers(user_id, limit)
    except Exception as e:
        logger.error(f"Top movers failed for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Data management endpoints
@app.post(
    "/api/v3/portfolio/{user_id}/update-prices",
    response_model=UpdatePricesResponse,
    tags=["Data Management"],
    summary="Update portfolio prices from CSV"
)
def update_portfolio_prices(
    user_id: int,
    request: PriceUpdateRequest = PriceUpdateRequest(),
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """Update portfolio prices from CSV data source"""
    try:
        logger.info(f"🔄 Updating prices for user {user_id} (force={request.force_update})")
        result = portfolio_service.update_prices_from_csv(user_id, request.force_update)
        
        logger.info(f"✅ Price update complete: {result.updated_count}/{result.total_holdings} updated")
        return result
        
    except Exception as e:
        logger.error(f"Price update failed for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Analysis endpoints
@app.post(
    "/api/v3/analysis/return",
    response_model=ReturnCalculationResponse,
    tags=["Analysis"],
    summary="Calculate return for ticker"
)
def calculate_return(
    request: ReturnCalculationRequest,
    user_id: int = 1,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """Calculate return for specific ticker between dates"""
    try:
        from datetime import datetime
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()
        
        result = portfolio_service.calculate_return(user_id, request.ticker, start_date, end_date)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No price data found for {request.ticker} in the specified date range"
            )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Return calculation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Debug endpoints (only in development)
if settings.DEBUG:
    @app.get(
        "/api/v3/debug/gldm",
        response_model=GLDMDebugResponse,
        tags=["Debug"],
        summary="GLDM debug information"
    )
    def get_gldm_debug(
        user_id: int = 1,
        portfolio_service: PortfolioService = Depends(get_portfolio_service)
    ):
        """Get comprehensive GLDM debug information"""
        try:
            return portfolio_service.get_gldm_debug_info(user_id)
        except Exception as e:
            logger.error(f"GLDM debug failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

# Legacy endpoints for backward compatibility
@app.get("/portfolio", include_in_schema=False)
def get_portfolio_legacy(
    user_id: int = 1,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """Legacy endpoint - use /api/v3/portfolio instead"""
    logger.warning("Using deprecated endpoint /portfolio - use /api/v3/portfolio")
    return get_portfolio(user_id, portfolio_service)

@app.get("/portfolio/gldm-debug", include_in_schema=False)
def get_gldm_debug_legacy(
    user_id: int = 1,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """Legacy debug endpoint"""
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")
    logger.warning("Using deprecated endpoint /portfolio/gldm-debug - use /api/v3/debug/gldm")
    return get_gldm_debug(user_id, portfolio_service)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="Perfect Portfolio API with clean architecture",
        routes=app.routes,
    )
    
    # Add custom info
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"📊 Environment: {'Development' if settings.DEBUG else 'Production'}")
    logger.info(f"🗄️  Database: {settings.DATABASE_URL}")
    logger.info(f"📁 CSV Path: {settings.CSV_PATH}")
    
    # Create database tables
    try:
        db_manager.create_tables()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info(f"🛑 Shutting down {settings.APP_NAME}")

# Main entry point
if __name__ == "__main__":
    logger.info("🚀 Starting Portfolio API - The Perfect Way")
    logger.info("📊 Clean Architecture | Type-Safe | Production-Ready")
    logger.info("🔧 CSV-based data with database integration")
    
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.DEBUG
    )
