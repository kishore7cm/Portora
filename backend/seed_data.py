from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Login, Portfolio, Transaction, TransactionType
from passlib.context import CryptContext
from datetime import datetime

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_initial_data():
    """Create initial users and sample data"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).first():
            print("Data already exists, skipping seed...")
            return
        
        # Create users
        users_data = [
            {
                "name": "Kishore Chandramouli",
                "email": "kishore@portora.com",
                "username": "Kishore",
                "password": "123456"
            },
            {
                "name": "Sarah Johnson",
                "email": "sarah@portora.com", 
                "username": "SarahJ",
                "password": "password123"
            },
            {
                "name": "Mike Chen",
                "email": "mike@portora.com",
                "username": "MikeC",
                "password": "mike123"
            },
            {
                "name": "Emily Davis",
                "email": "emily@portora.com",
                "username": "EmilyD",
                "password": "emily123"
            }
        ]
        
        for user_data in users_data:
            # Create user
            user = User(
                name=user_data["name"],
                email=user_data["email"]
            )
            db.add(user)
            db.flush()  # Get the user ID
            
            # Create login
            login = Login(
                user_id=user.id,
                username=user_data["username"],
                password_hash=get_password_hash(user_data["password"])
            )
            db.add(login)
            
            # Create sample portfolio based on user
            if user_data["username"] == "Kishore":
                sample_portfolio = [
                    {"ticker": "AAPL", "shares": 10.0, "avg_price": 150.00},
                    {"ticker": "MSFT", "shares": 5.0, "avg_price": 300.00},
                    {"ticker": "GOOGL", "shares": 3.0, "avg_price": 2500.00},
                    {"ticker": "TSLA", "shares": 2.0, "avg_price": 800.00},
                    {"ticker": "NVDA", "shares": 8.0, "avg_price": 400.00}
                ]
            elif user_data["username"] == "SarahJ":
                sample_portfolio = [
                    {"ticker": "AAPL", "shares": 5.0, "avg_price": 145.00},
                    {"ticker": "AMZN", "shares": 2.0, "avg_price": 3200.00},
                    {"ticker": "META", "shares": 3.0, "avg_price": 350.00},
                    {"ticker": "BRK.B", "shares": 1.0, "avg_price": 300.00}
                ]
            elif user_data["username"] == "MikeC":
                sample_portfolio = [
                    {"ticker": "TSLA", "shares": 10.0, "avg_price": 750.00},
                    {"ticker": "NVDA", "shares": 15.0, "avg_price": 380.00},
                    {"ticker": "AMD", "shares": 20.0, "avg_price": 120.00}
                ]
            elif user_data["username"] == "EmilyD":
                sample_portfolio = [
                    {"ticker": "GOOGL", "shares": 1.0, "avg_price": 2400.00},
                    {"ticker": "AAPL", "shares": 3.0, "avg_price": 155.00},
                    {"ticker": "MSFT", "shares": 2.0, "avg_price": 310.00}
                ]
            else:
                sample_portfolio = []
            
            for stock in sample_portfolio:
                portfolio = Portfolio(
                    user_id=user.id,
                    ticker=stock["ticker"],
                    shares=stock["shares"],
                    avg_price=stock["avg_price"]
                )
                db.add(portfolio)
                
                # Create sample transactions
                buy_transaction = Transaction(
                    user_id=user.id,
                    ticker=stock["ticker"],
                    type=TransactionType.BUY,
                    shares=stock["shares"],
                    price=stock["avg_price"],
                    date=datetime.now()
                )
                db.add(buy_transaction)
        
        db.commit()
        print("✅ Initial data created successfully!")
        print("Users created:")
        for user_data in users_data:
            print(f"  - {user_data['username']} ({user_data['email']}) - Password: {user_data['password']}")
            
    except Exception as e:
        print(f"❌ Error creating initial data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_data()
