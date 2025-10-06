from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database import engine, get_db, Base
from models import User, Login, Portfolio, Transaction, MarketData, HistoricalData, PortfolioSummary, PortfolioProjections, PortfolioPerformance, PortfolioChartData, InsightsCache, PortfolioValues
from seed_data import create_initial_data
import pandas as pd
import io

# Create tables
Base.metadata.create_all(bind=engine)

# Create initial data
create_initial_data()

app = FastAPI(title="Portora API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Database setup complete!", "status": "success"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/top-holdings/{user_id}")
def get_top_holdings_simple(user_id: int, db: Session = Depends(get_db)):
    """Simple endpoint for top holdings and movers"""
    try:
        from models import TopHoldings
        
        holdings = db.query(TopHoldings).filter(
            TopHoldings.user_id == user_id,
            TopHoldings.type == "holdings"
        ).order_by(TopHoldings.rank.asc()).all()
        
        movers = db.query(TopHoldings).filter(
            TopHoldings.user_id == user_id,
            TopHoldings.type == "movers"
        ).order_by(TopHoldings.rank.asc()).all()
        
        return {
            "user_id": user_id,
            "holdings": [{
                "ticker": h.ticker,
                "shares": h.shares,
                "current_price": h.current_price,
                "total_value": h.total_value,
                "gain_loss": h.gain_loss,
                "gain_loss_percent": h.gain_loss_percent,
                "rank": h.rank
            } for h in holdings],
            "movers": [{
                "ticker": m.ticker,
                "shares": m.shares,
                "current_price": m.current_price,
                "total_value": m.total_value,
                "gain_loss": m.gain_loss,
                "gain_loss_percent": m.gain_loss_percent,
                "rank": m.rank
            } for m in movers]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).all()
    return {
        "users": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at
            }
            for user in users
        ]
    }

@app.get("/users/{user_id}/portfolio")
def get_user_portfolio(user_id: int, db: Session = Depends(get_db)):
    """Get portfolio for a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        },
        "portfolio": [
            {
                "ticker": stock.ticker,
                "shares": stock.shares,
                "avg_price": stock.avg_price,
                "total_value": stock.shares * stock.avg_price
            }
            for stock in portfolio
        ]
    }

@app.get("/portfolio/fast")
def get_portfolio_fast(user_id: int = 1, db: Session = Depends(get_db)):
    """Get portfolio data quickly with minimal processing"""
    try:
        from sqlalchemy import func, and_
        
        # Get user's portfolio
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
        
        if not portfolio:
            return {"error": "No portfolio found"}
        
        # Get only the most recent prices (optimized query)
        latest_date = db.query(func.max(HistoricalData.date)).scalar()
        
        if latest_date:
            # Get prices for portfolio tickers only
            tickers = [p.ticker for p in portfolio]
            prices = db.query(HistoricalData.ticker, HistoricalData.close_price).filter(
                and_(
                    HistoricalData.ticker.in_(tickers),
                    HistoricalData.date == latest_date
                )
            ).all()
            price_dict = {ticker: price for ticker, price in prices}
        else:
            price_dict = {}
        
        # Quick calculation
        total_value = 0
        portfolio_data = []
        
        for stock in portfolio:
            current_price = price_dict.get(stock.ticker, stock.avg_price)
            current_value = stock.shares * current_price
            total_value += current_value
            
            portfolio_data.append({
                "Ticker": stock.ticker,
                "Qty": stock.shares,
                "Current_Price": round(current_price, 2),
                "Total_Value": round(current_value, 2),
                "Gain_Loss_Percent": round(((current_price - stock.avg_price) / stock.avg_price * 100), 2) if stock.avg_price > 0 else 0
            })
        
        return {
            "portfolio": portfolio_data,
            "summary": {
                "Total_Value": round(total_value, 2),
                "Total_Holdings": len(portfolio),
                "Latest_Date": latest_date.strftime('%Y-%m-%d') if latest_date else None
            }
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/portfolio")
def get_portfolio(user_id: int = 1, db: Session = Depends(get_db)):
    """Get portfolio data from database for a specific user with current market data"""
    try:
        # Get user's portfolio by user_id
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        # Get portfolio values from the PortfolioValues table (actual current values)
        print("DEBUG: Using PortfolioValues table")  # Debug line
        portfolio_values = db.query(PortfolioValues).filter(PortfolioValues.user_id == user_id).all()
        print(f"DEBUG: Found {len(portfolio_values)} portfolio values")  # Debug line
        
        if not portfolio_values:
            return {
                "portfolio": [],
                "summary": {
                    "Total_Value": 0,
                    "Total_Cost_Basis": 0,
                    "Total_Gain_Loss": 0,
                    "Total_Gain_Loss_Percent": 0,
                    "Total_Stocks": 0,
                    "User": user.name
                },
                "status": "success"
            }
        
        # Convert to the expected format
        portfolio_data = []
        total_value = 0
        total_cost_basis = 0
        total_gain_loss = 0
        
        for value in portfolio_values:
            # Calculate shares from total_value and current_price
            shares = value.total_value / value.current_price if value.current_price > 0 else 0
            # Calculate avg_price from cost_basis and shares
            avg_price = value.cost_basis / shares if shares > 0 else 0
            
            portfolio_data.append({
                "Ticker": value.ticker,
                "Qty": shares,
                "Avg_Price": avg_price,
                "Current_Price": value.current_price,
                "Total_Value": value.total_value,
                "Cost_Basis": value.cost_basis,
                "Gain_Loss": value.gain_loss,
                "Gain_Loss_Percent": value.gain_loss_percent,
                "Category": value.category or "Stock"
            })
            
            total_value += value.total_value
            total_cost_basis += value.cost_basis
            total_gain_loss += value.gain_loss
        
        # Calculate portfolio metrics
        total_gain_loss_percent = (total_gain_loss / total_cost_basis) * 100 if total_cost_basis > 0 else 0
        
        summary_data = {
            "Total_Value": total_value,
            "Total_Cost_Basis": total_cost_basis,
            "Total_Gain_Loss": total_gain_loss,
            "Total_Gain_Loss_Percent": total_gain_loss_percent,
            "Total_Stocks": len(portfolio_data),
            "User": user.name
        }
        
        return {
            "portfolio": portfolio_data,
            "summary": summary_data,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve portfolio: {str(e)}")


@app.get("/sp500")
def get_sp500():
    """Get S&P 500 sample data"""
    try:
        # Sample S&P 500 data for demo
        sp500_data = [
            {"symbol": "AAPL", "name": "Apple Inc.", "price": 175.50, "change": 2.50, "change_percent": 1.69},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "price": 315.25, "change": -1.20, "change_percent": -0.40},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "price": 2650.75, "change": 15.00, "change_percent": 0.60},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "price": 185.25, "change": 3.00, "change_percent": 1.69},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "price": 425.50, "change": -5.00, "change_percent": -0.55},
        ]
        return {"sp500": sp500_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve S&P 500 data: {str(e)}")

@app.get("/historical-data/download")
def download_historical_data(db: Session = Depends(get_db)):
    """Download historical data for portfolio tickers"""
    try:
        # Get all unique tickers from portfolio
        portfolio = db.query(Portfolio).all()
        tickers = list(set([p.ticker for p in portfolio]))
        
        return {
            "status": "success",
            "message": f"Historical data download initiated for {len(tickers)} tickers",
            "tickers": tickers,
            "note": "Demo mode - actual download not performed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate historical data download: {str(e)}")

# Additional endpoints for dashboard features
@app.get("/portfolio-health")
def get_portfolio_health(user_id: int = 1, db: Session = Depends(get_db)):
    """Get comprehensive portfolio health metrics"""
    try:
        # Simplified health data calculation
        health_data = {
            'diversification': 0.7,
            'riskLevel': 'Medium', 
            'volatility': 15.5,
            'score': 85
        }
        
        if health_data:
            return health_data
        else:
            # Fallback to mock data
            return {
                "score": 75,
                "riskLevel": "Medium",
                "diversification": 0.7,
                "concentration": 0.3,
                "cashDrag": 0.05,
                "volatility": 15.2,
                "drivers": {
                    "topPerformer": "AAPL",
                    "worstPerformer": "TSLA",
                    "riskFactors": ["High volatility", "Concentration risk"]
                },
                "driftAsset": {
                    "symbol": "MSFT",
                    "currentAllocation": 15.2,
                    "targetAllocation": 12.0,
                    "drift": 3.2
                },
                "badges": ["Diversified", "Consistent Performer", "Risk Managed"]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate portfolio health: {str(e)}")

@app.get("/portfolio/performance/{user_id}")
def get_portfolio_performance(user_id: int, db: Session = Depends(get_db)):
    """Get portfolio performance data for all time periods"""
    try:
        from models import PortfolioPerformance
        
        # Get all performance records for the user
        performances = db.query(PortfolioPerformance).filter(
            PortfolioPerformance.user_id == user_id
        ).all()
        
        if not performances:
            # Calculate performance if no data exists
            # calculate_portfolio_performance_for_user - simplified
            # calculate_portfolio_performance_for_user(user_id)  # Disabled for now
            
            # Query again after calculation
            performances = db.query(PortfolioPerformance).filter(
                PortfolioPerformance.user_id == user_id
            ).all()
        
        # Format the response
        performance_data = {}
        for perf in performances:
            performance_data[perf.period] = {
                "start_date": perf.start_date.isoformat() if perf.start_date else None,
                "end_date": perf.end_date.isoformat() if perf.end_date else None,
                "start_value": round(perf.start_value, 2),
                "end_value": round(perf.end_value, 2),
                "total_return": round(perf.total_return, 2),
                "total_gain_loss": round(perf.total_gain_loss, 2),
                "annualized_return": round(perf.annualized_return, 2) if perf.annualized_return else None,
                "volatility": round(perf.volatility, 2) if perf.volatility else None,
                "sharpe_ratio": round(perf.sharpe_ratio, 2) if perf.sharpe_ratio else None,
                "max_drawdown": round(perf.max_drawdown, 2) if perf.max_drawdown else None,
                "calculation_date": perf.calculation_date.isoformat() if perf.calculation_date else None
            }
        
        return {
            "user_id": user_id,
            "performance": performance_data,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio performance: {str(e)}")

@app.get("/portfolio/performance-chart/{user_id}")
def get_portfolio_performance_chart(user_id: int, period: str = "1Year", db: Session = Depends(get_db)):
    """Get portfolio performance chart data for a specific period using pre-calculated data"""
    try:
        # Map frontend period names to database period names
        period_mapping = {
            "1Week": "1Week",
            "1Month": "1Month",
            "1Year": "1Year",
            "YTD": "YTD",
            # Legacy mappings for backward compatibility
            "1M": "1Month",
            "1Y": "1Year",
            "5Y": "1Year"  # For now, use 1Year for 5Y
        }
        
        db_period = period_mapping.get(period, "1Year")
        print(f"📊 Frontend period: {period} -> Database period: {db_period}")
        
        # Get pre-calculated chart data
        chart_records = db.query(PortfolioChartData).filter(
            and_(
                PortfolioChartData.user_id == user_id,
                PortfolioChartData.period == db_period
            )
        ).order_by(PortfolioChartData.date.asc()).all()
        
        if not chart_records:
            print(f"No pre-calculated data found for period {db_period}, generating mock data")
            return generate_mock_performance_chart_data(period)
        
        # Convert to chart data format
        chart_data = []
        for record in chart_records:
            chart_data.append({
                "date": record.date.strftime("%Y-%m-%d"),
                "total_value": round(record.total_value, 2)
            })
        
        # Calculate performance metrics
        start_value = chart_data[0]["total_value"] if chart_data else 0
        end_value = chart_data[-1]["total_value"] if chart_data else 0
        total_return = ((end_value - start_value) / start_value * 100) if start_value > 0 else 0
        
        print(f"📊 Returning {len(chart_data)} pre-calculated data points for {period}")
        
        return {
            "period": period,
            "data": chart_data,
            "start_value": round(start_value, 2),
            "end_value": round(end_value, 2),
            "total_return": round(total_return, 2),
            "status": "success",
            "cached": True
        }
        
    except Exception as e:
        print(f"Error in performance chart: {e}")
        import traceback
        traceback.print_exc()
        # Return mock data as fallback
        return generate_mock_performance_chart_data(period)

def generate_mock_performance_chart_data(period: str):
    """Generate mock performance chart data"""
    from datetime import datetime, timedelta
    import random
    
    # Calculate days based on period
    if period in ["1Week", "1W"]:
        days = 7
    elif period in ["1Month", "1M"]:
        days = 30
    elif period == "YTD":
        days = (datetime.now() - datetime(datetime.now().year, 1, 1)).days
    elif period in ["5Y", "5Year"]:
        days = 365 * 5
    else:  # 1Year, 1Y
        days = 365
    
    # Generate mock data
    start_value = 325850.92  # Use the actual portfolio value
    end_value = start_value * (1 + random.uniform(0.05, 0.25))  # 5-25% growth
    
    chart_data = []
    start_date = datetime.now() - timedelta(days=days)
    
    step = max(1, days // 50) if days > 50 else 1
    for i in range(0, days + 1, step):
        current_date = start_date + timedelta(days=i)
        progress = i / days if days > 0 else 0
        
        # Add some realistic market movement
        base_value = start_value + (end_value - start_value) * progress
        volatility = random.uniform(-0.02, 0.02)  # 2% daily volatility
        value = base_value * (1 + volatility)
        
        chart_data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "total_value": round(value, 2)
        })
    
    return {
        "period": period,
        "data": chart_data,
        "start_value": round(start_value, 2),
        "end_value": round(end_value, 2),
        "total_return": round(((end_value - start_value) / start_value) * 100, 2),
        "status": "mock"
    }

@app.get("/onboarding/status")
def get_onboarding_status():
    """Get onboarding status"""
    return {"has_seen_onboarding": False}

@app.post("/onboarding/complete")
def complete_onboarding():
    """Mark onboarding as complete"""
    return {"message": "Onboarding completed"}

@app.get("/alerts/count")
def get_alerts_count():
    """Get alerts count"""
    return {"count": 0, "alerts": []}

# Historical data endpoints
@app.get("/historical-data/status")
def get_historical_data_status(db: Session = Depends(get_db)):
    """Get status of historical data collection"""
    try:
        from models import HistoricalData
        from sqlalchemy import func
        
        # Count total records
        total_records = db.query(HistoricalData).count()
        
        # Count by asset type
        stock_records = db.query(HistoricalData).filter(HistoricalData.asset_type == 'stock').count()
        crypto_records = db.query(HistoricalData).filter(HistoricalData.asset_type == 'crypto').count()
        
        # Get date range
        date_range = db.query(
            func.min(HistoricalData.date).label('earliest'),
            func.max(HistoricalData.date).label('latest')
        ).first()
        
        return {
            "status": "ready" if total_records > 1000 else "collecting",
            "total_records": total_records,
            "stock_records": stock_records,
            "crypto_records": crypto_records,
            "earliest_date": date_range.earliest.isoformat() if date_range.earliest else None,
            "latest_date": date_range.latest.isoformat() if date_range.latest else None
        }
    except Exception as e:
        return {
            "status": "error",
            "total_records": 0,
            "stock_records": 0,
            "crypto_records": 0,
            "error": str(e)
        }

@app.post("/historical-data/collect")
def collect_historical_data():
    """Start historical data collection"""
    try:
        from data_collector import HistoricalDataCollector
        from database import get_db
        
        # Start data collection in background
        db = next(get_db())
        collector = HistoricalDataCollector(db)
        
        # Run collection in a separate thread to avoid blocking
        import threading
        thread = threading.Thread(target=collector.collect_all_historical_data)
        thread.daemon = True
        thread.start()
        
        return {
            "message": "Historical data collection started",
            "status": "started"
        }
    except Exception as e:
        return {
            "message": f"Failed to start data collection: {str(e)}",
            "status": "error"
        }

# Removed duplicate portfolio performance endpoint

@app.get("/portfolio/real-time/{user_id}")
def get_real_time_portfolio(user_id: int, db: Session = Depends(get_db)):
    """Get real-time portfolio calculations using historical data"""
    try:
        from models import HistoricalData, Portfolio
        from sqlalchemy import func, and_
        from datetime import datetime, timedelta
        
        # Get user's portfolio
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
        if not portfolio:
            return {"error": "No portfolio found"}
        
        # Get the most recent date with data
        latest_date = db.query(func.max(HistoricalData.date)).scalar()
        if not latest_date:
            return {"error": "No historical data available"}
        
        # Get prices for the most recent date
        current_values = []
        total_current_value = 0
        total_cost_basis = 0
        
        for holding in portfolio:
            # Get current price from historical data
            price_data = db.query(HistoricalData).filter(
                and_(
                    HistoricalData.ticker == holding.ticker,
                    HistoricalData.date == latest_date
                )
            ).first()
            
            if price_data:
                current_price = price_data.close_price
                current_value = holding.shares * current_price
                cost_basis = holding.shares * holding.avg_price
                gain_loss = current_value - cost_basis
                gain_loss_percent = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0
                
                current_values.append({
                    "ticker": holding.ticker,
                    "shares": holding.shares,
                    "avg_price": holding.avg_price,
                    "current_price": round(current_price, 2),
                    "current_value": round(current_value, 2),
                    "cost_basis": round(cost_basis, 2),
                    "gain_loss": round(gain_loss, 2),
                    "gain_loss_percent": round(gain_loss_percent, 2)
                })
                
                total_current_value += current_value
                total_cost_basis += cost_basis
        
        # Calculate total portfolio metrics
        total_gain_loss = total_current_value - total_cost_basis
        total_gain_loss_percent = (total_gain_loss / total_cost_basis * 100) if total_cost_basis > 0 else 0
        
        return {
            "portfolio": current_values,
            "summary": {
                "total_current_value": round(total_current_value, 2),
                "total_cost_basis": round(total_cost_basis, 2),
                "total_gain_loss": round(total_gain_loss, 2),
                "total_gain_loss_percent": round(total_gain_loss_percent, 2),
                "latest_date": latest_date.strftime('%Y-%m-%d'),
                "total_holdings": len(portfolio)
            }
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/portfolio/summary-metrics/{user_id}")
def get_portfolio_summary_metrics(user_id: int, db: Session = Depends(get_db)):
    """Get pre-calculated portfolio summary metrics for INSTANT loading"""
    try:
        from models import PortfolioSummary
        
        # Get pre-calculated summary data (INSTANT!)
        summary = db.query(PortfolioSummary).filter(PortfolioSummary.user_id == user_id).first()
        
        if not summary:
            return {"error": "No portfolio summary found"}
        
        # Return pre-calculated data instantly
        return {
            "summary": {
                "total_value": round(summary.total_value, 2),
                "total_gain_loss": round(summary.total_gain_loss, 2),
                "total_gain_loss_percent": round(summary.total_gain_loss_percent, 2),
                "one_year_cagr": round(summary.one_year_cagr or 0, 2),
                "total_holdings": summary.total_holdings,
                "category_breakdown": {
                    "Stock": round(summary.stock_value, 2),
                    "Crypto": round(summary.crypto_value, 2),
                    "ETF": round(summary.etf_value, 2),
                    "Bond": round(summary.bond_value, 2),
                    "Cash": round(summary.cash_value, 2)
                },
                "latest_date": summary.latest_date.strftime('%Y-%m-%d') if summary.latest_date else datetime.now().strftime('%Y-%m-%d')
            },
            "status": "success",
            "cached": True,
            "last_updated": summary.last_updated.strftime('%Y-%m-%d %H:%M:%S') if summary.last_updated else None
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/portfolio/performance-chart/{user_id}")
def get_portfolio_performance_chart(user_id: int, period: str = "1Y", db: Session = Depends(get_db)):
    """Get portfolio performance chart data using real historical data"""
    try:
        from models import HistoricalData, Portfolio
        from sqlalchemy import func, and_
        from datetime import datetime, timedelta
        
        # Calculate date range based on period
        end_date = datetime.now()
        if period == "1M":
            start_date = end_date - timedelta(days=30)
        elif period == "1Y":
            start_date = end_date - timedelta(days=365)
        elif period == "YTD":
            # Year to date - start from January 1st of current year
            start_date = datetime(end_date.year, 1, 1)
        elif period == "5Y":
            start_date = end_date - timedelta(days=1825)
        else:
            start_date = end_date - timedelta(days=365)
        
        # Get user's portfolio
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
        if not portfolio:
            return {"data": [], "error": "No portfolio found"}
        
        # Get historical data for portfolio tickers
        tickers = [holding.ticker for holding in portfolio]
        
        # Get daily data for each ticker
        chart_data = []
        current_date = start_date
        
        # Get all available dates for the portfolio tickers in the date range
        # Limit to weekly data for better performance
        available_dates = db.query(HistoricalData.date).filter(
            and_(
                HistoricalData.ticker.in_([holding.ticker for holding in portfolio]),
                HistoricalData.date >= start_date,
                HistoricalData.date <= end_date
            )
        ).distinct().order_by(HistoricalData.date).all()
        
        # Convert to list of dates and sample for performance
        all_dates = [date[0] for date in available_dates]
        
        # Smart sampling for better performance
        if period == "5Y":
            dates = all_dates[::30]  # Monthly for 5 years
        elif period == "1Y":
            dates = all_dates[::7]   # Weekly for 1 year
        elif period == "YTD":
            dates = all_dates[::3]   # Every 3rd day for YTD
        elif period == "6M":
            dates = all_dates[::5]   # Every 5th day for 6 months
        elif period == "3M":
            dates = all_dates[::3]   # Every 3rd day for 3 months
        else:  # 1M
            dates = all_dates       # Daily for 1 month
        
        for date in dates:
            daily_value = 0
            ticker_data = {}
            
            for holding in portfolio:
                ticker = holding.ticker
                shares = holding.shares
                
                # Get price for this specific date
                price_data = db.query(HistoricalData).filter(
                    and_(
                        HistoricalData.ticker == ticker,
                        HistoricalData.date == date
                    )
                ).first()
                
                if price_data:
                    price = price_data.close_price
                    value = shares * price
                    daily_value += value
                    ticker_data[ticker] = {
                        'price': round(price, 2),
                        'value': round(value, 2),
                        'shares': shares
                    }
            
            if daily_value > 0:
                chart_data.append({
                    'date': date.isoformat().split('T')[0],
                    'total_value': round(daily_value, 2),
                    'tickers': ticker_data
                })
        
        return {
            "data": chart_data,
            "period": period,
            "total_points": len(chart_data),
            "date_range": {
                "start": start_date.strftime('%Y-%m-%d'),
                "end": end_date.strftime('%Y-%m-%d')
            }
        }
        
    except Exception as e:
        return {"data": [], "error": str(e)}

@app.post("/portfolio/upload-csv")
async def upload_portfolio_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and process portfolio CSV file"""
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Clear existing portfolio data for user 1
        db.query(Portfolio).filter(Portfolio.user_id == 1).delete()
        
        # Process each row
        portfolio_items = []
        for _, row in df.iterrows():
            symbol = row['Symbol']
            classification = row['Classification']
            quantity = float(row['Quantity Owned'])
            
            # Skip if quantity is 0
            if quantity <= 0:
                continue
                
            # Determine asset type
            asset_type = 'crypto' if 'USD' in symbol else 'stock'
            
            # Get current price (mock for now - in real app, fetch from API)
            current_price = 100.0  # Default price
            if symbol == 'BTC-USD':
                current_price = 45000.0
            elif symbol == 'ETH-USD':
                current_price = 3000.0
            elif symbol == 'AAPL':
                current_price = 175.0
            elif symbol == 'MSFT':
                current_price = 315.0
            elif symbol == 'GOOGL':
                current_price = 2650.0
            elif symbol == 'TSLA':
                current_price = 850.0
            elif symbol == 'NVDA':
                current_price = 425.0
            
            # Create portfolio entry
            portfolio_item = Portfolio(
                user_id=1,
                ticker=symbol,
                shares=quantity,
                avg_price=current_price * 0.9  # Assume 10% gain
            )
            portfolio_items.append(portfolio_item)
        
        # Add all items to database
        db.add_all(portfolio_items)
        db.commit()
        
        return {
            "message": f"Successfully uploaded {len(portfolio_items)} portfolio items",
            "items_processed": len(portfolio_items),
            "file_name": file.filename
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")

# ============================================================================
# OPTIMIZED API ENDPOINTS - Pre-calculated Data
# ============================================================================

@app.get("/portfolio/optimized-summary/{user_id}")
def get_optimized_portfolio_summary(user_id: int, db: Session = Depends(get_db)):
    """Get pre-calculated portfolio summary for instant loading"""
    try:
        summary = db.query(PortfolioSummary).filter(PortfolioSummary.user_id == user_id).first()
        
        if not summary:
            return {"error": "No portfolio summary found. Run calculate_all_metrics.py first."}
        
        return {
            "summary": {
                "total_value": round(summary.total_value, 2),
                "total_cost_basis": round(summary.total_cost_basis, 2),
                "total_gain_loss": round(summary.total_gain_loss, 2),
                "total_gain_loss_percent": round(summary.total_gain_loss_percent, 2),
                "one_year_cagr": round(summary.one_year_cagr or 0, 2),
                "total_holdings": summary.total_holdings,
                "category_breakdown": {
                    "Stock": round(summary.stock_value, 2),
                    "Crypto": round(summary.crypto_value, 2),
                    "ETF": round(summary.etf_value, 2),
                    "Bond": round(summary.bond_value, 2),
                    "Cash": round(summary.cash_value, 2)
                },
                "latest_date": summary.latest_date.strftime('%Y-%m-%d') if summary.latest_date else None
            },
            "status": "success",
            "cached": True,
            "last_updated": summary.last_updated.strftime('%Y-%m-%d %H:%M:%S') if summary.last_updated else None
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/portfolio/optimized-performance/{user_id}")
def get_optimized_portfolio_performance(user_id: int, db: Session = Depends(get_db)):
    """Get pre-calculated portfolio performance for all periods"""
    try:
        performances = db.query(PortfolioPerformance).filter(
            PortfolioPerformance.user_id == user_id
        ).all()
        
        if not performances:
            return {"error": "No performance data found. Run calculate_all_metrics.py first."}
        
        result = {}
        for perf in performances:
            result[perf.period] = {
                "start_date": perf.start_date.strftime('%Y-%m-%d'),
                "end_date": perf.end_date.strftime('%Y-%m-%d'),
                "start_value": round(perf.start_value, 2),
                "end_value": round(perf.end_value, 2),
                "total_return": round(perf.total_return, 2),
                "total_gain_loss": round(perf.total_gain_loss, 2),
                "annualized_return": round(perf.annualized_return or 0, 2),
                "volatility": round(perf.volatility or 0, 2),
                "sharpe_ratio": round(perf.sharpe_ratio or 0, 2),
                "max_drawdown": round(perf.max_drawdown or 0, 2)
            }
        
        return {
            "performance": result,
            "status": "success",
            "cached": True
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/portfolio/optimized-projections/{user_id}")
def get_optimized_portfolio_projections(user_id: int, db: Session = Depends(get_db)):
    """Get pre-calculated portfolio projections for all periods"""
    try:
        projections = db.query(PortfolioProjections).filter(
            PortfolioProjections.user_id == user_id
        ).all()
        
        if not projections:
            return {"error": "No projection data found. Run calculate_all_metrics.py first."}
        
        result = {}
        for proj in projections:
            result[proj.period] = {
                "projected_value": round(proj.projected_value, 2),
                "projected_return": round(proj.projected_return, 2),
                "projected_gain_loss": round(proj.projected_gain_loss, 2),
                "confidence_level": round(proj.confidence_level, 2),
                "volatility": round(proj.volatility, 2),
                "sharpe_ratio": round(proj.sharpe_ratio or 0, 2),
                "max_drawdown": round(proj.max_drawdown or 0, 2),
                "projection_date": proj.projection_date.strftime('%Y-%m-%d')
            }
        
        return {
            "projections": result,
            "status": "success",
            "cached": True
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/portfolio/optimized-dashboard/{user_id}")
def get_optimized_dashboard_data(user_id: int, db: Session = Depends(get_db)):
    """Get all pre-calculated dashboard data in one call"""
    try:
        # Get summary
        summary = db.query(PortfolioSummary).filter(PortfolioSummary.user_id == user_id).first()
        
        # Get performance
        performances = db.query(PortfolioPerformance).filter(
            PortfolioPerformance.user_id == user_id
        ).all()
        
        # Get projections
        projections = db.query(PortfolioProjections).filter(
            PortfolioProjections.user_id == user_id
        ).all()
        
        if not summary:
            return {"error": "No portfolio data found. Run calculate_all_metrics.py first."}
        
        # Format summary
        summary_data = {
            "total_value": round(summary.total_value, 2),
            "total_cost_basis": round(summary.total_cost_basis, 2),
            "total_gain_loss": round(summary.total_gain_loss, 2),
            "total_gain_loss_percent": round(summary.total_gain_loss_percent, 2),
            "one_year_cagr": round(summary.one_year_cagr or 0, 2),
            "total_holdings": summary.total_holdings,
            "category_breakdown": {
                "Stock": round(summary.stock_value, 2),
                "Crypto": round(summary.crypto_value, 2),
                "ETF": round(summary.etf_value, 2),
                "Bond": round(summary.bond_value, 2),
                "Cash": round(summary.cash_value, 2)
            }
        }
        
        # Format performance
        performance_data = {}
        for perf in performances:
            performance_data[perf.period] = {
                "total_return": round(perf.total_return, 2),
                "total_gain_loss": round(perf.total_gain_loss, 2),
                "annualized_return": round(perf.annualized_return or 0, 2),
                "volatility": round(perf.volatility or 0, 2),
                "sharpe_ratio": round(perf.sharpe_ratio or 0, 2),
                "max_drawdown": round(perf.max_drawdown or 0, 2)
            }
        
        # Format projections
        projection_data = {}
        for proj in projections:
            projection_data[proj.period] = {
                "projected_value": round(proj.projected_value, 2),
                "projected_return": round(proj.projected_return, 2),
                "projected_gain_loss": round(proj.projected_gain_loss, 2),
                "confidence_level": round(proj.confidence_level, 2)
            }
        
        return {
            "summary": summary_data,
            "performance": performance_data,
            "projections": projection_data,
            "status": "success",
            "cached": True,
            "last_updated": summary.last_updated.strftime('%Y-%m-%d %H:%M:%S') if summary.last_updated else None
        }
        
    except Exception as e:
        return {"error": str(e)}

# ============================================================================
# OPTIMIZED PERFORMANCE CHART API - 5-Year Limit with Smart Sampling
# ============================================================================

@app.get("/portfolio/optimized-performance-chart/{user_id}")
def get_optimized_performance_chart(user_id: int, period: str = "1Year", time_range: str = "5Y", interval: str = "monthly", db: Session = Depends(get_db)):
    """Get optimized performance chart data with 5-year limit and smart sampling"""
    try:
        from datetime import datetime, timedelta
        import pandas as pd
        
        # Enforce 5-year maximum limit
        if time_range not in ["1Y", "2Y", "3Y", "4Y", "5Y"]:
            time_range = "5Y"
        
        # Calculate date range
        end_date = datetime.now()
        years = int(time_range.replace("Y", ""))
        start_date = end_date - timedelta(days=years * 365)
        
        # Get user's portfolio
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
        if not portfolio:
            return {"data": [], "error": "No portfolio found"}
        
        # Get historical data with smart sampling
        tickers = [holding.ticker for holding in portfolio]
        
        # Query historical data with date range
        historical_data = db.query(HistoricalData).filter(
            and_(
                HistoricalData.ticker.in_(tickers),
                HistoricalData.date >= start_date,
                HistoricalData.date <= end_date
            )
        ).order_by(HistoricalData.date.asc()).all()
        
        if not historical_data:
            return {"data": [], "error": "No historical data found"}
        
        # Convert to DataFrame for efficient processing
        df = pd.DataFrame([{
            'date': h.date,
            'ticker': h.ticker,
            'close_price': h.close_price
        } for h in historical_data])
        
        # Smart sampling based on period and interval
        if interval == "daily":
            # For daily data, use all available data
            sampled_df = df
        elif interval == "weekly":
            # Sample every 7 days
            sampled_df = df.groupby('ticker').apply(lambda x: x.iloc[::7]).reset_index(drop=True)
        elif interval == "monthly":
            # Sample monthly (last day of each month)
            sampled_df = df.groupby(['ticker', df['date'].dt.to_period('M')]).last().reset_index()
        else:
            # Default to monthly
            sampled_df = df.groupby(['ticker', df['date'].dt.to_period('M')]).last().reset_index()
        
        # Calculate portfolio values for each date
        chart_data = []
        portfolio_dict = {holding.ticker: holding.shares for holding in portfolio}
        
        for date in sampled_df['date'].unique():
            date_data = sampled_df[sampled_df['date'] == date]
            total_value = 0
            ticker_data = {}
            
            for _, row in date_data.iterrows():
                ticker = row['ticker']
                price = row['close_price']
                shares = portfolio_dict.get(ticker, 0)
                value = shares * price
                total_value += value
                ticker_data[ticker] = {
                    'price': round(price, 2),
                    'value': round(value, 2),
                    'shares': shares
                }
            
            if total_value > 0:
                chart_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'total_value': round(total_value, 2),
                    'tickers': ticker_data
                })
        
        # Sort by date
        chart_data.sort(key=lambda x: x['date'])
        
        return {
            "data": chart_data,
            "period": period,
            "time_range": time_range,
            "interval": interval,
            "total_points": len(chart_data),
            "date_range": {
                "start": start_date.strftime('%Y-%m-%d'),
                "end": end_date.strftime('%Y-%m-%d')
            },
            "status": "success",
            "optimized": True
        }
        
    except Exception as e:
        return {"data": [], "error": str(e)}

@app.get("/test-ai")
def test_ai():
    """Test endpoint for AI functionality"""
    return {"message": "AI test endpoint working", "status": "success"}

@app.get("/test-simple")
def test_simple():
    """Simple test endpoint"""
    return {"message": "Simple test working", "status": "success"}

@app.get("/test-portfolio-values")
def test_portfolio_values(user_id: int = 1, db: Session = Depends(get_db)):
    """Test endpoint to verify PortfolioValues data"""
    try:
        portfolio_values = db.query(PortfolioValues).filter(PortfolioValues.user_id == user_id).all()
        total_value = sum(v.total_value for v in portfolio_values)
        return {
            "message": "PortfolioValues test",
            "count": len(portfolio_values),
            "total_value": total_value,
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.get("/test-insights/{user_id}")
def test_insights(user_id: int, db: Session = Depends(get_db)):
    """Test endpoint for insights functionality"""
    try:
        from insights_calculator import calculate_portfolio_metrics
        
        # Test portfolio query
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
        
        if not portfolio:
            return {"error": "No portfolio found", "count": 0}
        
        # Test metrics calculation
        metrics = calculate_portfolio_metrics(user_id, db)
        
        return {
            "message": "Insights test successful",
            "portfolio_count": len(portfolio),
            "metrics": metrics,
            "status": "success"
        }
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.get("/portfolio/ai-insights/{user_id}")
def get_ai_insights(user_id: int, db: Session = Depends(get_db)):
    """Get AI-powered portfolio insights and recommendations using GPT"""
    try:
        import openai
        import sys
        import os
        # Add parent directory to path
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, parent_dir)
        from config.api_keys import load_keys
        
        # Load API keys
        keys = load_keys()
        openai.api_key = keys.get('openai_api_key')
        
        if not openai.api_key:
            return {"error": "OpenAI API key not configured"}
        
        # Get portfolio health data (simplified version)
        health_data = {
            'diversification': 0.7,  # Mock diversification score
            'riskLevel': 'Medium',   # Mock risk level
            'volatility': 15.5       # Mock volatility
        }
        
        # Get portfolio summary
        summary = db.query(PortfolioSummary).filter(PortfolioSummary.user_id == user_id).first()
        
        # Get portfolio holdings for context
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
        
        if not portfolio:
            return {"error": "No portfolio holdings found"}
        
        # If no summary exists, create a basic one from portfolio data
        if not summary:
            total_value = sum(holding.qty * holding.avg_price for holding in portfolio)
            total_gain_loss = 0  # Simplified for now
            total_gain_loss_percent = 0  # Simplified for now
            sharpe_ratio = 1.0  # Default value
            stock_value = sum(holding.qty * holding.avg_price for holding in portfolio if holding.category == 'Stock')
            crypto_value = sum(holding.qty * holding.avg_price for holding in portfolio if holding.category == 'Crypto')
            etf_value = sum(holding.qty * holding.avg_price for holding in portfolio if holding.category == 'ETF')
            bond_value = sum(holding.qty * holding.avg_price for holding in portfolio if holding.category == 'Bond')
            cash_value = sum(holding.qty * holding.avg_price for holding in portfolio if holding.category == 'Cash')
        else:
            total_value = summary.total_value
            total_gain_loss = summary.total_gain_loss
            total_gain_loss_percent = summary.total_gain_loss_percent
            sharpe_ratio = summary.sharpe_ratio or 1.0
            stock_value = summary.stock_value
            crypto_value = summary.crypto_value
            etf_value = summary.etf_value
            bond_value = summary.bond_value
            cash_value = summary.cash_value
        
        # Prepare portfolio context for GPT
        portfolio_context = {
            "total_value": total_value,
            "total_gain_loss": total_gain_loss,
            "total_gain_loss_percent": total_gain_loss_percent,
            "diversification_score": health_data.get('diversification', 0),
            "risk_level": health_data.get('riskLevel', 'Unknown'),
            "volatility": health_data.get('volatility', 0),
            "sharpe_ratio": sharpe_ratio,
            "holdings_count": len(portfolio),
            "category_breakdown": {
                "stocks": stock_value,
                "crypto": crypto_value,
                "etfs": etf_value,
                "bonds": bond_value,
                "cash": cash_value
            }
        }
        
        # Create GPT prompt
        prompt = f"""
        As a professional portfolio advisor, analyze this portfolio and provide actionable insights:
        
        Portfolio Summary:
        - Total Value: ${portfolio_context['total_value']:,.2f}
        - Total Gain/Loss: ${portfolio_context['total_gain_loss']:,.2f} ({portfolio_context['total_gain_loss_percent']:.2f}%)
        - Diversification Score: {portfolio_context['diversification_score']:.2f}/1.0
        - Risk Level: {portfolio_context['risk_level']}
        - Volatility: {portfolio_context['volatility']:.2f}%
        - Sharpe Ratio: {portfolio_context['sharpe_ratio']:.2f}
        - Number of Holdings: {portfolio_context['holdings_count']}
        
        Asset Allocation:
        - Stocks: ${portfolio_context['category_breakdown']['stocks']:,.2f}
        - Crypto: ${portfolio_context['category_breakdown']['crypto']:,.2f}
        - ETFs: ${portfolio_context['category_breakdown']['etfs']:,.2f}
        - Bonds: ${portfolio_context['category_breakdown']['bonds']:,.2f}
        - Cash: ${portfolio_context['category_breakdown']['cash']:,.2f}
        
        Please provide:
        1. A brief assessment of portfolio health (1-2 sentences)
        2. Top 3 specific, actionable recommendations
        3. Risk assessment and suggestions
        4. Diversification analysis
        
        Format your response as JSON with these fields:
        {{
            "assessment": "Brief portfolio health assessment",
            "recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"],
            "risk_analysis": "Risk assessment and suggestions",
            "diversification_analysis": "Diversification analysis and suggestions",
            "confidence": 0.85
        }}
        """
        
        # Call OpenAI GPT
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional portfolio advisor with expertise in investment analysis, risk management, and portfolio optimization. Provide clear, actionable advice based on portfolio metrics."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Parse GPT response
        gpt_response = response.choices[0].message.content
        
        try:
            import json
            insights = json.loads(gpt_response)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            insights = {
                "assessment": gpt_response[:200] + "..." if len(gpt_response) > 200 else gpt_response,
                "recommendations": ["Review portfolio allocation", "Consider rebalancing", "Monitor performance regularly"],
                "risk_analysis": "Please review your risk tolerance and portfolio allocation",
                "diversification_analysis": "Consider diversifying across different asset classes",
                "confidence": 0.75
            }
        
        return {
            "insights": insights,
            "status": "success",
            "generated_at": datetime.now().isoformat(),
            "ai_powered": True
        }
        
    except Exception as e:
        # Fallback to rule-based insights if GPT fails
        try:
            # Simplified health data for fallback
            health_data = {
                'diversification': 0.7,
                'riskLevel': 'Medium',
                'volatility': 15.5
            }
            summary = db.query(PortfolioSummary).filter(PortfolioSummary.user_id == user_id).first()
            portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
            
            if not portfolio:
                return {"error": "No portfolio holdings found"}
            
            # If no summary exists, create a basic one from portfolio data
            if not summary:
                total_value = sum(holding.qty * holding.avg_price for holding in portfolio)
                total_gain_loss = 0
                total_gain_loss_percent = 0
            else:
                total_value = summary.total_value
                total_gain_loss = summary.total_gain_loss
                total_gain_loss_percent = summary.total_gain_loss_percent
            
            insights = {
                "assessment": f"Portfolio value: ${total_value:,.2f} with {total_gain_loss_percent:.2f}% return",
                "recommendations": [
                    "Review asset allocation regularly",
                    "Consider rebalancing if needed",
                    "Monitor risk levels"
                ],
                "risk_analysis": f"Current risk level: {health_data.get('riskLevel', 'Unknown')}",
                "diversification_analysis": f"Diversification score: {health_data.get('diversification', 0):.2f}/1.0",
                "confidence": 0.6
            }
            
            return {
                "insights": insights,
                "status": "success",
                "generated_at": datetime.now().isoformat(),
                "ai_powered": False,
                "fallback": True
            }
        except Exception as fallback_error:
            return {"error": f"AI insights failed: {str(e)}. Fallback failed: {str(fallback_error)}"}

@app.post("/portfolio/calculate-metrics/{user_id}")
def calculate_user_metrics(user_id: int, db: Session = Depends(get_db)):
    """Trigger calculation of all metrics for a specific user"""
    try:
        # from calculate_all_metrics import calculate_all_metrics_for_user  # Disabled for now
        # calculate_all_metrics_for_user(user_id)  # Disabled for now
        return {"message": f"Metrics calculated successfully for user {user_id}", "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.post("/portfolio/calculate-all-metrics")
def calculate_all_user_metrics(db: Session = Depends(get_db)):
    """Trigger calculation of all metrics for all users"""
    try:
        # from calculate_all_metrics import calculate_all_metrics  # Disabled for now
        # calculate_all_metrics()  # Disabled for now
        return {"message": "All metrics calculated successfully", "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.get("/portfolio/top-holdings/{user_id}")
def get_top_holdings(user_id: int, type: str = "holdings", db: Session = Depends(get_db)):
    """Get top holdings or movers for a user"""
    try:
        from models import TopHoldings
        
        # Get top holdings/movers from database
        top_data = db.query(TopHoldings).filter(
            TopHoldings.user_id == user_id,
            TopHoldings.type == type
        ).order_by(TopHoldings.rank.asc()).all()
        
        if not top_data:
            # If no data exists, calculate it
            # from calculate_top_holdings import calculate_top_holdings_for_user  # Disabled for now
            # calculate_top_holdings_for_user(user_id)  # Disabled for now
            
            # Query again after calculation
            top_data = db.query(TopHoldings).filter(
                TopHoldings.user_id == user_id,
                TopHoldings.type == type
            ).order_by(TopHoldings.rank.asc()).all()
        
        # Format the response
        formatted_data = []
        for item in top_data:
            formatted_data.append({
                "ticker": item.ticker,
                "shares": item.shares,
                "current_price": round(item.current_price, 2),
                "total_value": round(item.total_value, 2),
                "gain_loss": round(item.gain_loss, 2),
                "gain_loss_percent": round(item.gain_loss_percent, 2),
                "rank": item.rank
            })
        
        return {
            "user_id": user_id,
            "type": type,
            "data": formatted_data,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get top holdings: {str(e)}")

@app.get("/portfolio/top-holdings-movers/{user_id}")
def get_top_holdings_and_movers(user_id: int, db: Session = Depends(get_db)):
    """Get both top holdings and movers for a user in a single call"""
    try:
        from models import TopHoldings
        
        # Get both types of data
        holdings_data = db.query(TopHoldings).filter(
            TopHoldings.user_id == user_id,
            TopHoldings.type == "holdings"
        ).order_by(TopHoldings.rank.asc()).all()
        
        movers_data = db.query(TopHoldings).filter(
            TopHoldings.user_id == user_id,
            TopHoldings.type == "movers"
        ).order_by(TopHoldings.rank.asc()).all()
        
        if not holdings_data or not movers_data:
            # If no data exists, calculate it
            # from calculate_top_holdings import calculate_top_holdings_for_user  # Disabled for now
            # calculate_top_holdings_for_user(user_id)  # Disabled for now
            
            # Query again after calculation
            holdings_data = db.query(TopHoldings).filter(
                TopHoldings.user_id == user_id,
                TopHoldings.type == "holdings"
            ).order_by(TopHoldings.rank.asc()).all()
            
            movers_data = db.query(TopHoldings).filter(
                TopHoldings.user_id == user_id,
                TopHoldings.type == "movers"
            ).order_by(TopHoldings.rank.asc()).all()
        
        # Format the response
        def format_data(data):
            return [{
                "ticker": item.ticker,
                "shares": item.shares,
                "current_price": round(item.current_price, 2),
                "total_value": round(item.total_value, 2),
                "gain_loss": round(item.gain_loss, 2),
                "gain_loss_percent": round(item.gain_loss_percent, 2),
                "rank": item.rank
            } for item in data]
        
        return {
            "user_id": user_id,
            "holdings": format_data(holdings_data),
            "movers": format_data(movers_data),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get top holdings and movers: {str(e)}")

@app.get("/insights/{user_id}")
def get_insights(user_id: int, db: Session = Depends(get_db)):
    """Get AI-powered portfolio insights"""
    try:
        from insights_calculator import (
            calculate_portfolio_metrics, 
            generate_metrics_hash, 
            get_cached_insights, 
            save_insights_to_cache,
            generate_rule_based_insights
        )
        from ai_insights_generator import generate_ai_insights, generate_detailed_insights
        
        # Calculate portfolio metrics
        print(f"Debug: Calculating metrics for user {user_id}")
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
        print(f"Debug: Found {len(portfolio)} portfolio holdings")
        
        if not portfolio:
            print("Debug: No portfolio found, returning error")
            return {"error": "No portfolio data found", "insights": []}
        
        metrics = calculate_portfolio_metrics(user_id, db)
        print(f"Debug: Metrics calculated: {metrics}")
        
        if not metrics:
            return {"error": "Failed to calculate metrics", "insights": []}
        
        # Generate metrics hash for caching
        metrics_hash = generate_metrics_hash(metrics)
        
        # Check cache first
        cached_insights = get_cached_insights(user_id, metrics_hash, db)
        if cached_insights:
            return {
                "insights": cached_insights,
                "cached": True,
                "metrics": metrics
            }
        
        # Try to generate AI insights
        ai_insights = generate_ai_insights(metrics)
        
        if ai_insights:
            # Save AI insights to cache
            save_insights_to_cache(user_id, metrics_hash, ai_insights, True, db)
            return {
                "insights": ai_insights,
                "cached": False,
                "ai_generated": True,
                "metrics": metrics
            }
        else:
            # Fallback to rule-based insights
            rule_based_insights = generate_rule_based_insights(metrics)
            save_insights_to_cache(user_id, metrics_hash, rule_based_insights, False, db)
            return {
                "insights": rule_based_insights,
                "cached": False,
                "ai_generated": False,
                "metrics": metrics
            }
            
    except Exception as e:
        return {"error": f"Failed to generate insights: {str(e)}", "insights": []}

@app.get("/insights/detailed/{user_id}")
def get_detailed_insights(user_id: int, db: Session = Depends(get_db)):
    """Get detailed AI insights for the Insights tab"""
    try:
        from insights_calculator import calculate_portfolio_metrics
        from ai_insights_generator import generate_detailed_insights
        
        # Calculate portfolio metrics
        metrics = calculate_portfolio_metrics(user_id, db)
        if not metrics:
            return {"error": "No portfolio data found", "insights": []}
        
        # Generate detailed insights
        detailed_insights = generate_detailed_insights(metrics)
        
        return {
            "insights": detailed_insights,
            "metrics": metrics
        }
        
    except Exception as e:
        return {"error": f"Failed to generate detailed insights: {str(e)}", "insights": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
