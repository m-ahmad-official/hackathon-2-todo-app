import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # JWT settings
    BETTER_AUTH_SECRET: str = os.getenv("BETTER_AUTH_SECRET", "dev-better-auth-secret-change-in-production")
    BETTER_AUTH_PUBLIC_KEY: str = os.getenv("BETTER_AUTH_PUBLIC_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")  # Changed from RS256 to HS256 for simpler implementation
    JWT_EXPIRATION_DELTA: int = int(os.getenv("JWT_EXPIRATION_DELTA", "604800"))  # 7 days in seconds

    model_config = {"env_file": ".env"}


settings = Settings()