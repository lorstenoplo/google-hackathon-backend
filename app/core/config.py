import os
import json

from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv

load_dotenv()

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
    CORS_ORIGINS: List[str] = json.loads(os.environ.get("CORS_ORIGINS", "[]"))
    
    # Backend URLs
    BACKEND_URL: str = os.environ.get("BACKEND_URL", "http://localhost:8000")

    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")

    MISTRAL_API_KEY: str = os.environ.get("MISTRAL_API_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()