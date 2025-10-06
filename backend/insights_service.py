"""
Portfolio Insights Service using OpenAI GPT
"""

import os
import json
import hashlib
import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import openai
from openai import OpenAI

# Database imports
from core.database import SessionLocal
from domain.models_v2 import Portfolio, PortfolioSummary

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioInsightsService:
    """Service for generating AI-powered portfolio insights"""
    
    def __init__(self, db: Session):
        self.db = db
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            self.client = OpenAI(api_key=self.openai_api_key)
        else:
            self.client = None
            logger.warning("OpenAI API key not found. AI insights will use rule-based fallbacks.")
    
    def create_insights_cache_table(self):
        """Create insights cache table if it doesn't exist"""
        try:
            self.db.execute(text("""
                CREATE TABLE IF NOT EXISTS insights_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    metrics_hash TEXT NOT NULL,
                    insights TEXT NOT NULL,
                    insight_type TEXT DEFAULT 'ai',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, metrics_hash)
                )
            """))
            self.db.commit()
            logger.info("✅ Insights cache table created/verified")
        except Exception as e:
            logger.error(f"Error creating insights cache table: {e}")
            self.db.rollback()
    
    def compute_portfolio_metrics(self, user_id: int, as_of: Optional[date] = None) -> Dict[str, Any]:
        """Compute portfolio metrics for insights generation"""
        if as_of is None:
            as_of = date.today()
        
        try:
            # Get portfolio summary
            summary = (
                self.db.query(PortfolioSummary)
                .filter(PortfolioSummary.user_id == user_id)
                .filter(PortfolioSummary.date == as_of)
                .first()
            )
            
            # Get portfolio positions
            positions = (
                self.db.query(Portfolio)
                .filter(Portfolio.user_id == user_id)
                .all()
            )
            
            if not summary or not positions:
                # Use fallback values for demo
                return {
                    "net_worth": 327625.00,
                    "gain_loss_pct": 0.81,
                    "sharpe_ratio": 1.85,
                    "diversification_score": 75,
                    "top_sector": "Technology",
                    "sector_concentration": 45.2,
                    "benchmark_diff": 2.3,
                    "num_positions": 15,
                    "cash_percentage": 4.4,
                    "crypto_percentage": 22.9,
                    "stock_percentage": 72.5,
                    "risk_level": "Medium-High"
                }
            
            # Calculate metrics from actual data
            total_value = float(summary.total_value or 0)
            gain_loss_pct = float(summary.total_gain_loss_percent or 0)
            
            # Calculate diversification (simplified Herfindahl-Hirschman Index)
            position_values = [float(pos.units * pos.avg_price) for pos in positions]
            total_portfolio_value = sum(position_values)
            
            if total_portfolio_value > 0:
                weights = [val / total_portfolio_value for val in position_values]
                hhi = sum(w * w for w in weights)
                diversification_score = max(0, min(100, (1 - hhi) * 100))
            else:
                diversification_score = 50
            
            # Sector analysis (simplified)
            tech_tickers = {'AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMZN', 'TSLA'}
            tech_value = sum(
                float(pos.units * pos.avg_price) 
                for pos in positions 
                if pos.ticker in tech_tickers
            )
            sector_concentration = (tech_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
            
            return {
                "net_worth": total_value,
                "gain_loss_pct": gain_loss_pct,
                "sharpe_ratio": 1.85,  # Placeholder
                "diversification_score": diversification_score,
                "top_sector": "Technology",
                "sector_concentration": sector_concentration,
                "benchmark_diff": gain_loss_pct - 0.5,  # Assume 0.5% benchmark
                "num_positions": len(positions),
                "cash_percentage": 4.4,  # Placeholder
                "crypto_percentage": 22.9,  # Placeholder
                "stock_percentage": 72.5,  # Placeholder
                "risk_level": "Medium-High" if diversification_score < 70 else "Medium"
            }
            
        except Exception as e:
            logger.error(f"Error computing portfolio metrics: {e}")
            # Return fallback metrics
            return {
                "net_worth": 327625.00,
                "gain_loss_pct": 0.81,
                "sharpe_ratio": 1.85,
                "diversification_score": 75,
                "top_sector": "Technology",
                "sector_concentration": 45.2,
                "benchmark_diff": 0.31,
                "num_positions": 15,
                "cash_percentage": 4.4,
                "crypto_percentage": 22.9,
                "stock_percentage": 72.5,
                "risk_level": "Medium"
            }
    
    def generate_rule_based_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate rule-based insights as fallback"""
        insights = []
        
        # Performance insight
        if metrics["gain_loss_pct"] > 0:
            insights.append(f"Your portfolio is performing well with a {metrics['gain_loss_pct']:.2f}% return, outpacing many traditional benchmarks.")
        else:
            insights.append(f"Your portfolio is down {abs(metrics['gain_loss_pct']):.2f}%, which is within normal market fluctuation ranges.")
        
        # Diversification insight
        if metrics["diversification_score"] > 80:
            insights.append("Your portfolio shows excellent diversification, which helps reduce overall risk.")
        elif metrics["diversification_score"] > 60:
            insights.append("Your portfolio has moderate diversification. Consider spreading investments across more sectors.")
        else:
            insights.append("Your portfolio is concentrated in few positions. Diversifying could help reduce risk.")
        
        # Sector concentration insight
        if metrics["sector_concentration"] > 50:
            insights.append(f"High concentration in {metrics['top_sector']} ({metrics['sector_concentration']:.1f}%) creates sector-specific risk.")
        
        # Crypto allocation insight
        if metrics["crypto_percentage"] > 20:
            insights.append("Your crypto allocation is significant. While offering growth potential, it also increases volatility.")
        
        return insights[:3]  # Return top 3 insights
    
    def generate_ai_insights(self, metrics: Dict[str, Any]) -> Optional[List[str]]:
        """Generate AI-powered insights using OpenAI"""
        if not self.client:
            return None
        
        try:
            # Create compact prompt
            prompt = f"""Analyze this portfolio and provide 3 concise insights (1-2 sentences each):

Portfolio Metrics:
- Net Worth: ${metrics['net_worth']:,.0f}
- Return: {metrics['gain_loss_pct']:.2f}%
- Diversification Score: {metrics['diversification_score']:.0f}/100
- Top Sector: {metrics['top_sector']} ({metrics['sector_concentration']:.1f}%)
- Crypto Allocation: {metrics['crypto_percentage']:.1f}%
- Risk Level: {metrics['risk_level']}
- Positions: {metrics['num_positions']}

Provide exactly 3 insights focusing on: 1) Performance, 2) Risk/Diversification, 3) Strategic recommendation. Keep each under 25 words."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional financial advisor providing concise portfolio insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse insights (split by numbers or newlines)
            insights = []
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove numbering (1., 2., etc.)
                    clean_line = line.lstrip('123456789. -')
                    if clean_line:
                        insights.append(clean_line)
            
            return insights[:3] if insights else None
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return None
    
    def get_cached_insights(self, user_id: int, metrics_hash: str) -> Optional[List[str]]:
        """Get cached insights if available"""
        try:
            result = self.db.execute(text("""
                SELECT insights FROM insights_cache 
                WHERE user_id = :user_id AND metrics_hash = :hash
                ORDER BY created_at DESC LIMIT 1
            """), {"user_id": user_id, "hash": metrics_hash}).fetchone()
            
            if result:
                return json.loads(result[0])
            return None
        except Exception as e:
            logger.error(f"Error getting cached insights: {e}")
            return None
    
    def cache_insights(self, user_id: int, metrics_hash: str, insights: List[str], insight_type: str = "ai"):
        """Cache insights for future use"""
        try:
            self.db.execute(text("""
                INSERT OR REPLACE INTO insights_cache 
                (user_id, metrics_hash, insights, insight_type)
                VALUES (:user_id, :hash, :insights, :type)
            """), {
                "user_id": user_id,
                "hash": metrics_hash,
                "insights": json.dumps(insights),
                "type": insight_type
            })
            self.db.commit()
        except Exception as e:
            logger.error(f"Error caching insights: {e}")
            self.db.rollback()
    
    def generate_insights(self, user_id: int) -> Dict[str, Any]:
        """Main method to generate portfolio insights"""
        try:
            # Ensure cache table exists
            self.create_insights_cache_table()
            
            # Compute portfolio metrics
            metrics = self.compute_portfolio_metrics(user_id)
            
            # Create hash of metrics for caching
            metrics_str = json.dumps(metrics, sort_keys=True)
            metrics_hash = hashlib.sha256(metrics_str.encode()).hexdigest()[:16]
            
            # Check cache first
            cached_insights = self.get_cached_insights(user_id, metrics_hash)
            if cached_insights:
                return {
                    "insights": cached_insights,
                    "source": "cache",
                    "metrics": metrics
                }
            
            # Try AI insights first
            ai_insights = self.generate_ai_insights(metrics)
            if ai_insights:
                self.cache_insights(user_id, metrics_hash, ai_insights, "ai")
                return {
                    "insights": ai_insights,
                    "source": "ai",
                    "metrics": metrics
                }
            
            # Fallback to rule-based insights
            rule_insights = self.generate_rule_based_insights(metrics)
            self.cache_insights(user_id, metrics_hash, rule_insights, "rule")
            
            return {
                "insights": rule_insights,
                "source": "rule",
                "metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {
                "insights": ["Portfolio analysis temporarily unavailable. Please try again later."],
                "source": "error",
                "metrics": {}
            }

def get_insights_service(db: Session = None) -> PortfolioInsightsService:
    """Get insights service instance"""
    if db is None:
        db = SessionLocal()
    return PortfolioInsightsService(db)
