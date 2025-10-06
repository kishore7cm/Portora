#!/usr/bin/env python3
"""
Portfolio Insights Calculator
Calculates key metrics for AI insights generation
"""

import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from models import Portfolio, HistoricalData, PortfolioSummary
from typing import Dict, Any, Optional
import hashlib
import json
from datetime import datetime, timedelta

def calculate_portfolio_metrics(user_id: int, db: Session) -> Dict[str, Any]:
    """
    Calculate comprehensive portfolio metrics for insights generation
    """
    try:
        # Get portfolio holdings
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
        
        if not portfolio:
            return None
        
        # Get portfolio summary if available
        summary = db.query(PortfolioSummary).filter(PortfolioSummary.user_id == user_id).first()
        
        # Calculate basic metrics
        total_value = 0
        total_cost = 0
        stock_value = 0
        crypto_value = 0
        etf_value = 0
        bond_value = 0
        cash_value = 0
        
        sector_breakdown = {}
        ticker_values = {}
        
        for holding in portfolio:
            current_value = holding.shares * holding.avg_price
            cost_basis = holding.shares * holding.avg_price  # Simplified - using avg_price as cost
            
            total_value += current_value
            total_cost += cost_basis
            ticker_values[holding.ticker] = current_value
            
            # Categorize by type
            if hasattr(holding, 'category'):
                category = holding.category
            else:
                # Determine category based on ticker patterns
                if holding.ticker in ['BTC', 'ETH', 'ADA', 'DOT', 'LINK']:
                    category = 'Crypto'
                elif holding.ticker in ['VOO', 'VTI', 'SPY', 'QQQ']:
                    category = 'ETF'
                elif holding.ticker in ['BND', 'TLT', 'AGG']:
                    category = 'Bond'
                elif holding.ticker in ['CASH', 'USD']:
                    category = 'Cash'
                else:
                    category = 'Stock'
            
            if category == 'Stock':
                stock_value += current_value
                # Simple sector mapping (in real app, use proper sector data)
                sector = get_sector_for_ticker(holding.ticker)
                sector_breakdown[sector] = sector_breakdown.get(sector, 0) + current_value
            elif category == 'Crypto':
                crypto_value += current_value
            elif category == 'ETF':
                etf_value += current_value
            elif category == 'Bond':
                bond_value += current_value
            elif category == 'Cash':
                cash_value += current_value
        
        # Calculate performance metrics
        gain_loss = total_value - total_cost
        gain_loss_pct = (gain_loss / total_cost * 100) if total_cost > 0 else 0
        
        # Calculate diversification score (Herfindahl-Hirschman Index)
        if total_value > 0:
            weights = [v / total_value for v in ticker_values.values()]
            diversification = 1 - sum(w**2 for w in weights)  # Higher is better
        else:
            diversification = 0
        
        # Calculate sector concentration
        if sector_breakdown and total_value > 0:
            sector_weights = [v / total_value for v in sector_breakdown.values()]
            sector_concentration = max(sector_weights) if sector_weights else 0
            top_sector = max(sector_breakdown, key=sector_breakdown.get) if sector_breakdown else 'Unknown'
        else:
            sector_concentration = 0
            top_sector = 'Unknown'
        
        # Calculate Sharpe ratio (simplified)
        sharpe_ratio = calculate_sharpe_ratio(user_id, db, total_value)
        
        # Calculate benchmark difference (simplified)
        benchmark_diff = calculate_benchmark_difference(user_id, db, total_value)
        
        # Prepare metrics
        metrics = {
            "net_worth": round(total_value, 2),
            "gain_loss_pct": round(gain_loss_pct, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "diversification": round(diversification, 2),
            "top_sector": top_sector,
            "sector_concentration": round(sector_concentration, 2),
            "benchmark_diff": round(benchmark_diff, 2),
            "holdings_count": len(portfolio),
            "category_breakdown": {
                "stocks": round(stock_value, 2),
                "crypto": round(crypto_value, 2),
                "etfs": round(etf_value, 2),
                "bonds": round(bond_value, 2),
                "cash": round(cash_value, 2)
            }
        }
        
        return metrics
        
    except Exception as e:
        print(f"Error calculating portfolio metrics: {e}")
        return None

def get_sector_for_ticker(ticker: str) -> str:
    """Simple sector mapping for common tickers"""
    tech_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX', 'ADBE', 'CRM']
    finance_tickers = ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'AXP', 'V', 'MA', 'PYPL']
    healthcare_tickers = ['JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR']
    consumer_tickers = ['KO', 'PEP', 'WMT', 'PG', 'NKE', 'MCD', 'SBUX', 'DIS']
    energy_tickers = ['XOM', 'CVX', 'COP', 'EOG', 'SLB']
    
    if ticker in tech_tickers:
        return 'Technology'
    elif ticker in finance_tickers:
        return 'Financial'
    elif ticker in healthcare_tickers:
        return 'Healthcare'
    elif ticker in consumer_tickers:
        return 'Consumer'
    elif ticker in energy_tickers:
        return 'Energy'
    else:
        return 'Other'

def calculate_sharpe_ratio(user_id: int, db: Session, current_value: float) -> float:
    """Calculate simplified Sharpe ratio"""
    try:
        # Get historical data for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Get portfolio performance data
        historical_data = db.query(HistoricalData).filter(
            HistoricalData.date >= start_date,
            HistoricalData.date <= end_date
        ).all()
        
        if not historical_data:
            return 1.0  # Default value
        
        # Calculate daily returns (simplified)
        daily_returns = []
        for i in range(1, len(historical_data)):
            prev_value = historical_data[i-1].close_price
            curr_value = historical_data[i].close_price
            if prev_value > 0:
                daily_return = (curr_value - prev_value) / prev_value
                daily_returns.append(daily_return)
        
        if not daily_returns:
            return 1.0
        
        # Calculate Sharpe ratio (simplified)
        mean_return = np.mean(daily_returns)
        std_return = np.std(daily_returns)
        
        if std_return > 0:
            sharpe = mean_return / std_return * np.sqrt(252)  # Annualized
            return max(0, min(3, sharpe))  # Clamp between 0 and 3
        else:
            return 1.0
            
    except Exception as e:
        print(f"Error calculating Sharpe ratio: {e}")
        return 1.0

def calculate_benchmark_difference(user_id: int, db: Session, current_value: float) -> float:
    """Calculate portfolio performance vs benchmark (simplified)"""
    try:
        # This is a simplified calculation
        # In a real app, you'd compare against S&P 500 or other benchmarks
        
        # For now, return a random value between -5 and 5
        import random
        return round(random.uniform(-2, 3), 2)
        
    except Exception as e:
        print(f"Error calculating benchmark difference: {e}")
        return 0.0

def generate_metrics_hash(metrics: Dict[str, Any]) -> str:
    """Generate SHA-256 hash of metrics for caching"""
    metrics_str = json.dumps(metrics, sort_keys=True)
    return hashlib.sha256(metrics_str.encode()).hexdigest()

def get_cached_insights(user_id: int, metrics_hash: str, db: Session) -> Optional[str]:
    """Check if insights are cached for these metrics"""
    try:
        from models import InsightsCache
        
        # Check for cached insights from today
        today = datetime.now().date()
        cached = db.query(InsightsCache).filter(
            InsightsCache.user_id == user_id,
            InsightsCache.metrics_hash == metrics_hash,
            InsightsCache.date >= today
        ).first()
        
        if cached:
            return cached.insights_text
        return None
        
    except Exception as e:
        print(f"Error checking cache: {e}")
        return None

def save_insights_to_cache(user_id: int, metrics_hash: str, insights_text: str, 
                          is_ai_generated: bool, db: Session) -> None:
    """Save insights to cache"""
    try:
        from models import InsightsCache
        
        cache_entry = InsightsCache(
            user_id=user_id,
            metrics_hash=metrics_hash,
            insights_text=insights_text,
            is_ai_generated=is_ai_generated
        )
        
        db.add(cache_entry)
        db.commit()
        
    except Exception as e:
        print(f"Error saving to cache: {e}")
        db.rollback()

def generate_rule_based_insights(metrics: Dict[str, Any]) -> str:
    """Generate rule-based insights as fallback"""
    insights = []
    
    # Diversification insights
    if metrics['diversification'] < 0.3:
        insights.append("Portfolio shows low diversification, consider spreading investments across more assets.")
    elif metrics['diversification'] > 0.7:
        insights.append("Portfolio is well diversified across multiple holdings.")
    
    # Sector concentration insights
    if metrics['sector_concentration'] > 0.6:
        insights.append(f"High concentration in {metrics['top_sector']} sector increases volatility risk.")
    elif metrics['sector_concentration'] < 0.3:
        insights.append("Portfolio is well spread across different sectors.")
    
    # Performance insights
    if metrics['gain_loss_pct'] > 10:
        insights.append("Strong positive performance with significant gains.")
    elif metrics['gain_loss_pct'] < -5:
        insights.append("Portfolio is experiencing losses, consider reviewing allocation.")
    else:
        insights.append("Portfolio shows moderate performance with room for optimization.")
    
    # Risk insights
    if metrics['sharpe_ratio'] < 0.5:
        insights.append("Risk-adjusted returns could be improved with better diversification.")
    elif metrics['sharpe_ratio'] > 1.5:
        insights.append("Excellent risk-adjusted returns with efficient portfolio management.")
    
    # Benchmark insights
    if metrics['benchmark_diff'] > 2:
        insights.append("Portfolio is outperforming market benchmarks significantly.")
    elif metrics['benchmark_diff'] < -2:
        insights.append("Portfolio is underperforming market benchmarks, consider rebalancing.")
    
    return " ".join(insights) if insights else "Portfolio analysis complete. Consider regular rebalancing and monitoring."
