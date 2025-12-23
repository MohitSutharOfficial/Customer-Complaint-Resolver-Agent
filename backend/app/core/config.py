"""
Customer Complaint Resolver Agent - Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    google_api_key: str = ""  # Gemini API key
    
    # Database (using SQLite for simplicity)
    database_url: str = "sqlite+aiosqlite:///./complaints.db"
    sync_database_url: str = "sqlite:///./complaints.db"
    
    # Redis (optional)
    redis_url: str = "redis://localhost:6379"
    
    # JWT Settings
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # App Settings
    debug: bool = True
    environment: str = "development"
    
    # Agent Settings
    max_retries: int = 3
    confidence_threshold: float = 0.7
    max_response_iterations: int = 3
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
