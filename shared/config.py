"""Shared configuration base class for all STSS services."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class SharedSettings(BaseSettings):
    """Base settings with fields common to all services (CORS, logging, env)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    env: str = "development"

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Logging
    log_level: str = "DEBUG"
    log_output: str = "console"
    log_dir: str = "./logs"
    log_rotation: str = "daily"
    log_retention: int = 30
