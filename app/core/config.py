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

    SERVICE_ACCOUNT_FILE: str = os.environ.get("SERVICE_ACCOUNT_FILE", "")
    GOOGLE_CLOUD_PROJECT: str = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
    GOOGLE_CLOUD_LOCATION: str = os.environ.get("GOOGLE_CLOUD_LOCATION", "")
    GOOGLE_GENAI_USE_VERTEXAI: str = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "")

    TESSERACT_PATH: str = os.environ.get("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()