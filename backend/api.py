import sys
print(">>> RUNNING API FILE:", __file__, file=sys.stderr)
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import jwt, datetime
import pandas as pd
import os

# Add the parent directory to Python path to import analysis modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from portora_main import run_analysis, run_sp500_analysis
    from historical_data import historical_manager
except ImportError as e:
    print(f"Warning: Could not import analysis modules: {e}")
    run_analysis = None
    run_sp500_analysis = None
    historical_manager = None

SECRET_KEY = "change_me_super_secret"
ALGORITHM = "HS256"
COOKIE_NAME = "portora_session"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- existing endpoints ---
@app.get("/")
def root():
    return {"ok": True}

@app.get("/health")
def health_check():
    """Health check endpoint for deployment platforms"""
    return {
        "status": "healthy",
        "service": "Portora Portfolio Advisor API",
        "version": "1.0.0"
    }

@app.get("/portfolio")
def get_portfolio():
    if run_analysis is None or historical_manager is None:
        return {"error": "Analysis module not available"}
    
    try:
        portfolio_df, summary_df = run_analysis()
        
        # Get all tickers from portfolio
        tickers = portfolio_df['Ticker'].unique().tolist()
        
        # Check if we have historical data, if not download it
        print(f"Checking historical data for {len(tickers)} tickers...")
        
        # For now, just calculate with existing data
        # In production, you'd want to check if data exists first
        historical_data = historical_manager.calculate_portfolio_historical_values(portfolio_df)
        
        # Store current portfolio snapshot
        current_total = portfolio_df['Curr $'].sum()
        historical_manager.store_portfolio_snapshot(portfolio_df, current_total)
        
        return {
            "portfolio": portfolio_df.to_dict('records'),
            "summary": summary_df.to_dict('records'),
            "historical": historical_data
        }
    except Exception as e:
        print(f"Error in portfolio endpoint: {str(e)}")
        return {"error": f"Failed to analyze portfolio: {str(e)}"}

# Historical data calculation is now handled by historical_data.py

@app.get("/sp500")
def get_sp500():
    if run_sp500_analysis is None:
        return {"error": "Analysis module not available"}
    
    try:
        sp500_df = run_sp500_analysis()
        return {"sp500": sp500_df.to_dict('records')}
    except Exception as e:
        return {"error": f"Failed to analyze S&P 500: {str(e)}"}

@app.get("/historical-data/download")
def download_historical_data():
    """Download 1 year of historical data for all portfolio tickers"""
    if run_analysis is None or historical_manager is None:
        return {"error": "Analysis module not available"}
    
    try:
        portfolio_df, _ = run_analysis()
        tickers = portfolio_df['Ticker'].unique().tolist()
        
        print(f"Starting historical data download for {len(tickers)} tickers...")
        successful, failed = historical_manager.download_historical_data(tickers, days_back=365)
        
        return {
            "status": "success",
            "message": f"Downloaded historical data for {successful} tickers, {failed} failed",
            "successful": successful,
            "failed": failed,
            "tickers": tickers
        }
    except Exception as e:
        return {"error": f"Failed to download historical data: {str(e)}"}

@app.get("/historical-data/update-daily")
def update_daily_data():
    """Update daily data for all portfolio tickers"""
    if run_analysis is None or historical_manager is None:
        return {"error": "Analysis module not available"}
    
    try:
        portfolio_df, _ = run_analysis()
        tickers = portfolio_df['Ticker'].unique().tolist()
        
        print(f"Updating daily data for {len(tickers)} tickers...")
        historical_manager.update_daily_data(tickers)
        
        return {
            "status": "success",
            "message": f"Daily data updated for {len(tickers)} tickers",
            "tickers": tickers
        }
    except Exception as e:
        return {"error": f"Failed to update daily data: {str(e)}"}

@app.get("/historical-data/snapshots")
def get_portfolio_snapshots():
    """Get recent portfolio snapshots"""
    if historical_manager is None:
        return {"error": "Historical data manager not available"}
    
    try:
        snapshots = historical_manager.get_portfolio_snapshots(days_back=30)
        return {"snapshots": snapshots}
    except Exception as e:
        return {"error": f"Failed to get snapshots: {str(e)}"}

@app.get("/projections/portfolio")
def get_portfolio_projections():
    """Get portfolio projections based on historical data analysis"""
    if run_analysis is None or historical_manager is None:
        return {"error": "Analysis module not available"}
    
    try:
        portfolio_df, _ = run_analysis()
        projection_summary = historical_manager.get_projection_summary(portfolio_df)
        
        if projection_summary is None:
            return {"error": "Unable to generate projections - insufficient historical data"}
        
        return {
            "status": "success",
            "projections": projection_summary
        }
    except Exception as e:
        return {"error": f"Failed to generate projections: {str(e)}"}

@app.get("/projections/asset/{ticker}")
def get_asset_projections(ticker: str):
    """Get projections for a specific asset"""
    if historical_manager is None:
        return {"error": "Historical data manager not available"}
    
    try:
        projections = historical_manager.generate_projections(ticker, days_ahead=30)
        
        if projections is None:
            return {"error": f"Unable to generate projections for {ticker} - insufficient data"}
        
        return {
            "status": "success",
            "ticker": ticker,
            "projections": projections
        }
    except Exception as e:
        return {"error": f"Failed to generate projections for {ticker}: {str(e)}"}

@app.get("/analysis/trend/{ticker}")
def get_asset_trend_analysis(ticker: str):
    """Get trend analysis for a specific asset"""
    if historical_manager is None:
        return {"error": "Historical data manager not available"}
    
    try:
        trend_analysis = historical_manager.calculate_trend_analysis(ticker)
        
        if trend_analysis is None:
            return {"error": f"Unable to analyze trends for {ticker} - insufficient data"}
        
        return {
            "status": "success",
            "ticker": ticker,
            "trend_analysis": trend_analysis
        }
    except Exception as e:
        return {"error": f"Failed to analyze trends for {ticker}: {str(e)}"}

# --- Portfolio Health endpoint ---
@app.get("/portfolio-health-test")
async def get_portfolio_health_test():
    """Test endpoint for portfolio health"""
    return {"status": "success", "health": 85, "test": "working"}

@app.get("/portfolio-health")
async def get_portfolio_health():
    """Get portfolio health score, drivers, drift, and badges"""
    # Return stub data for now
    return {
        "status": "success",
        "health": 78.5,
        "drivers": {
            "diversification": 82.3,
            "concentration": 75.0,
            "cashDrag": 90.0,
            "volProxy": 65.2
        },
        "driftAsset": {
            "stocks": {
                "current": 44.9,
                "target": 40.0,
                "delta": 4.9
            },
            "crypto": {
                "current": 12.6,
                "target": 10.0,
                "delta": 2.6
            },
            "bonds": {
                "current": 12.0,
                "target": 20.0,
                "delta": -8.0
            },
            "currencies": {
                "current": 30.5,
                "target": 30.0,
                "delta": 0.5
            }
        },
        "badges": ["Balanced", "Well Diversified", "Cash Optimized"],
        "byAsset": {
            "stocks": {"current": 44.9, "target": 40.0},
            "crypto": {"current": 12.6, "target": 10.0},
            "bonds": {"current": 12.0, "target": 20.0},
            "currencies": {"current": 30.5, "target": 30.0}
        },
        "bySector": {
            "Technology": 25.3,
            "Healthcare": 15.2,
            "Financial": 12.8,
            "Consumer": 18.7,
            "Industrial": 8.9,
            "Other": 19.1
        }
    }

def calculate_portfolio_health(portfolio, summary):
    """Calculate portfolio health metrics"""
    
    # Initialize health metrics
    health_metrics = {
        'health': 0,
        'drivers': {
            'diversification': 0,
            'concentration': 0,
            'cashDrag': 0,
            'volProxy': 0
        },
        'driftAsset': {},
        'badges': [],
        'byAsset': {},
        'bySector': {}
    }
    
    try:
        if not portfolio:
            return health_metrics
        
        # Convert portfolio to DataFrame for easier calculations
        df = pd.DataFrame(portfolio)
        logger.info(f"DataFrame created with {len(df)} rows")
        
        # Calculate total portfolio value
        total_value = df['Curr $'].sum()
        if total_value == 0:
            return health_metrics
        
        # Calculate weights
        df['weight'] = df['Curr $'] / total_value
        
        # 1. Diversification Score (HHI-based, 0-100)
        hhi = (df['weight'] ** 2).sum()
        diversification_score = max(0, 100 - (hhi * 100))  # Lower HHI = higher score
        health_metrics['drivers']['diversification'] = round(diversification_score, 1)
        
        # 2. Concentration Score (penalize if top 3 > 35%)
        top_3_weight = df.nlargest(3, 'weight')['weight'].sum()
        concentration_score = max(0, 100 - ((top_3_weight - 0.35) * 200)) if top_3_weight > 0.35 else 100
        health_metrics['drivers']['concentration'] = round(concentration_score, 1)
        
        # 3. Cash Drag Score (penalize if cash > 10%)
        cash_weight = df[df['Category'].str.contains('Cash|Money Market', case=False, na=False)]['weight'].sum()
        cash_drag_score = max(0, 100 - ((cash_weight - 0.10) * 500)) if cash_weight > 0.10 else 100
        health_metrics['drivers']['cashDrag'] = round(cash_drag_score, 1)
        
        # 4. Volatility Proxy Score (based on equity allocation and beta)
        equity_weight = df[df['Category'].str.contains('Stock|Equity', case=False, na=False)]['weight'].sum()
        avg_beta = df[df['Category'].str.contains('Stock|Equity', case=False, na=False)]['Beta'].mean()
        if pd.isna(avg_beta):
            avg_beta = 1.0
        
        # Higher equity allocation and beta = higher risk = lower score
        vol_proxy_score = max(0, 100 - (equity_weight * avg_beta * 50))
        health_metrics['drivers']['volProxy'] = round(vol_proxy_score, 1)
        
        # Calculate overall health score (weighted average)
        health_score = (
            diversification_score * 0.30 +
            concentration_score * 0.25 +
            vol_proxy_score * 0.25 +
            cash_drag_score * 0.20
        )
        health_metrics['health'] = round(health_score, 1)
        
        # Calculate asset class drift
        asset_classes = df.groupby('Category').agg({
            'weight': 'sum',
            'Tgt %': 'first'
        }).reset_index()
        
        drift_asset = {}
        for _, row in asset_classes.iterrows():
            category = row['Category']
            current_pct = row['weight'] * 100
            target_pct = row['Tgt %'] if not pd.isna(row['Tgt %']) else 0
            drift_pct = current_pct - target_pct
            
            drift_asset[category] = {
                'current': round(current_pct, 1),
                'target': round(target_pct, 1),
                'delta': round(drift_pct, 1)
            }
        
        health_metrics['driftAsset'] = drift_asset
        
        # Generate badges based on thresholds
        badges = []
        if health_score >= 80:
            badges.append("Balanced")
        if health_score >= 90:
            badges.append("Excellent")
        if diversification_score >= 80:
            badges.append("Well Diversified")
        if concentration_score >= 80:
            badges.append("Risk Tamer")
        if cash_drag_score >= 80:
            badges.append("Cash Optimized")
        if vol_proxy_score >= 80:
            badges.append("Risk Managed")
        if health_score < 50:
            badges.append("Needs Attention")
        if health_score < 30:
            badges.append("High Risk")
        
        health_metrics['badges'] = badges
        
        # Prepare byAsset and bySector data for future charts
        health_metrics['byAsset'] = {
            category: {
                'current': round(row['weight'] * 100, 1),
                'target': round(row['Tgt %'] if not pd.isna(row['Tgt %']) else 0, 1)
            }
            for _, row in asset_classes.iterrows()
        }
        
        # Group by sector (if available)
        if 'Sector' in df.columns:
            sectors = df.groupby('Sector')['weight'].sum().reset_index()
            health_metrics['bySector'] = {
                row['Sector']: round(row['weight'] * 100, 1)
                for _, row in sectors.iterrows()
            }
        
        logger.info(f"Health metrics calculated successfully: {health_metrics['health']}")
        return health_metrics
        
    except Exception as e:
        logger.error(f"Error in calculate_portfolio_health: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return health_metrics

# --- User Management ---
from user_management import user_manager
from enhanced_user_management import enhanced_user_manager
from bot_management import bot_manager

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: str = None
    last_name: str = None

class UserProfileUpdate(BaseModel):
    first_name: str = None
    last_name: str = None
    email: str = None

@app.post("/register")
async def register_user(payload: RegisterRequest):
    """Register a new user"""
    result = user_manager.register_user(
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name
    )
    return result

@app.post("/login")
async def login_user(payload: LoginRequest, response: Response):
    """Authenticate user and create session"""
    email_normalized = payload.email.strip().lower()
    password_normalized = payload.password.strip()

    # Dev fallback: universal demo credentials
    if email_normalized == "demo@portora.com" and password_normalized == "123456":
        # Map demo credentials to a default demo user (conservative persona)
        try:
            demo_result = enhanced_user_manager.authenticate_user("conservative@example.com", "password123")
            if not demo_result or not demo_result.get("success"):
                # Ensure user exists
                created = enhanced_user_manager.register_user(
                    "conservative@example.com", "password123", "Conservative", "Investor"
                )
                if created and created.get("success"):
                    demo_result = enhanced_user_manager.authenticate_user("conservative@example.com", "password123")
            if demo_result and demo_result.get("success"):
                user = demo_result["user"]
                token = jwt.encode(
                    {"sub": user["email"], "user_id": user["id"], "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)},
                    SECRET_KEY, algorithm=ALGORITHM
                )
                # Set cookie for localhost so Next.js can send it back
                response.set_cookie(key=COOKIE_NAME, value=token, httponly=True, samesite="lax", domain="localhost")
                return {"status": "success", "user": user}
        except Exception:
            pass

    # Normal authentication path
    result = enhanced_user_manager.authenticate_user(email_normalized, password_normalized)
    if result and result.get("success"):
        user = result["user"]
        token = jwt.encode(
            {"sub": user["email"], "user_id": user["id"], "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)},
            SECRET_KEY, algorithm=ALGORITHM
        )
        response.set_cookie(key=COOKIE_NAME, value=token, httponly=True, samesite="lax", domain="localhost")
        return {"status": "success", "user": user}

    return {"status": "failure", "message": "Invalid credentials"}

@app.get("/me")
async def get_me(request: Request):
    """Get current user information"""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return {"status": "unauthenticated"}
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = decoded.get("user_id")
        if user_id:
            user = enhanced_user_manager.get_user_by_id(user_id)
            if user:
                return {"status": "authenticated", "user": user}
        return {"status": "unauthenticated", "message": "User not found"}
    except jwt.ExpiredSignatureError:
        return {"status": "unauthenticated", "message": "Session expired"}
    except jwt.InvalidTokenError:
        return {"status": "unauthenticated", "message": "Invalid session"}

@app.put("/profile")
async def update_profile(request: Request, payload: UserProfileUpdate):
    """Update user profile"""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return {"status": "unauthenticated"}
    
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = decoded.get("user_id")
        if not user_id:
            return {"status": "error", "message": "Invalid token"}
        
        # Update profile
        update_data = {k: v for k, v in payload.dict().items() if v is not None}
        success = user_manager.update_user_profile(user_id, **update_data)
        
        if success:
            return {"status": "success", "message": "Profile updated successfully"}
        else:
            return {"status": "error", "message": "Failed to update profile"}
            
    except jwt.ExpiredSignatureError:
        return {"status": "unauthenticated", "message": "Session expired"}
    except jwt.InvalidTokenError:
        return {"status": "unauthenticated", "message": "Invalid session"}

@app.get("/preferences")
async def get_preferences(request: Request):
    """Get user preferences"""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return {"status": "unauthenticated"}
    
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = decoded.get("user_id")
        if not user_id:
            return {"status": "error", "message": "Invalid token"}
        
        preferences = user_manager.get_all_user_preferences(user_id)
        return {"status": "success", "preferences": preferences}
        
    except jwt.ExpiredSignatureError:
        return {"status": "unauthenticated", "message": "Session expired"}
    except jwt.InvalidTokenError:
        return {"status": "unauthenticated", "message": "Invalid session"}

@app.post("/preferences")
async def set_preference(request: Request, key: str, value: str):
    """Set a user preference"""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return {"status": "unauthenticated"}
    
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = decoded.get("user_id")
        if not user_id:
            return {"status": "error", "message": "Invalid token"}
        
        success = user_manager.set_user_preference(user_id, key, value)
        if success:
            return {"status": "success", "message": "Preference set successfully"}
        else:
            return {"status": "error", "message": "Failed to set preference"}
            
    except jwt.ExpiredSignatureError:
        return {"status": "unauthenticated", "message": "Session expired"}
    except jwt.InvalidTokenError:
        return {"status": "unauthenticated", "message": "Invalid session"}

@app.post("/logout")
async def logout(response: Response):
    """Logout user"""
    response.delete_cookie(COOKIE_NAME)
    return {"status": "logged_out"}

# --- Portfolio Management ---
@app.get("/portfolios")
async def get_user_portfolios(request: Request):
    """Get all portfolios for the current user"""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return {"status": "unauthenticated"}
    
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = decoded.get("user_id")
        
        if not user_id:
            return {"status": "error", "message": "User not found"}
        portfolios = enhanced_user_manager.get_user_portfolios(user_id)
        
        return {"status": "success", "portfolios": portfolios}
        
    except jwt.ExpiredSignatureError:
        return {"status": "unauthenticated", "message": "Session expired"}
    except jwt.InvalidTokenError:
        return {"status": "unauthenticated", "message": "Invalid session"}
    except Exception as e:
        logger.error(f"Error getting portfolios: {e}")
        return {"status": "error", "message": "Failed to get portfolios"}

@app.get("/portfolios/{portfolio_id}/holdings")
async def get_portfolio_holdings(portfolio_id: int, request: Request):
    """Get holdings for a specific portfolio"""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return {"status": "unauthenticated"}
    
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = decoded.get("user_id")
        
        if not user_id:
            return {"status": "error", "message": "User not found"}
        user_portfolios = enhanced_user_manager.get_user_portfolios(user_id)
        
        # Check if portfolio belongs to user
        portfolio_exists = any(p["id"] == portfolio_id for p in user_portfolios)
        if not portfolio_exists:
            return {"status": "error", "message": "Portfolio not found"}
        
        holdings = enhanced_user_manager.get_portfolio_holdings(portfolio_id)
        return {"status": "success", "holdings": holdings}
        
    except jwt.ExpiredSignatureError:
        return {"status": "unauthenticated", "message": "Session expired"}
    except jwt.InvalidTokenError:
        return {"status": "unauthenticated", "message": "Invalid session"}
    except Exception as e:
        logger.error(f"Error getting portfolio holdings: {e}")
        return {"status": "error", "message": "Failed to get holdings"}

# --- Bot Management ---
@app.get("/bots")
async def get_user_bots(request: Request):
    """Get all bots for the current user"""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return {"status": "unauthenticated"}
    
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = decoded["sub"]
        
        # Get user ID
        user = enhanced_user_manager.authenticate_user(user_email, "dummy")
        if not user["success"]:
            return {"status": "error", "message": "User not found"}
        
        user_id = user["user"]["id"]
        bots = enhanced_user_manager.get_user_bots(user_id)
        
        return {"status": "success", "bots": bots}
        
    except jwt.ExpiredSignatureError:
        return {"status": "unauthenticated", "message": "Session expired"}
    except jwt.InvalidTokenError:
        return {"status": "unauthenticated", "message": "Invalid session"}
    except Exception as e:
        logger.error(f"Error getting bots: {e}")
        return {"status": "error", "message": "Failed to get bots"}

@app.get("/bots/types")
async def get_bot_types():
    """Get available bot types"""
    try:
        bot_types = bot_manager.get_available_bot_types()
        return {"status": "success", "bot_types": bot_types}
    except Exception as e:
        logger.error(f"Error getting bot types: {e}")
        return {"status": "error", "message": "Failed to get bot types"}

@app.get("/bots/{bot_type}/config")
async def get_bot_config_template(bot_type: str):
    """Get configuration template for a bot type"""
    try:
        config = bot_manager.get_bot_config_template(bot_type)
        return {"status": "success", "config": config}
    except Exception as e:
        logger.error(f"Error getting bot config: {e}")
        return {"status": "error", "message": "Failed to get bot config"}

class CreateBotRequest(BaseModel):
    name: str
    bot_type: str
    config: Dict[str, Any] = {}

@app.post("/bots")
async def create_bot(request: CreateBotRequest, http_request: Request):
    """Create a new trading bot"""
    token = http_request.cookies.get(COOKIE_NAME)
    if not token:
        return {"status": "unauthenticated"}
    
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = decoded["sub"]
        
        # Get user ID
        user = enhanced_user_manager.authenticate_user(user_email, "dummy")
        if not user["success"]:
            return {"status": "error", "message": "User not found"}
        
        user_id = user["user"]["id"]
        result = bot_manager.create_bot(user_id, request.name, request.bot_type, request.config)
        
        return result
        
    except jwt.ExpiredSignatureError:
        return {"status": "unauthenticated", "message": "Session expired"}
    except jwt.InvalidTokenError:
        return {"status": "unauthenticated", "message": "Invalid session"}
    except Exception as e:
        logger.error(f"Error creating bot: {e}")
        return {"status": "error", "message": "Failed to create bot"}

@app.post("/bots/{bot_id}/start")
async def start_bot(bot_id: int, request: Request):
    """Start a bot"""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return {"status": "unauthenticated"}
    
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = decoded["sub"]
        
        # Verify user owns this bot
        user = enhanced_user_manager.authenticate_user(user_email, "dummy")
        if not user["success"]:
            return {"status": "error", "message": "User not found"}
        
        user_id = user["user"]["id"]
        user_bots = enhanced_user_manager.get_user_bots(user_id)
        
        # Check if bot belongs to user
        bot_exists = any(b["id"] == bot_id for b in user_bots)
        if not bot_exists:
            return {"status": "error", "message": "Bot not found"}
        
        result = bot_manager.start_bot(bot_id)
        return result
        
    except jwt.ExpiredSignatureError:
        return {"status": "unauthenticated", "message": "Session expired"}
    except jwt.InvalidTokenError:
        return {"status": "unauthenticated", "message": "Invalid session"}
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        return {"status": "error", "message": "Failed to start bot"}

@app.post("/bots/{bot_id}/stop")
async def stop_bot(bot_id: int, request: Request):
    """Stop a bot"""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return {"status": "unauthenticated"}
    
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = decoded["sub"]
        
        # Verify user owns this bot
        user = enhanced_user_manager.authenticate_user(user_email, "dummy")
        if not user["success"]:
            return {"status": "error", "message": "User not found"}
        
        user_id = user["user"]["id"]
        user_bots = enhanced_user_manager.get_user_bots(user_id)
        
        # Check if bot belongs to user
        bot_exists = any(b["id"] == bot_id for b in user_bots)
        if not bot_exists:
            return {"status": "error", "message": "Bot not found"}
        
        result = bot_manager.stop_bot(bot_id)
        return result
        
    except jwt.ExpiredSignatureError:
        return {"status": "unauthenticated", "message": "Session expired"}
    except jwt.InvalidTokenError:
        return {"status": "unauthenticated", "message": "Invalid session"}
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
        return {"status": "error", "message": "Failed to stop bot"}

@app.get("/bots/{bot_id}/performance")
async def get_bot_performance(bot_id: int, request: Request):
    """Get bot performance data"""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return {"status": "unauthenticated"}
    
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = decoded["sub"]
        
        # Verify user owns this bot
        user = enhanced_user_manager.authenticate_user(user_email, "dummy")
        if not user["success"]:
            return {"status": "error", "message": "User not found"}
        
        user_id = user["user"]["id"]
        user_bots = enhanced_user_manager.get_user_bots(user_id)
        
        # Check if bot belongs to user
        bot_exists = any(b["id"] == bot_id for b in user_bots)
        if not bot_exists:
            return {"status": "error", "message": "Bot not found"}
        
        result = bot_manager.get_bot_performance(bot_id)
        return result
        
    except jwt.ExpiredSignatureError:
        return {"status": "unauthenticated", "message": "Session expired"}
    except jwt.InvalidTokenError:
        return {"status": "unauthenticated", "message": "Invalid session"}
    except Exception as e:
        logger.error(f"Error getting bot performance: {e}")
        return {"status": "error", "message": "Failed to get bot performance"}

# --- Comparison & Benchmarking ---
@app.get("/comparison")
async def get_comparison_data(request: Request):
    """Get comparison data; demo-friendly: if unauthenticated, use demo portfolio holdings."""
    user_holdings = []
    token = request.cookies.get(COOKIE_NAME)
    if token:
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = decoded.get("user_id")
            if user_id:
                user_portfolios = enhanced_user_manager.get_user_portfolios(user_id)
                if user_portfolios:
                    conservative_portfolio = next((p for p in user_portfolios if "Conservative" in p["name"]), None)
                    portfolio_id = conservative_portfolio["id"] if conservative_portfolio else user_portfolios[0]["id"]
                    user_holdings = enhanced_user_manager.get_portfolio_holdings(portfolio_id)
        except Exception:
            pass

    # Fallback to demo user's primary portfolio holdings if empty
    if not user_holdings:
        try:
            demo_auth = enhanced_user_manager.authenticate_user("conservative@example.com", "password123")
            if demo_auth and demo_auth.get("success"):
                demo_user_id = demo_auth["user"]["id"]
                primary_id = enhanced_user_manager.get_primary_portfolio_id(demo_user_id)
                if primary_id:
                    user_holdings = enhanced_user_manager.get_portfolio_holdings(primary_id)
        except Exception:
            user_holdings = []

    # Calculate user metrics (stubbed for now)
    user_metrics = calculate_user_metrics(user_holdings)

    # Get community data (stubbed)
    community_metrics = get_community_metrics()

    # Stubbed benchmark data
    comparison_data = {
        "user": user_metrics,
        "sp500": {
            "one_year_return": 12.5,
            "volatility": 18.2,
            "dividend_yield": 1.8,
            "allocation": {
                "equity": 100.0,
                "bond": 0.0,
                "cash": 0.0
            }
        },
        "model6040": {
            "one_year_return": 10.8,
            "volatility": 12.5,
            "dividend_yield": 2.1,
            "allocation": {
                "equity": 60.0,
                "bond": 40.0,
                "cash": 0.0
            }
        },
        "allWeather": {
            "one_year_return": 8.9,
            "volatility": 8.7,
            "dividend_yield": 2.3,
            "allocation": {
                "equity": 30.0,
                "bond": 55.0,
                "cash": 15.0
            }
        },
        "community": community_metrics
    }

    return {"status": "success", "data": comparison_data}

def calculate_user_metrics(holdings):
    """Calculate user portfolio metrics (stubbed)"""
    if not holdings:
        return {
            "one_year_return": 0.0,
            "volatility": 0.0,
            "dividend_yield": 0.0,
            "allocation": {
                "equity": 0.0,
                "bond": 0.0,
                "cash": 0.0
            }
        }
    
    # Use realistic stubbed prices for holdings
    stubbed_prices = {
        "VTI": 250.0, "VEA": 45.0, "VWO": 42.0, "BND": 75.0, "GLD": 180.0,
        "QQQ": 380.0, "ARKK": 45.0, "TSLA": 250.0, "NVDA": 450.0, "BTC-USD": 65000.0,
        "AAPL": 175.0, "MSFT": 350.0, "GOOGL": 140.0, "AMZN": 150.0, "META": 300.0,
        "SCHD": 80.0, "VYM": 90.0, "JNJ": 160.0, "KO": 60.0, "PG": 150.0
    }
    
    # Calculate total value using stubbed prices
    total_value = 0
    for holding in holdings:
        symbol = holding.get("symbol", "")
        quantity = holding.get("quantity", 0)
        price = stubbed_prices.get(symbol, 100.0)  # Default price if not found
        total_value += quantity * price
    
    # Calculate allocation by asset class
    equity_value = 0
    bond_value = 0
    cash_value = 0
    
    for holding in holdings:
        symbol = holding.get("symbol", "")
        quantity = holding.get("quantity", 0)
        asset_class = holding.get("asset_class", "")
        price = stubbed_prices.get(symbol, 100.0)
        value = quantity * price
        
        if asset_class in ["equity", "crypto"]:
            equity_value += value
        elif asset_class == "bond":
            bond_value += value
        elif asset_class == "cash":
            cash_value += value
    
    # Stubbed performance metrics - use realistic data based on holdings
    if total_value > 0:
        # Calculate allocation based on actual holdings
        equity_pct = (equity_value / total_value * 100)
        bond_pct = (bond_value / total_value * 100)
        cash_pct = (cash_value / total_value * 100)
        
        # Generate performance metrics based on allocation
        if equity_pct > 80:
            # High equity allocation - higher returns, higher volatility
            one_year_return = 18.5
            volatility = 25.2
            dividend_yield = 1.2
        elif equity_pct > 60:
            # Balanced allocation
            one_year_return = 15.2
            volatility = 22.1
            dividend_yield = 1.5
        elif equity_pct > 40:
            # Conservative allocation
            one_year_return = 12.8
            volatility = 18.5
            dividend_yield = 2.1
        else:
            # Very conservative allocation
            one_year_return = 8.9
            volatility = 12.3
            dividend_yield = 2.8
    else:
        # No holdings - use default values
        one_year_return = 15.2
        volatility = 22.1
        dividend_yield = 1.5
        equity_pct = 85.0
        bond_pct = 12.0
        cash_pct = 3.0
    
    return {
        "one_year_return": one_year_return,
        "volatility": volatility,
        "dividend_yield": dividend_yield,
        "allocation": {
            "equity": equity_pct if total_value > 0 else 85.0,
            "bond": bond_pct if total_value > 0 else 12.0,
            "cash": cash_pct if total_value > 0 else 3.0
        }
    }

def get_community_metrics():
    """Get community average metrics (stubbed)"""
    return {
        "median_one_year_return": 11.8,
        "median_volatility": 16.5,
        "average_dividend_yield": 1.9,
        "average_allocation": {
            "equity": 75.0,
            "bond": 20.0,
            "cash": 5.0
        }
    }

# Onboarding endpoints
@app.get("/onboarding/status")
async def get_onboarding_status():
    """Get onboarding status for current user"""
    try:
        # For demo purposes, check if user is logged in via localStorage
        # In production, this would use proper JWT authentication
        return {
            "has_seen_onboarding": False,  # Default for demo
            "show_onboarding": True
        }
    except Exception as e:
        logger.error(f"Error getting onboarding status: {e}")
        return {"error": "Failed to get onboarding status"}

@app.post("/onboarding/complete")
async def complete_onboarding():
    """Mark onboarding as complete for current user"""
    try:
        # For demo purposes, this would update the user's preferences
        # In production, this would use proper JWT authentication
        return {
            "success": True,
            "message": "Onboarding completed successfully"
        }
    except Exception as e:
        logger.error(f"Error completing onboarding: {e}")
        return {"error": "Failed to complete onboarding"}

# Alerts endpoints
@app.get("/alerts")
async def get_alerts(unread_only: bool = False, limit: int = 50):
    """Get alerts for current user"""
    try:
        # For demo purposes, return sample alerts
        # In production, this would use proper JWT authentication
        sample_alerts = [
            {
                "id": 1,
                "type": "portfolio",
                "title": "Portfolio Health Alert",
                "message": "Your portfolio health score has improved to 85! Great diversification.",
                "is_read": False,
                "priority": "medium",
                "created_at": "2024-01-15T10:30:00Z",
                "expires_at": None,
                "metadata": {"health_score": 85}
            },
            {
                "id": 2,
                "type": "market",
                "title": "Market Update",
                "message": "S&P 500 is up 2.3% today. Consider reviewing your positions.",
                "is_read": False,
                "priority": "low",
                "created_at": "2024-01-15T09:15:00Z",
                "expires_at": "2024-01-16T09:15:00Z",
                "metadata": {"market_change": 2.3}
            },
            {
                "id": 3,
                "type": "bot",
                "title": "Trading Bot Activity",
                "message": "DCA Bot executed a buy order for AAPL at $150.25",
                "is_read": True,
                "priority": "high",
                "created_at": "2024-01-15T08:45:00Z",
                "expires_at": None,
                "metadata": {"symbol": "AAPL", "action": "buy", "price": 150.25}
            }
        ]
        
        if unread_only:
            sample_alerts = [alert for alert in sample_alerts if not alert["is_read"]]
        
        return sample_alerts[:limit]
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return {"error": "Failed to get alerts"}

@app.get("/alerts/count")
async def get_alert_count():
    """Get unread alert count for current user"""
    try:
        # For demo purposes, return sample count
        return {"unread_count": 2}
    except Exception as e:
        logger.error(f"Error getting alert count: {e}")
        return {"error": "Failed to get alert count"}

@app.post("/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: int):
    """Mark an alert as read"""
    try:
        # For demo purposes, just return success
        # In production, this would update the database
        return {"success": True, "message": "Alert marked as read"}
    except Exception as e:
        logger.error(f"Error marking alert as read: {e}")
        return {"error": "Failed to mark alert as read"}

@app.post("/alerts/read-all")
async def mark_all_alerts_read():
    """Mark all alerts as read for current user"""
    try:
        # For demo purposes, just return success
        # In production, this would update the database
        return {"success": True, "message": "All alerts marked as read"}
    except Exception as e:
        logger.error(f"Error marking all alerts as read: {e}")
        return {"error": "Failed to mark all alerts as read"}

# Community Benchmark endpoints
@app.get("/community/comparison")
async def get_community_comparison():
    """Get community benchmark comparison data"""
    try:
        # Sample community data for demo
        community_data = {
            "community_stats": {
                "total_users": 15420,
                "active_users_30d": 8934,
                "average_portfolio_value": 125000,
                "median_portfolio_value": 85000,
                "top_performers_count": 2341
            },
            "performance_benchmarks": {
                "community_median_1y_return": 12.4,
                "community_median_volatility": 18.2,
                "community_median_sharpe_ratio": 0.68,
                "community_median_max_drawdown": -15.3,
                "top_quartile_1y_return": 24.7,
                "bottom_quartile_1y_return": 2.1
            },
            "allocation_benchmarks": {
                "community_avg_equity_allocation": 72.5,
                "community_avg_bond_allocation": 18.3,
                "community_avg_cash_allocation": 9.2,
                "community_avg_crypto_allocation": 3.8,
                "community_avg_international_allocation": 15.7
            },
            "sector_performance": {
                "technology": {"avg_allocation": 28.4, "avg_return": 18.2},
                "healthcare": {"avg_allocation": 12.1, "avg_return": 14.7},
                "financials": {"avg_allocation": 15.8, "avg_return": 11.3},
                "consumer_discretionary": {"avg_allocation": 8.9, "avg_return": 16.1},
                "industrials": {"avg_allocation": 9.2, "avg_return": 9.8},
                "energy": {"avg_allocation": 4.1, "avg_return": 22.4},
                "utilities": {"avg_allocation": 3.2, "avg_return": 6.5},
                "materials": {"avg_allocation": 2.8, "avg_return": 13.2}
            },
            "risk_profiles": {
                "conservative": {"count": 2341, "avg_return": 8.2, "avg_volatility": 12.1},
                "moderate": {"count": 6789, "avg_return": 12.4, "avg_volatility": 16.8},
                "aggressive": {"count": 4567, "avg_return": 18.7, "avg_volatility": 24.3},
                "very_aggressive": {"count": 1723, "avg_return": 25.1, "avg_volatility": 31.2}
            },
            "popular_strategies": [
                {"name": "Dollar Cost Averaging", "users": 8934, "avg_return": 13.2},
                {"name": "Value Investing", "users": 4567, "avg_return": 11.8},
                {"name": "Growth Investing", "users": 6789, "avg_return": 16.4},
                {"name": "Dividend Focus", "users": 3456, "avg_return": 9.7},
                {"name": "Index Fund Strategy", "users": 5678, "avg_return": 12.1},
                {"name": "Sector Rotation", "users": 1234, "avg_return": 14.8}
            ],
            "recent_trends": {
                "most_bought_stocks": [
                    {"symbol": "AAPL", "buys": 1234, "avg_price": 150.25},
                    {"symbol": "MSFT", "buys": 987, "avg_price": 280.45},
                    {"symbol": "GOOGL", "buys": 876, "avg_price": 95.67},
                    {"symbol": "TSLA", "buys": 765, "avg_price": 245.32},
                    {"symbol": "NVDA", "buys": 654, "avg_price": 425.18}
                ],
                "most_sold_stocks": [
                    {"symbol": "META", "sells": 543, "avg_price": 285.67},
                    {"symbol": "NFLX", "sells": 432, "avg_price": 345.21},
                    {"symbol": "AMZN", "sells": 321, "avg_price": 125.43},
                    {"symbol": "BABA", "sells": 210, "avg_price": 78.90},
                    {"symbol": "PYPL", "sells": 198, "avg_price": 65.34}
                ]
            }
        }
        
        return community_data
        
    except Exception as e:
        logger.error(f"Error getting community comparison: {e}")
        return {"error": "Failed to get community comparison data"}
