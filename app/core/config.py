from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings
    """
    # General settings
    PROJECT_NAME: str = "ReadEase API"
    PROJECT_DESCRIPTION: str = "API for accessibility tools for people with dyslexia"
    PROJECT_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Backend URLs
    BACKEND_URL: str = "http://localhost:8000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()