"""Auth Service configuration via Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    """Auth Service settings loaded from environment/.env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    env: str = "development"

    # Database
    auth_database_url: str = "sqlite:///data/auth.db"
    audit_database_url: str = "sqlite:///data/audit.db"

    # JWT
    token_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    admin_access_token_expire_minutes: int = 5
    refresh_token_expire_days: int = 7
    service_token_expire_hours: int = 8

    # Login protection
    max_login_attempts: int = 5
    account_lock_minutes: int = 10

    # Password hashing
    bcrypt_cost_factor: int = 12

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Logging
    log_level: str = "DEBUG"

    # Internal user provisioning (Info Service → POST /internal/users)
    default_initial_password: str = "ChangeMe123"

    # Service-to-service login (/auth/sys/login)
    service_client_id: str = "info_service"
    service_client_secret: str = "change-me-service-secret"
    service_token_scope: str = "user:read course:read calendar:read"
    service_token_audience: str = "info_service"
    jwt_key_id: str = "auth-hs256-key-1"


@lru_cache
def get_auth_settings() -> AuthSettings:
    return AuthSettings()
