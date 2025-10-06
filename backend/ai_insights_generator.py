#!/usr/bin/env python3
"""
AI Insights Generator
Generates natural language insights using OpenAI API
"""

import openai
import json
from typing import List, Dict, Any, Optional
from config.api_keys import load_keys

def generate_ai_insights(metrics: Dict[str, Any]) -> Optional[str]:
    """
    Generate AI-powered insights using OpenAI API
    """
    try:
        # Load API keys
        keys = load_keys()
        openai.api_key = keys.get('openai_api_key')
        
        if not openai.api_key:
            print("OpenAI API key not configured")
            return None
        
        # Create compact prompt
        prompt = f"""Convert this portfolio analysis into 2-3 natural language insights. Keep concise, financial-advisor style. Output plain text sentences only.

Portfolio Analysis:
- Net Worth: ${metrics['net_worth']:,.0f}
- Performance: {metrics['gain_loss_pct']:+.1f}%
- Sharpe Ratio: {metrics['sharpe_ratio']:.2f}
- Diversification: {metrics['diversification']:.2f}/1.0
- Top Sector: {metrics['top_sector']} ({metrics['sector_concentration']:.1%} concentration)
- Benchmark: {metrics['benchmark_diff']:+.1f}% vs market
- Holdings: {metrics['holdings_count']} assets

Asset Allocation:
- Stocks: ${metrics['category_breakdown']['stocks']:,.0f}
- Crypto: ${metrics['category_breakdown']['crypto']:,.0f}
- ETFs: ${metrics['category_breakdown']['etfs']:,.0f}
- Bonds: ${metrics['category_breakdown']['bonds']:,.0f}
- Cash: ${metrics['category_breakdown']['cash']:,.0f}

Provide 2-3 actionable insights focusing on risk, diversification, and performance optimization."""
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Cheaper and faster model
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional portfolio advisor. Provide concise, actionable insights based on portfolio metrics. Focus on risk management, diversification, and performance optimization. Keep responses under 200 words."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,  # Limit tokens for cost control
            temperature=0.7
        )
        
        insights_text = response.choices[0].message.content.strip()
        return insights_text
        
    except Exception as e:
        print(f"Error generating AI insights: {e}")
        return None

def generate_detailed_insights(metrics: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Generate detailed insights for the Insights tab (3-5 cards)
    """
    try:
        # Load API keys
        keys = load_keys()
        openai.api_key = keys.get('openai_api_key')
        
        if not openai.api_key:
            return generate_rule_based_detailed_insights(metrics)
        
        # Create detailed prompt for multiple insights
        prompt = f"""Analyze this portfolio and provide 4 specific insights in JSON format. Each insight should have a title and description.

Portfolio Analysis:
- Net Worth: ${metrics['net_worth']:,.0f}
- Performance: {metrics['gain_loss_pct']:+.1f}%
- Sharpe Ratio: {metrics['sharpe_ratio']:.2f}
- Diversification: {metrics['diversification']:.2f}/1.0
- Top Sector: {metrics['top_sector']} ({metrics['sector_concentration']:.1%} concentration)
- Benchmark: {metrics['benchmark_diff']:+.1f}% vs market
- Holdings: {metrics['holdings_count']} assets

Asset Allocation:
- Stocks: ${metrics['category_breakdown']['stocks']:,.0f}
- Crypto: ${metrics['category_breakdown']['crypto']:,.0f}
- ETFs: ${metrics['category_breakdown']['etfs']:,.0f}
- Bonds: ${metrics['category_breakdown']['bonds']:,.0f}
- Cash: ${metrics['category_breakdown']['cash']:,.0f}

Return JSON with this structure:
{{
    "insights": [
        {{"title": "Risk Assessment", "description": "..."}},
        {{"title": "Diversification Analysis", "description": "..."}},
        {{"title": "Performance Review", "description": "..."}},
        {{"title": "Recommendations", "description": "..."}}
    ]
}}"""
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional portfolio advisor. Provide specific, actionable insights in the requested JSON format. Each insight should be 1-2 sentences and focus on different aspects of the portfolio."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            insights_data = json.loads(response_text)
            return insights_data.get('insights', [])
        except json.JSONDecodeError:
            # Fallback to rule-based if JSON parsing fails
            return generate_rule_based_detailed_insights(metrics)
        
    except Exception as e:
        print(f"Error generating detailed AI insights: {e}")
        return generate_rule_based_detailed_insights(metrics)

def generate_rule_based_detailed_insights(metrics: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate rule-based detailed insights as fallback"""
    insights = []
    
    # Risk Assessment
    if metrics['sharpe_ratio'] < 0.5:
        risk_desc = f"Portfolio shows low risk-adjusted returns (Sharpe: {metrics['sharpe_ratio']:.2f}). Consider rebalancing to improve efficiency."
    elif metrics['sharpe_ratio'] > 1.5:
        risk_desc = f"Excellent risk management with high Sharpe ratio of {metrics['sharpe_ratio']:.2f}. Portfolio is efficiently managed."
    else:
        risk_desc = f"Moderate risk profile with Sharpe ratio of {metrics['sharpe_ratio']:.2f}. Monitor performance regularly."
    
    insights.append({
        "title": "Risk Assessment",
        "description": risk_desc
    })
    
    # Diversification Analysis
    if metrics['diversification'] < 0.3:
        div_desc = f"Low diversification score of {metrics['diversification']:.2f}. Consider adding more holdings to reduce concentration risk."
    elif metrics['diversification'] > 0.7:
        div_desc = f"Strong diversification with score of {metrics['diversification']:.2f}. Portfolio is well spread across assets."
    else:
        div_desc = f"Moderate diversification at {metrics['diversification']:.2f}. Consider adding more holdings for better balance."
    
    insights.append({
        "title": "Diversification Analysis",
        "description": div_desc
    })
    
    # Performance Review
    if metrics['gain_loss_pct'] > 10:
        perf_desc = f"Strong performance with {metrics['gain_loss_pct']:+.1f}% returns. Portfolio is outperforming expectations."
    elif metrics['gain_loss_pct'] < -5:
        perf_desc = f"Portfolio is down {metrics['gain_loss_pct']:+.1f}%. Consider reviewing allocation and risk management."
    else:
        perf_desc = f"Moderate performance at {metrics['gain_loss_pct']:+.1f}%. Room for optimization through better asset selection."
    
    insights.append({
        "title": "Performance Review",
        "description": perf_desc
    })
    
    # Recommendations
    if metrics['sector_concentration'] > 0.6:
        rec_desc = f"High concentration in {metrics['top_sector']} sector ({metrics['sector_concentration']:.1%}). Consider diversifying across sectors."
    elif metrics['benchmark_diff'] < -2:
        rec_desc = f"Underperforming benchmark by {metrics['benchmark_diff']:+.1f}%. Review asset allocation and consider rebalancing."
    else:
        rec_desc = "Portfolio is well-balanced. Continue monitoring and consider regular rebalancing to maintain optimal allocation."
    
    insights.append({
        "title": "Recommendations",
        "description": rec_desc
    })
    
    return insights
