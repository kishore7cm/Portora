from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db
from models import User, PortfolioValues

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/portfolio")
def get_portfolio(user_id: int = 1, db: Session = Depends(get_db)):
    """Get portfolio data using PortfolioValues table"""
    try:
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        # Get portfolio values from PortfolioValues table
        portfolio_values = db.query(PortfolioValues).filter(PortfolioValues.user_id == user_id).all()
        
        if not portfolio_values:
            return {
                "portfolio": [],
                "summary": {
                    "Total_Value": 0,
                    "Total_Cost_Basis": 0,
                    "Total_Gain_Loss": 0,
                    "Total_Gain_Loss_Percent": 0,
                    "Total_Stocks": 0,
                    "User": user.name
                },
                "status": "success"
            }
        
        # Convert to expected format
        portfolio_data = []
        total_value = 0
        total_cost_basis = 0
        total_gain_loss = 0
        
        for value in portfolio_values:
            # Calculate shares and avg_price
            shares = value.total_value / value.current_price if value.current_price > 0 else 0
            avg_price = value.cost_basis / shares if shares > 0 else 0
            
            portfolio_data.append({
                "Ticker": value.ticker,
                "Qty": shares,
                "Avg_Price": avg_price,
                "Current_Price": value.current_price,
                "Total_Value": value.total_value,
                "Cost_Basis": value.cost_basis,
                "Gain_Loss": value.gain_loss,
                "Gain_Loss_Percent": value.gain_loss_percent,
                "Category": value.category or "Stock"
            })
            
            total_value += value.total_value
            total_cost_basis += value.cost_basis
            total_gain_loss += value.gain_loss
        
        # Calculate summary
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

@app.get("/test")
def test():
    """Test endpoint"""
    return {"message": "New API working", "status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
