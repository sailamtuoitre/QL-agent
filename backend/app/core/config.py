from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Core
    PROJECT_NAME: str = "Restaurant Revenue Analytics Agent"
    API_V1_STR: str = "/api/v1"
    MODE: str = "DEV"  # DEV or PROD
    
    # Security
    SECRET_KEY: str = "unsafe-secret-key-for-dev-only-change-in-prod"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Paths
    DATA_DIR: str = os.path.join(os.getcwd(), "backend", "data")
    RAW_DATA_DIR: str = os.path.join(DATA_DIR, "raw")
    PROCESSED_DATA_DIR: str = os.path.join(DATA_DIR, "processed")
    CHROMA_PERSIST_DIRECTORY: str = os.path.join(DATA_DIR, "chroma_db")

settings = Settings()

# Ensure data directories exist
os.makedirs(settings.RAW_DATA_DIR, exist_ok=True)
os.makedirs(settings.PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
