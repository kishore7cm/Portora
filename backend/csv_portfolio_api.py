#!/usr/bin/env python3
"""
Wealtheon CSV Portfolio API - Reads directly from master_portfolio_new.csv
"""

import csv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Wealtheon CSV Portfolio API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load CSV data at startup
CSV_PATH = "/Users/kishorecm/Documents/EaseLi/Portfolio CSV files/master_portfolio_new.csv"
portfolio_data = []
total_value = 0

def load_csv_data():
    global portfolio_data, total_value
    try:
        with open(CSV_PATH, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                shares = float(row['shares'])
                total_val = float(row['total_value'])
                total_cost = float(row['total_cost'])
                current_price = total_val / shares if shares > 0 else 0
                gain_loss = total_val - total_cost
                gain_loss_percent = (gain_loss / total_cost * 100) if total_cost > 0 else 0
                
                portfolio_data.append({
                    "Ticker": row['symbol'],
                    "Qty": shares,
                    "Current_Price": current_price,
                    "Total_Value": total_val,
                    "Cost_Basis": total_cost,
                    "Gain_Loss": gain_loss,
                    "Gain_Loss_Percent": gain_loss_percent,
                    "Category": row['asset_type']
                })
                total_value += total_val
        
        print(f"✅ Loaded {len(portfolio_data)} holdings from CSV")
        print(f"💰 Total portfolio value: ${total_value:,.2f}")
        
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")

# Load data on startup
load_csv_data()

@app.get("/")
def root():
    return {
        "message": "Wealtheon CSV Portfolio API", 
        "records": len(portfolio_data),
        "total_value": total_value
    }

@app.get("/portfolio")
def get_portfolio(user_id: int = 1):
    return {"portfolio": portfolio_data}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Wealtheon CSV Portfolio API on http://localhost:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=False)
