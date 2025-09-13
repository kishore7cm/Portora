#!/usr/bin/env python3
"""
Populate Database with Dummy Data
Creates dummy users, portfolios, and trading bots for testing
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta
from enhanced_user_management import enhanced_user_manager
from bot_management import bot_manager
import csv
import os

def create_dummy_users():
    """Create dummy users with different portfolio types"""
    users = [
        {
            "email": "conservative@example.com",
            "password": "password123",
            "first_name": "Conservative",
            "last_name": "Investor",
            "portfolio_type": "conservative"
        },
        {
            "email": "aggressive@example.com", 
            "password": "password123",
            "first_name": "Aggressive",
            "last_name": "Trader",
            "portfolio_type": "aggressive"
        },
        {
            "email": "balanced@example.com",
            "password": "password123", 
            "first_name": "Balanced",
            "last_name": "Investor",
            "portfolio_type": "balanced"
        },
        {
            "email": "tech@example.com",
            "password": "password123",
            "first_name": "Tech",
            "last_name": "Enthusiast", 
            "portfolio_type": "tech_heavy"
        },
        {
            "email": "dividend@example.com",
            "password": "password123",
            "first_name": "Dividend",
            "last_name": "Hunter",
            "portfolio_type": "dividend_focused"
        }
    ]
    
    created_users = []
    for user_data in users:
        # Try to register, but if user exists, get their ID
        result = enhanced_user_manager.register_user(
            user_data["email"],
            user_data["password"], 
            user_data["first_name"],
            user_data["last_name"]
        )
        
        if result and result.get("success"):
            user_id = result["user_id"]
            created_users.append({
                "id": user_id,
                "email": user_data["email"],
                "portfolio_type": user_data["portfolio_type"]
            })
            print(f"✅ Created user: {user_data['email']} (ID: {user_id})")
        elif result and "already exists" in result.get("message", ""):
            # User exists, try to authenticate to get user ID
            auth_result = enhanced_user_manager.authenticate_user(user_data["email"], user_data["password"])
            if auth_result and auth_result.get("success"):
                user_id = auth_result["user"]["id"]
                created_users.append({
                    "id": user_id,
                    "email": user_data["email"],
                    "portfolio_type": user_data["portfolio_type"]
                })
                print(f"✅ Found existing user: {user_data['email']} (ID: {user_id})")
            else:
                print(f"❌ Failed to authenticate existing user: {user_data['email']}")
        else:
            print(f"❌ Failed to create user: {user_data['email']} - {result}")
    
    return created_users

def create_dummy_portfolios(users):
    """Create dummy portfolios for each user"""
    portfolio_templates = {
        "conservative": {
            "name": "Conservative Portfolio",
            "holdings": [
                {"symbol": "VTI", "shares": 100, "asset_class": "equity", "sector": "total_market"},
                {"symbol": "BND", "shares": 200, "asset_class": "bond", "sector": "total_bond"},
                {"symbol": "VEA", "shares": 50, "asset_class": "equity", "sector": "international"},
                {"symbol": "VWO", "shares": 30, "asset_class": "equity", "sector": "emerging_markets"},
                {"symbol": "GLD", "shares": 20, "asset_class": "commodity", "sector": "precious_metals"}
            ]
        },
        "aggressive": {
            "name": "Aggressive Growth Portfolio", 
            "holdings": [
                {"symbol": "QQQ", "shares": 150, "asset_class": "equity", "sector": "technology"},
                {"symbol": "ARKK", "shares": 100, "asset_class": "equity", "sector": "innovation"},
                {"symbol": "TSLA", "shares": 50, "asset_class": "equity", "sector": "automotive"},
                {"symbol": "NVDA", "shares": 75, "asset_class": "equity", "sector": "semiconductors"},
                {"symbol": "BTC-USD", "shares": 0.5, "asset_class": "crypto", "sector": "cryptocurrency"}
            ]
        },
        "balanced": {
            "name": "Balanced Portfolio",
            "holdings": [
                {"symbol": "VTI", "shares": 120, "asset_class": "equity", "sector": "total_market"},
                {"symbol": "BND", "shares": 150, "asset_class": "bond", "sector": "total_bond"},
                {"symbol": "VEA", "shares": 60, "asset_class": "equity", "sector": "international"},
                {"symbol": "REIT", "shares": 40, "asset_class": "equity", "sector": "real_estate"},
                {"symbol": "GLD", "shares": 15, "asset_class": "commodity", "sector": "precious_metals"}
            ]
        },
        "tech_heavy": {
            "name": "Tech-Heavy Portfolio",
            "holdings": [
                {"symbol": "AAPL", "shares": 100, "asset_class": "equity", "sector": "technology"},
                {"symbol": "MSFT", "shares": 80, "asset_class": "equity", "sector": "technology"},
                {"symbol": "GOOGL", "shares": 60, "asset_class": "equity", "sector": "technology"},
                {"symbol": "AMZN", "shares": 40, "asset_class": "equity", "sector": "technology"},
                {"symbol": "META", "shares": 50, "asset_class": "equity", "sector": "technology"}
            ]
        },
        "dividend_focused": {
            "name": "Dividend Focused Portfolio",
            "holdings": [
                {"symbol": "SCHD", "shares": 200, "asset_class": "equity", "sector": "dividend_aristocrats"},
                {"symbol": "VYM", "shares": 150, "asset_class": "equity", "sector": "high_dividend"},
                {"symbol": "JNJ", "shares": 100, "asset_class": "equity", "sector": "healthcare"},
                {"symbol": "KO", "shares": 120, "asset_class": "equity", "sector": "consumer_staples"},
                {"symbol": "PG", "shares": 80, "asset_class": "equity", "sector": "consumer_staples"}
            ]
        }
    }
    
    created_portfolios = []
    for user in users:
        portfolio_type = user["portfolio_type"]
        template = portfolio_templates[portfolio_type]
        
        # Create portfolio
        portfolio_id = enhanced_user_manager.create_portfolio(
            user["id"],
            template["name"],
            "Dummy portfolio for testing"
        )
        
        if portfolio_id:
            # Add holdings
            for holding in template["holdings"]:
                enhanced_user_manager.add_holding_to_portfolio(
                    portfolio_id,
                    holding["symbol"],
                    holding["shares"],
                    holding["asset_class"],
                    holding["sector"]
                )
            
            created_portfolios.append({
                "id": portfolio_id,
                "user_id": user["id"],
                "name": template["name"],
                "type": portfolio_type
            })
            print(f"✅ Created portfolio: {template['name']} for user {user['email']}")
    
    return created_portfolios

def create_dummy_bots(users):
    """Create dummy trading bots for each user"""
    bot_templates = [
        {"name": "DCA Bitcoin Bot", "type": "dca", "symbol": "BTC-USD"},
        {"name": "Momentum Tech Bot", "type": "momentum", "symbol": "QQQ"},
        {"name": "Mean Reversion Bot", "type": "mean_reversion", "symbol": "SPY"},
        {"name": "Grid Trading Bot", "type": "grid", "symbol": "ETH-USD"},
        {"name": "News Sentiment Bot", "type": "news_based", "symbol": "AAPL"}
    ]
    
    created_bots = []
    for user in users:
        # Create 2-3 random bots per user
        num_bots = random.randint(2, 3)
        selected_bots = random.sample(bot_templates, num_bots)
        
        for bot_template in selected_bots:
            bot_id = bot_manager.create_bot(
                user["id"],
                bot_template["name"],
                bot_template["type"],
                {"symbol": bot_template["symbol"], "amount": 1000}
            )
            
            if bot_id:
                created_bots.append({
                    "id": bot_id,
                    "user_id": user["id"],
                    "name": bot_template["name"],
                    "type": bot_template["type"]
                })
                print(f"✅ Created bot: {bot_template['name']} for user {user['email']}")
    
    return created_bots

def main():
    """Main function to populate all dummy data"""
    print("🚀 Starting dummy data population...")
    
    # Create users
    print("\n📝 Creating dummy users...")
    users = create_dummy_users()
    
    # Create portfolios
    print("\n💼 Creating dummy portfolios...")
    portfolios = create_dummy_portfolios(users)
    
    # Create bots
    print("\n🤖 Creating dummy trading bots...")
    bots = create_dummy_bots(users)
    
    print(f"\n✅ Dummy data population complete!")
    print(f"   - Users: {len(users)}")
    print(f"   - Portfolios: {len(portfolios)}")
    print(f"   - Bots: {len(bots)}")
    
    # Print summary
    print("\n📊 Summary:")
    for user in users:
        user_portfolios = [p for p in portfolios if p["user_id"] == user["id"]]
        user_bots = [b for b in bots if b["user_id"] == user["id"]]
        print(f"   {user['email']}: {len(user_portfolios)} portfolios, {len(user_bots)} bots")

    # Map the root demo credentials to the conservative user and import CSV holdings
    try:
        print("\n📥 Importing CSV holdings into demo user (mapped from conservative@example.com)...")
        # Ensure conservative user exists
        auth = enhanced_user_manager.authenticate_user("conservative@example.com", "password123")
        if not auth or not auth.get("success"):
            created = enhanced_user_manager.register_user("conservative@example.com", "password123", "Conservative", "Investor")
            if created and created.get("success"):
                auth = enhanced_user_manager.authenticate_user("conservative@example.com", "password123")
        if auth and auth.get("success"):
            user_id = auth["user"]["id"]
            primary_portfolio_id = enhanced_user_manager.get_primary_portfolio_id(user_id)
            if not primary_portfolio_id:
                primary_portfolio_id = enhanced_user_manager.create_portfolio(user_id, "Main Portfolio", "Imported from CSV")
            if primary_portfolio_id:
                enhanced_user_manager.clear_portfolio_holdings(primary_portfolio_id)
                csv_path = os.path.join(os.path.dirname(__file__), "portfolio", "robinhood_portfolio_combined2.csv")
                if os.path.exists(csv_path):
                    with open(csv_path, newline='') as f:
                        reader = csv.DictReader(f)
                        imported = 0
                        for row in reader:
                            symbol = row.get("Symbol")
                            cls = row.get("Classification", "Stock")
                            qty_str = row.get("Quantity Owned") or row.get("Quantity") or "0"
                            try:
                                quantity = float(qty_str)
                            except Exception:
                                quantity = 0.0
                            # Map classification to asset_class
                            asset_class = "equity"
                            if cls and cls.lower() == "crypto":
                                asset_class = "crypto"
                            elif cls and cls.lower() == "bond":
                                asset_class = "bond"
                            elif cls and cls.lower() == "etf":
                                asset_class = "equity"
                            sector = "unknown"
                            if symbol:
                                if enhanced_user_manager.add_holding_to_portfolio(primary_portfolio_id, symbol, quantity, asset_class, sector):
                                    imported += 1
                        print(f"✅ Imported {imported} holdings from CSV into demo user's portfolio (id={primary_portfolio_id})")
                else:
                    print(f"⚠ CSV file not found at {csv_path}; skipped import")
        else:
            print("⚠ Could not ensure conservative demo user; skipped CSV import")
    except Exception as e:
        print(f"❌ CSV import error: {e}")

if __name__ == "__main__":
    main()
