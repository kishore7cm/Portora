"""
Real-time portfolio calculator using actual market data
Fetches yesterday's closing prices and calculates current portfolio value
"""

import yfinance as yf
import requests
from datetime import date, datetime, timedelta
from typing import Dict, List, Any
import json

# Your actual portfolio holdings (update these with your real positions)
ACTUAL_PORTFOLIO = {
    # Stocks
    "AAPL": {"units": 100.0, "type": "stock"},
    "AMZN": {"units": 200.0, "type": "stock"},
    "MSFT": {"units": 80.0, "type": "stock"},
    "NVDA": {"units": 150.0, "type": "stock"},
    "TSLA": {"units": 100.0, "type": "stock"},
    "GOOGL": {"units": 120.0, "type": "stock"},
    "META": {"units": 90.0, "type": "stock"},
    
    # ETFs/Bonds
    "BND": {"units": 200.0, "type": "bond_etf"},
    "VCIT": {"units": 150.0, "type": "bond_etf"},
    "VOO": {"units": 80.0, "type": "etf"},
    
    # Crypto (using yesterday's prices)
    "BTC-USD": {"units": 0.5, "type": "crypto"},
    "ETH-USD": {"units": 15.0, "type": "crypto"},
    
    # Cash
    "CASH": {"units": 15000.0, "type": "cash"}
}

def get_yesterday_date():
    """Get yesterday's date (for market data)"""
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # If yesterday was weekend, get Friday's data
    while yesterday.weekday() > 4:  # 5=Saturday, 6=Sunday
        yesterday = yesterday - timedelta(days=1)
    
    return yesterday

def fetch_stock_prices(tickers: List[str]) -> Dict[str, float]:
    """Fetch yesterday's closing prices for stocks using yfinance"""
    prices = {}
    yesterday = get_yesterday_date()
    
    print(f"📈 Fetching stock prices for {yesterday}...")
    
    try:
        # Fetch data for all tickers at once
        tickers_str = " ".join(tickers)
        data = yf.download(tickers_str, start=yesterday, end=yesterday + timedelta(days=1), progress=False)
        
        if len(tickers) == 1:
            # Single ticker
            ticker = tickers[0]
            if not data.empty and 'Close' in data.columns:
                prices[ticker] = float(data['Close'].iloc[-1])
                print(f"  {ticker}: ${prices[ticker]:.2f}")
            else:
                print(f"  ❌ No data for {ticker}")
        else:
            # Multiple tickers
            if not data.empty and 'Close' in data.columns:
                for ticker in tickers:
                    try:
                        if ticker in data['Close'].columns:
                            price = float(data['Close'][ticker].iloc[-1])
                            prices[ticker] = price
                            print(f"  {ticker}: ${price:.2f}")
                        else:
                            print(f"  ❌ No data for {ticker}")
                    except Exception as e:
                        print(f"  ❌ Error getting {ticker}: {e}")
    
    except Exception as e:
        print(f"❌ Error fetching stock data: {e}")
        # Fallback to individual requests
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="2d")
                if not hist.empty:
                    prices[ticker] = float(hist['Close'].iloc[-1])
                    print(f"  {ticker}: ${prices[ticker]:.2f}")
            except Exception as e:
                print(f"  ❌ Error getting {ticker}: {e}")
    
    return prices

def fetch_crypto_prices(tickers: List[str]) -> Dict[str, float]:
    """Fetch current crypto prices (crypto markets are 24/7)"""
    prices = {}
    
    print(f"₿ Fetching crypto prices...")
    
    for ticker in tickers:
        try:
            crypto = yf.Ticker(ticker)
            hist = crypto.history(period="1d")
            if not hist.empty:
                prices[ticker] = float(hist['Close'].iloc[-1])
                print(f"  {ticker}: ${prices[ticker]:.2f}")
        except Exception as e:
            print(f"  ❌ Error getting {ticker}: {e}")
    
    return prices

def calculate_real_portfolio_value() -> Dict[str, Any]:
    """Calculate portfolio value using real market data"""
    
    print("🚀 Calculating real portfolio value...")
    print(f"📅 Using market data from: {get_yesterday_date()}")
    
    # Separate tickers by type
    stock_tickers = []
    crypto_tickers = []
    positions = []
    
    for ticker, info in ACTUAL_PORTFOLIO.items():
        if info["type"] in ["stock", "bond_etf", "etf"]:
            stock_tickers.append(ticker)
        elif info["type"] == "crypto":
            crypto_tickers.append(ticker)
    
    # Fetch prices
    stock_prices = fetch_stock_prices(stock_tickers) if stock_tickers else {}
    crypto_prices = fetch_crypto_prices(crypto_tickers) if crypto_tickers else {}
    
    # Combine all prices
    all_prices = {**stock_prices, **crypto_prices}
    
    # Calculate positions
    total_value = 0.0
    cash_value = 0.0
    
    for ticker, info in ACTUAL_PORTFOLIO.items():
        units = info["units"]
        
        if info["type"] == "cash":
            cash_value = units
            total_value += units
            positions.append({
                "ticker": ticker,
                "units": units,
                "price": 1.0,
                "position_val": units,
                "type": info["type"]
            })
        elif ticker in all_prices:
            price = all_prices[ticker]
            position_val = units * price
            total_value += position_val
            
            positions.append({
                "ticker": ticker,
                "units": units,
                "price": price,
                "position_val": position_val,
                "type": info["type"]
            })
            
            print(f"💰 {ticker}: {units} units × ${price:.2f} = ${position_val:,.2f}")
        else:
            print(f"⚠️ Missing price for {ticker}, excluding from calculation")
    
    # Calculate allocation
    stock_value = sum(pos["position_val"] for pos in positions if pos["type"] in ["stock"])
    etf_value = sum(pos["position_val"] for pos in positions if pos["type"] in ["etf", "bond_etf"])
    crypto_value = sum(pos["position_val"] for pos in positions if pos["type"] == "crypto")
    
    allocation = {
        "stock": (stock_value / total_value * 100) if total_value > 0 else 0,
        "bond": (etf_value / total_value * 100) if total_value > 0 else 0,
        "crypto": (crypto_value / total_value * 100) if total_value > 0 else 0,
        "cash": (cash_value / total_value * 100) if total_value > 0 else 0
    }
    
    # Calculate returns
    starting_value = 325850.92
    total_gain_loss = total_value - starting_value
    return_pct = (total_gain_loss / starting_value * 100) if starting_value > 0 else 0
    
    # Get top holdings
    top_holdings = sorted(
        [pos for pos in positions if pos["type"] != "cash"],
        key=lambda x: x["position_val"],
        reverse=True
    )[:3]
    
    result = {
        "date": get_yesterday_date().isoformat(),
        "total_value": total_value,
        "cash": cash_value,
        "starting_value": starting_value,
        "total_gain_loss": total_gain_loss,
        "return_pct": return_pct,
        "positions": positions,
        "allocation": allocation,
        "top_holdings": top_holdings,
        "summary": {
            "stock_value": stock_value,
            "etf_bond_value": etf_value,
            "crypto_value": crypto_value,
            "cash_value": cash_value
        }
    }
    
    print(f"\n📊 Portfolio Summary:")
    print(f"  💰 Total Value: ${total_value:,.2f}")
    print(f"  📈 Starting Value: ${starting_value:,.2f}")
    print(f"  💹 Gain/Loss: ${total_gain_loss:,.2f} ({return_pct:+.2f}%)")
    print(f"  📊 Allocation: Stock {allocation['stock']:.1f}%, Bond/ETF {allocation['bond']:.1f}%, Crypto {allocation['crypto']:.1f}%, Cash {allocation['cash']:.1f}%")
    
    return result

if __name__ == "__main__":
    # Calculate and display real portfolio value
    portfolio_data = calculate_real_portfolio_value()
    
    # Save to JSON file
    with open("real_portfolio_data.json", "w") as f:
        json.dump(portfolio_data, f, indent=2)
    
    print(f"\n✅ Real portfolio data saved to real_portfolio_data.json")
    print(f"🎯 Your current portfolio value: ${portfolio_data['total_value']:,.2f}")
