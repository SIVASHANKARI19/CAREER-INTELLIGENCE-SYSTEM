import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./career_intelligence.db"
    JWT_SECRET: str = "super-secret-jwt-key-change-in-production-123456789"
    ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRY_DAYS: int = 7
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
    GEMINI_API_KEY: str = ""
    GITHUB_TOKEN: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
