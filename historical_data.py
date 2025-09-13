import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import time
import logging
import numpy as np
from scipy import stats
import requests
from alpaca_trade_api.rest import REST
from alpaca_trade_api import TimeFrame
from config.api_keys import load_keys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HistoricalDataManager:
    def __init__(self, db_path="historical_data.db"):
        self.db_path = db_path
        # Use hardcoded keys since .env file is blocked
        self.alpaca = REST(
            "AKLE4VA1CEHBBHXNXCHZ", 
            "SQiQpXxbecEhS2p5z9l2olfhA135AuMktWUu12pm", 
            "https://api.alpaca.markets"
        )
        self._initialize_db()
        
        # Rate limiting settings
        self.requests_per_minute = 200  # Alpaca's limit
        self.request_count = 0
        self.last_reset = datetime.now()

    def _initialize_db(self):
        """Initialize SQLite database with proper schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table for stock prices
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_prices (
                ticker TEXT NOT NULL,
                date TEXT NOT NULL,
                close REAL,
                volume INTEGER,
                PRIMARY KEY (ticker, date)
            )
        """)
        
        # Create table for crypto prices
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crypto_prices (
                ticker TEXT NOT NULL,
                date TEXT NOT NULL,
                close REAL,
                volume INTEGER,
                PRIMARY KEY (ticker, date)
            )
        """)
        
        # Create table for portfolio snapshots
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                date TEXT NOT NULL PRIMARY KEY,
                total_value REAL,
                portfolio_composition TEXT -- Store as JSON string
            )
        """)
        
        # Create table for projections
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projections (
                ticker TEXT NOT NULL,
                projection_date TEXT NOT NULL,
                projected_value REAL,
                confidence_score REAL,
                volatility REAL,
                trend_direction TEXT,
                PRIMARY KEY (ticker, projection_date)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_prices_date ON stock_prices(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_crypto_prices_date ON crypto_prices(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_date ON portfolio_snapshots(date)")
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")

    def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        now = datetime.now()
        if (now - self.last_reset).seconds >= 60:
            self.request_count = 0
            self.last_reset = now
        
        if self.request_count >= self.requests_per_minute:
            sleep_time = 60 - (now - self.last_reset).seconds
            if sleep_time > 0:
                logger.info(f"Rate limit reached. Sleeping for {sleep_time} seconds...")
                time.sleep(sleep_time)
                self.request_count = 0
                self.last_reset = datetime.now()
        
        self.request_count += 1

    def _fetch_twelve_crypto_data(self, ticker, start_date, end_date):
        """Fetch crypto data from Twelve Data API"""
        try:
            # Convert BTC-USD to BTC/USD format for Twelve API
            crypto_symbol = ticker.replace("-USD", "/USD")
            
            # Twelve Data API endpoint
            url = "https://api.twelvedata.com/time_series"
            params = {
                "symbol": crypto_symbol,
                "interval": "1day",
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "apikey": "fb22b25e80884e8b89ef865a3ddb9802"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'values' not in data:
                logger.error(f"No data returned from Twelve API for {ticker}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(data['values'])
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime')
            df = df.sort_index()
            
            # Convert string values to float
            for col in ['open', 'high', 'low', 'close', 'volume']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching crypto data from Twelve API for {ticker}: {e}")
            return pd.DataFrame()

    def download_historical_data(self, tickers, days_back=365):
        """Download 1 year of historical data for all tickers"""
        logger.info(f"Starting historical data download for {len(tickers)} symbols")
        
        # Use older data to avoid SIP subscription limitations
        end_date = datetime.now() - timedelta(days=30)
        start_date = end_date - timedelta(days=days_back)
        
        successful_downloads = 0
        failed_downloads = 0
        
        for i, ticker in enumerate(tickers, 1):
            try:
                self._check_rate_limit()
                logger.info(f"Downloading {ticker} ({i}/{len(tickers)})")
                
                # Determine if it's crypto or stock
                if ticker.endswith("-USD"):
                    # Crypto - use Twelve Data API
                    try:
                        data = self._fetch_twelve_crypto_data(ticker, start_date, end_date)
                        table_name = "crypto_prices"
                    except Exception as e:
                        logger.error(f"Error downloading crypto {ticker}: {e}")
                        failed_downloads += 1
                        continue
                else:
                    # Stock
                    try:
                        data = self.alpaca.get_bars(
                            ticker,
                            TimeFrame.Day,
                            start=start_date.strftime('%Y-%m-%d'),
                            end=end_date.strftime('%Y-%m-%d')
                        ).df
                        table_name = "stock_prices"
                    except Exception as e:
                        logger.error(f"Error downloading stock {ticker}: {e}")
                        failed_downloads += 1
                        continue
                
                if not data.empty:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    for date, row in data.iterrows():
                        date_str = date.strftime('%Y-%m-%d')
                        close_price = row['close']
                        volume = row.get('volume', 0)
                        
                        cursor.execute(f"""
                            INSERT OR REPLACE INTO {table_name} (ticker, date, close, volume)
                            VALUES (?, ?, ?, ?)
                        """, (ticker, date_str, close_price, volume))
                    
                    conn.commit()
                    conn.close()
                    successful_downloads += 1
                else:
                    logger.warning(f"No data received for {ticker}")
                    failed_downloads += 1
                    
            except Exception as e:
                logger.error(f"Error downloading {ticker}: {e}")
                failed_downloads += 1
        
        logger.info(f"Download complete: {successful_downloads} successful, {failed_downloads} failed")
        return successful_downloads, failed_downloads

    def update_daily_data(self, tickers):
        """Update data for the last few days (for daily updates)"""
        logger.info(f"Updating daily data for {len(tickers)} symbols")
        
        # Use older data to avoid SIP subscription limitations
        end_date = datetime.now() - timedelta(days=30)
        start_date = end_date - timedelta(days=7)  # Last week
        
        for ticker in tickers:
            try:
                self._check_rate_limit()
                
                if ticker.endswith("-USD"):
                    try:
                        data = self._fetch_twelve_crypto_data(ticker, start_date, end_date)
                        table_name = "crypto_prices"
                    except:
                        continue
                else:
                    try:
                        data = self.alpaca.get_bars(
                            ticker,
                            TimeFrame.Day,
                            start=start_date.strftime('%Y-%m-%d'),
                            end=end_date.strftime('%Y-%m-%d')
                        ).df
                        table_name = "stock_prices"
                    except:
                        continue
                
                if not data.empty:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    for date, row in data.iterrows():
                        date_str = date.strftime('%Y-%m-%d')
                        close_price = row['close']
                        volume = row.get('volume', 0)
                        
                        cursor.execute(f"""
                            INSERT OR REPLACE INTO {table_name} (ticker, date, close, volume)
                            VALUES (?, ?, ?, ?)
                        """, (ticker, date_str, close_price, volume))
                    
                    conn.commit()
                    conn.close()
                    
            except Exception as e:
                logger.error(f"Error updating {ticker}: {e}")

    def get_historical_price(self, ticker, date_str):
        """Get historical price for a specific ticker and date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Try stock prices first, then crypto
        cursor.execute("""
            SELECT close FROM stock_prices
            WHERE ticker = ? AND date <= ?
            ORDER BY date DESC
            LIMIT 1
        """, (ticker, date_str))
        
        result = cursor.fetchone()
        if result:
            conn.close()
            return result[0]
        
        # Try crypto prices
        cursor.execute("""
            SELECT close FROM crypto_prices
            WHERE ticker = ? AND date <= ?
            ORDER BY date DESC
            LIMIT 1
        """, (ticker, date_str))
        
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def get_historical_prices(self, ticker, days_back=30):
        """Get historical prices for a ticker over the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Try stock prices first
        cursor.execute("""
            SELECT date, close FROM stock_prices
            WHERE ticker = ?
            ORDER BY date DESC
            LIMIT ?
        """, (ticker, days_back))
        
        results = cursor.fetchall()
        if results:
            conn.close()
            return [(row[0], row[1]) for row in results]
        
        # Try crypto prices
        cursor.execute("""
            SELECT date, close FROM crypto_prices
            WHERE ticker = ?
            ORDER BY date DESC
            LIMIT ?
        """, (ticker, days_back))
        
        results = cursor.fetchall()
        conn.close()
        return [(row[0], row[1]) for row in results] if results else []

    def calculate_trend_analysis(self, ticker, days_back=90):
        """Calculate trend analysis for a ticker"""
        prices = self.get_historical_prices(ticker, days_back)
        if len(prices) < 10:
            return None
        
        # Convert to numpy arrays
        dates = [datetime.strptime(p[0], '%Y-%m-%d') for p in prices]
        values = [p[1] for p in prices]
        
        # Calculate linear regression
        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        # Calculate volatility (standard deviation of returns)
        returns = np.diff(values) / values[:-1]
        volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
        
        # Calculate momentum indicators
        sma_20 = np.mean(values[-20:]) if len(values) >= 20 else np.mean(values)
        sma_50 = np.mean(values[-50:]) if len(values) >= 50 else np.mean(values)
        
        # Determine trend direction
        if slope > 0.01:
            trend_direction = "bullish"
        elif slope < -0.01:
            trend_direction = "bearish"
        else:
            trend_direction = "sideways"
        
        return {
            "slope": slope,
            "r_squared": r_value ** 2,
            "volatility": volatility,
            "sma_20": sma_20,
            "sma_50": sma_50,
            "trend_direction": trend_direction,
            "current_price": values[-1],
            "data_points": len(values)
        }

    def generate_projections(self, ticker, days_ahead=30):
        """Generate price projections for a ticker"""
        trend_analysis = self.calculate_trend_analysis(ticker)
        if not trend_analysis:
            return None
        
        # Get recent prices for projection
        recent_prices = self.get_historical_prices(ticker, 30)
        if not recent_prices:
            return None
        
        current_price = recent_prices[0][1]
        volatility = trend_analysis["volatility"]
        slope = trend_analysis["slope"]
        
        # Generate projections using Monte Carlo simulation
        projections = []
        confidence_scores = []
        
        # Perform Monte Carlo simulation
        num_simulations = 1000
        daily_volatility = volatility / np.sqrt(252)  # Convert annual to daily volatility
        
        # Calculate daily trend from slope (slope is per data point, not per day)
        if len(recent_prices) > 1:
            daily_trend = slope / len(recent_prices)  # Convert slope to daily trend
        else:
            daily_trend = 0
        
        # Cap the daily trend to reasonable bounds (-5% to +5% per day)
        daily_trend = max(-0.05, min(0.05, daily_trend))
        
        for day in range(1, days_ahead + 1):
            # Monte Carlo simulation for this day
            simulated_prices = []
            
            for _ in range(num_simulations):
                # Geometric Brownian Motion: S_t = S_0 * exp((μ - σ²/2) * t + σ * W_t)
                # Where μ is drift (daily_trend), σ is volatility, W_t is random walk
                
                # Calculate cumulative drift and volatility
                drift = daily_trend * day
                random_walk = np.random.normal(0, daily_volatility * np.sqrt(day))
                
                # Apply geometric Brownian motion
                simulated_price = current_price * np.exp(drift + random_walk)
                simulated_prices.append(simulated_price)
            
            # Use median of simulations as projection
            projected_price = np.median(simulated_prices)
            projections.append(projected_price)
            
            # Calculate confidence score based on R-squared and volatility
            confidence = max(0.1, min(0.9, trend_analysis["r_squared"] - (volatility * 0.01)))
            confidence_scores.append(confidence)
        
        # Store projections in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for i, (projected_price, confidence) in enumerate(zip(projections, confidence_scores)):
            projection_date = (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d')
            
            cursor.execute("""
                INSERT OR REPLACE INTO projections 
                (ticker, projection_date, projected_value, confidence_score, volatility, trend_direction)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ticker, projection_date, projected_price, confidence, volatility, trend_analysis["trend_direction"]))
        
        conn.commit()
        conn.close()
        
        return {
            "ticker": ticker,
            "current_price": current_price,
            "projections": projections,
            "confidence_scores": confidence_scores,
            "trend_analysis": trend_analysis
        }

    def calculate_portfolio_historical_values(self, portfolio_df, months_back=6):
        """Calculate historical portfolio values using real stored data"""
        historical_points = []
        today = datetime.now()
        
        for i in range(months_back - 1, -1, -1):
            target_date = today - timedelta(days=i * (365/12))
            target_date_str = target_date.strftime('%Y-%m-%d')
            month_name = target_date.strftime('%b')
            
            total_value_for_month = 0
            
            for _, row in portfolio_df.iterrows():
                ticker = row['Ticker']
                qty = row['Qty']
                
                historical_price = self.get_historical_price(ticker, target_date_str)
                
                if historical_price is not None:
                    total_value_for_month += qty * historical_price
                else:
                    logger.warning(f"No historical price for {ticker} on {target_date_str}")
                    total_value_for_month += row['Curr $']
                    
            historical_points.append({
                "month": month_name,
                "value": round(total_value_for_month, 2)
            })
        
        return historical_points

    def calculate_portfolio_projections(self, portfolio_df, days_ahead=90):
        """Calculate portfolio projections based on individual asset projections"""
        portfolio_projections = []
        
        for _, row in portfolio_df.iterrows():
            ticker = row['Ticker']
            qty = row['Qty']
            
            # Generate projections for this ticker
            ticker_projections = self.generate_projections(ticker, days_ahead)
            if ticker_projections:
                portfolio_projections.append({
                    "ticker": ticker,
                    "qty": qty,
                    "projections": ticker_projections
                })
        
        # Aggregate portfolio projections
        daily_portfolio_values = []
        for day in range(days_ahead):
            total_value = 0
            total_confidence = 0
            valid_projections = 0
            
            for asset in portfolio_projections:
                if day < len(asset["projections"]["projections"]):
                    projected_price = asset["projections"]["projections"][day]
                    confidence = asset["projections"]["confidence_scores"][day]
                    
                    total_value += asset["qty"] * projected_price
                    total_confidence += confidence
                    valid_projections += 1
            
            if valid_projections > 0:
                avg_confidence = total_confidence / valid_projections
                daily_portfolio_values.append({
                    "day": day + 1,
                    "projected_value": round(total_value, 2),
                    "confidence": round(avg_confidence, 3)
                })
        
        return daily_portfolio_values

    def store_portfolio_snapshot(self, portfolio_df, total_value):
        """Store current portfolio snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        portfolio_composition_json = portfolio_df.to_json(orient='records')
        
        cursor.execute("""
            INSERT OR REPLACE INTO portfolio_snapshots (date, total_value, portfolio_composition)
            VALUES (?, ?, ?)
        """, (date_str, total_value, portfolio_composition_json))
        
        conn.commit()
        conn.close()

    def get_portfolio_snapshots(self, days_back=30):
        """Get recent portfolio snapshots"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT date, total_value FROM portfolio_snapshots
            WHERE date >= ?
            ORDER BY date DESC
        """, (start_date,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{"date": row[0], "value": row[1]} for row in results]

    def get_projection_summary(self, portfolio_df):
        """Get a summary of portfolio projections"""
        projections = self.calculate_portfolio_projections(portfolio_df, 90)
        
        if not projections:
            return None
        
        # Calculate summary statistics
        current_value = portfolio_df['Curr $'].sum()
        projected_30_day = projections[29]["projected_value"] if len(projections) > 29 else current_value
        projected_90_day = projections[-1]["projected_value"] if projections else current_value
        
        # Calculate expected returns
        return_30_day = ((projected_30_day - current_value) / current_value) * 100 if current_value > 0 else 0
        return_90_day = ((projected_90_day - current_value) / current_value) * 100 if current_value > 0 else 0
        
        # Calculate average confidence
        avg_confidence = np.mean([p["confidence"] for p in projections]) if projections else 0
        
        return {
            "current_value": current_value,
            "projected_30_day": projected_30_day,
            "projected_90_day": projected_90_day,
            "expected_return_30_day": round(return_30_day, 2),
            "expected_return_90_day": round(return_90_day, 2),
            "average_confidence": round(avg_confidence, 3),
            "projections": projections
        }

# Create global instance
historical_manager = HistoricalDataManager()
logger.info("Historical data manager initialized successfully")