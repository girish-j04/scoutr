"""
ScoutR Backend Configuration.
Loads settings from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    gemini_api_key: str = ""
    gemini_model_name: str = "gemini-2.5-flash"

    # When True, use built-in mock data instead of local ChromaDB/SQLite/CSV
    use_mock_data: bool = False

    # MongoDB Atlas connection
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "scoutr"

    # Response cache TTL in seconds (default 10 minutes)
    cache_ttl_seconds: int = 600

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
