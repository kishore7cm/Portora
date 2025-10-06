"""
Application Configuration
Centralized settings for scalability
"""

import os
from typing import Optional

class Settings:
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./portfolio.db"
    
    # API Configuration
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8001
    API_VERSION: str = "2.0.0"
    
    # Data Sources
    HISTORICAL_CSV_PATH: str = "/Users/kishorecm/Documents/EaseLi/Portfolio CSV files/portfolio_history_10y.csv"
    
    # External APIs
    ALPACA_API_KEY: Optional[str] = os.getenv("APCA_API_KEY_ID")
    ALPACA_SECRET_KEY: Optional[str] = os.getenv("APCA_API_SECRET_KEY")
    TWELVE_DATA_API_KEY: Optional[str] = os.getenv("TWELVE_DATA_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Cache Settings (for future Redis integration)
    CACHE_TTL: int = 300  # 5 minutes
    ENABLE_CACHE: bool = False
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "portfolio_api.log"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]
    
    # Performance
    MAX_PORTFOLIO_SIZE: int = 1000
    MAX_HISTORICAL_DAYS: int = 3650  # 10 years
    
    # Feature Flags
    ENABLE_AI_INSIGHTS: bool = True
    ENABLE_REAL_TIME_UPDATES: bool = False
    ENABLE_BACKGROUND_TASKS: bool = False

# Global settings instance
settings = Settings()
