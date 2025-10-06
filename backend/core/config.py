"""
Core Configuration - The Perfect Way
Single source of truth for all settings
"""

import os
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import validator

class Settings(BaseSettings):
    """Application settings with validation"""
    
    # App Info
    APP_NAME: str = "Portfolio API"
    VERSION: str = "3.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./portfolio_v2.db"
    
    # API
    HOST: str = "127.0.0.1"
    PORT: int = 8001
    RELOAD: bool = True
    
    # Data Sources
    CSV_PATH: str = "/Users/kishorecm/Documents/EaseLi/Portfolio CSV files/portfolio_history_10y.csv"
    
    # External APIs (optional)
    ALPACA_API_KEY: Optional[str] = None
    ALPACA_SECRET_KEY: Optional[str] = None
    TWELVE_DATA_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "*"]
    
    # Performance
    CACHE_TTL: int = 300  # 5 minutes
    MAX_CONNECTIONS: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s | %(levelname)8s | %(name)s | %(message)s"
    
    @validator("CSV_PATH")
    @classmethod
    def validate_csv_path(cls, v):
        if not Path(v).exists():
            print(f"⚠️  CSV file not found: {v}")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
