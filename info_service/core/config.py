"""Info Service configuration via Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class InfoSettings(BaseSettings):
    """Info Service settings loaded from environment/.env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    env: str = "development"

    # Database
    info_database_url: str = "sqlite:///data/info.db"
    audit_database_url: str = "sqlite:///logs/audit.db"

    # Auth Service (cross-service calls)
    auth_service_url: str = "http://localhost:8001"
    auth_service_timeout: int = 10  # seconds

    # File upload
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 10
    allowed_upload_types: str = "jpg,jpeg,png,pdf,csv"

    # Logging
    log_level: str = "DEBUG"


@lru_cache()
def get_info_settings() -> InfoSettings:
    return InfoSettings()
