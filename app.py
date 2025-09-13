#!/usr/bin/env python3
"""
Portora API - Zero dependency version
Uses only Python standard library
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime
import urllib.parse
import os

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Route requests
        if path == '/':
            response = {"ok": True, "service": "Portora Portfolio Advisor API"}
        elif path == '/health':
            response = {
                "status": "healthy",
                "service": "Portora Portfolio Advisor API",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat()
            }
        elif path == '/portfolio':
            response = {
                "portfolio": [
                    {
                        "Category": "Equity",
                        "Ticker": "AAPL",
                        "Qty": 10,
                        "Curr $": 1500.00,
                        "Curr %": 15.0,
                        "Tgt %": 20.0,
                        "Drift %": -5.0,
                        "RSI": 65.2,
                        "MACD": 0.15,
                        "Market": "US",
                        "Trend": "Bullish",
                        "Action": "Hold"
                    },
                    {
                        "Category": "Equity", 
                        "Ticker": "MSFT",
                        "Qty": 8,
                        "Curr $": 2400.00,
                        "Curr %": 24.0,
                        "Tgt %": 25.0,
                        "Drift %": -1.0,
                        "RSI": 58.7,
                        "MACD": 0.08,
                        "Market": "US",
                        "Trend": "Bullish",
                        "Action": "Hold"
                    }
                ],
                "summary": [
                    {
                        "Category": "Equity",
                        "Curr $": 3900.00,
                        "Curr %": 39.0,
                        "Tgt %": 45.0,
                        "Drift": -6.0
                    }
                ],
                "historical": [
                    {"month": "2024-01", "value": 8500},
                    {"month": "2024-02", "value": 9200},
                    {"month": "2024-03", "value": 8800},
                    {"month": "2024-04", "value": 9500},
                    {"month": "2024-05", "value": 10200},
                    {"month": "2024-06", "value": 9800}
                ]
            }
        elif path == '/sp500':
            response = {
                "sp500": [
                    {
                        "Ticker": "AAPL",
                        "Name": "Apple Inc.",
                        "Sector": "Technology",
                        "Price": 150.00,
                        "Change": 2.50,
                        "Change %": 1.69,
                        "Volume": 45000000,
                        "MarketCap": 2500000000000,
                        "P_E": 28.5,
                        "RSI": 65.2,
                        "MACD": 0.15,
                        "Trend": "Bullish",
                        "Action": "Buy",
                        "Score": 85,
                        "Reason": "Strong fundamentals"
                    }
                ]
            }
        elif path == '/portfolio-health':
            response = {
                "overall_score": 78,
                "drift_score": 15,
                "diversification_score": 85,
                "risk_score": 72,
                "badges": [
                    {"name": "Well Diversified", "status": "earned"},
                    {"name": "Low Risk", "status": "earned"}
                ],
                "recommendations": [
                    "Consider rebalancing technology allocation",
                    "Add more international exposure"
                ]
            }
        elif path == '/alerts':
            response = {
                "alerts": [
                    {
                        "id": 1,
                        "type": "rebalance",
                        "title": "Portfolio Rebalance Needed",
                        "message": "Your portfolio has drifted 5% from target allocation",
                        "priority": "medium",
                        "created_at": "2024-01-15T10:30:00Z",
                        "read": False
                    }
                ]
            }
        elif path == '/alerts/count':
            response = {"unread_count": 1}
        elif path == '/onboarding/status':
            response = {"has_seen_onboarding": False}
        else:
            response = {"error": "Endpoint not found"}
        
        # Send response
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f"Portora API Server running on port {port}")
    print("Available endpoints:")
    print("  GET /health - Health check")
    print("  GET /portfolio - Portfolio data")
    print("  GET /sp500 - S&P 500 data")
    print("  GET /portfolio-health - Portfolio health")
    print("  GET /alerts - Alerts")
    print("  GET /alerts/count - Alert count")
    print("  GET /onboarding/status - Onboarding status")
    server.serve_forever()
