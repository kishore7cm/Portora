from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database import engine, get_db, Base
from models import User, Login, Portfolio, Transaction, MarketData, HistoricalData, PortfolioSummary, PortfolioProjections, PortfolioPerformance, PortfolioChartData
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
        
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
        
        # Convert to the expected format with current market data
        portfolio_data = []
        total_value = 0
        total_gain_loss = 0
        
        # Get current prices for each ticker (get most recent price for each)
        price_dict = {}
        for stock in portfolio:
            latest_price = db.query(HistoricalData).filter(
                HistoricalData.ticker == stock.ticker
            ).order_by(HistoricalData.date.desc()).first()
            
            if latest_price:
                price_dict[stock.ticker] = latest_price.close_price
            else:
                price_dict[stock.ticker] = stock.avg_price
        
        for stock in portfolio:
            # Get current price from the pre-fetched data
            current_price = price_dict.get(stock.ticker, stock.avg_price)
            current_value = stock.shares * current_price
            cost_basis = stock.shares * stock.avg_price
            gain_loss = current_value - cost_basis
            gain_loss_percent = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
            
            portfolio_data.append({
                "Ticker": stock.ticker,
                "Qty": stock.shares,
                "Avg_Price": stock.avg_price,
                "Current_Price": current_price,
                "Total_Value": current_value,
                "Cost_Basis": cost_basis,
                "Gain_Loss": gain_loss,
                "Gain_Loss_Percent": gain_loss_percent,
                "Category": "Stock"
            })
            
            total_value += current_value
            total_gain_loss += gain_loss
        
        # Calculate portfolio metrics
        total_cost_basis = sum(item["Cost_Basis"] for item in portfolio_data)
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
        from calculate_portfolio_health import calculate_portfolio_health_for_user
        
        # Calculate real portfolio health
        health_data = calculate_portfolio_health_for_user(user_id)
        
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
            from calculate_portfolio_performance import calculate_portfolio_performance_for_user
            calculate_portfolio_performance_for_user(user_id)
            
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

@app.post("/portfolio/calculate-metrics/{user_id}")
def calculate_user_metrics(user_id: int, db: Session = Depends(get_db)):
    """Trigger calculation of all metrics for a specific user"""
    try:
        from calculate_all_metrics import calculate_all_metrics_for_user
        calculate_all_metrics_for_user(user_id)
        return {"message": f"Metrics calculated successfully for user {user_id}", "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.post("/portfolio/calculate-all-metrics")
def calculate_all_user_metrics(db: Session = Depends(get_db)):
    """Trigger calculation of all metrics for all users"""
    try:
        from calculate_all_metrics import calculate_all_metrics
        calculate_all_metrics()
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
            from calculate_top_holdings import calculate_top_holdings_for_user
            calculate_top_holdings_for_user(user_id)
            
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
            from calculate_top_holdings import calculate_top_holdings_for_user
            calculate_top_holdings_for_user(user_id)
            
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
