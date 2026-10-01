import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "RESQ | Intelligent Disaster Response Coordination Platform"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "resq_secure_operations_eoc_secret_key_2026_super_secure")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database URL: PostgreSQL in production, SQLite fallback in local/tests
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./resq.db")
    
    # Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    # Simulation defaults
    DEFAULT_CITY: str = "Suryanagar, India"
    CITY_LAT: float = 16.5062
    CITY_LNG: float = 80.6480

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
