"""
Application configuration loaded from environment variables (.env).
Centralizing config here avoids scattering os.getenv() calls across the codebase.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./shop.db"

    # JWT
    jwt_secret_key: str = "insecure-dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 720  # 12 hours

    # Admin bootstrap (used once on startup to seed an admin user if none exists)
    admin_mobile: str = "9999999999"
    admin_password: str = "admin123"
    admin_name: str = "Shop Admin"

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance so we parse the .env file only once."""
    return Settings()
