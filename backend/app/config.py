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
    use_mock_data: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Prevent crashes from unrecognized variables


@lru_cache()
def get_settings() -> Settings:
    return Settings()
