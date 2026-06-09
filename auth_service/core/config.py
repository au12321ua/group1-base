"""Auth Service configuration via Pydantic Settings."""

import os
import re
from functools import lru_cache

from pydantic import model_validator

from shared.config import SharedSettings


class AuthSettings(SharedSettings):
    """Auth Service settings loaded from environment/.env file."""

    # Database
    auth_database_url: str = "sqlite+aiosqlite:///./data/auth.db"
    audit_database_url: str = "sqlite+aiosqlite:///./data/audit.db"

    # JWT — enable algorithms independently; signing picks one enabled algorithm
    jwt_support_hs256: bool = True
    jwt_support_rs256: bool = False
    jwt_signing_algorithm: str = "HS256"
    token_secret_key: str = "change-me-in-production"
    jwt_hs256_key_id: str = "auth-hs256-key-1"
    jwt_rsa_private_key_pem: str = ""
    jwt_rsa_public_key_pem: str = ""
    jwt_rsa_key_id: str = "auth-rs256-key-1"
    access_token_expire_minutes: int = 15
    admin_access_token_expire_minutes: int = 5
    refresh_token_expire_days: int = 7
    service_token_expire_hours: int = 8

    # Login protection
    max_login_attempts: int = 5
    account_lock_minutes: int = 10

    # Password hashing
    bcrypt_cost_factor: int = 12

    # Internal user provisioning (Info Service → POST /internal/users)
    default_initial_password: str = "ChangeMe123"

    # Service-to-service login (/auth/sys/login) — multi-client via env prefix
    # Pattern: SERVICE_CLIENT_<NAME>_ID|SECRET|SCOPE|AUDIENCE
    service_client_configs: dict[str, dict[str, str]] = {}

    _SERVICE_CLIENT_RE = re.compile(
        r"^SERVICE_CLIENT_(.+?)_(ID|SECRET|SCOPE|AUDIENCE)$"
    )

    @model_validator(mode="after")
    def _populate_service_clients(self) -> "AuthSettings":
        """Scan os.environ for SERVICE_CLIENT_* prefix vars and build config dict."""
        clients: dict[str, dict[str, str]] = {}
        for key, value in os.environ.items():
            m = self._SERVICE_CLIENT_RE.match(key)
            if m:
                name = m.group(1).lower()
                field = m.group(2).lower()
                clients.setdefault(name, {})[field] = value

        for name, cfg in clients.items():
            missing = [f for f in ("id", "secret", "scope", "audience") if f not in cfg]
            if missing:
                raise ValueError(
                    f"Service client '{name}' is missing required fields: "
                    f"{', '.join(f'SERVICE_CLIENT_{name.upper()}_{f.upper()}' for f in missing)}"
                )

        self.service_client_configs = clients
        return self

    @model_validator(mode="after")
    def _validate_jwt_config(self) -> "AuthSettings":
        """Validate JWT algorithm flags and key material."""
        if not self.jwt_support_hs256 and not self.jwt_support_rs256:
            raise ValueError("At least one of JWT_SUPPORT_HS256 / JWT_SUPPORT_RS256 must be true")

        if self.jwt_signing_algorithm not in ("HS256", "RS256"):
            raise ValueError(f"Unsupported JWT_SIGNING_ALGORITHM: {self.jwt_signing_algorithm}")

        if self.jwt_signing_algorithm == "HS256" and not self.jwt_support_hs256:
            raise ValueError("JWT_SIGNING_ALGORITHM=HS256 requires JWT_SUPPORT_HS256=true")
        if self.jwt_signing_algorithm == "RS256" and not self.jwt_support_rs256:
            raise ValueError("JWT_SIGNING_ALGORITHM=RS256 requires JWT_SUPPORT_RS256=true")

        if self.jwt_support_rs256:
            if not self.jwt_rsa_private_key_pem.strip() or not self.jwt_rsa_public_key_pem.strip():
                raise ValueError(
                    "JWT_SUPPORT_RS256=true requires JWT_RSA_PRIVATE_KEY_PEM and "
                    "JWT_RSA_PUBLIC_KEY_PEM"
                )

        return self


@lru_cache
def get_auth_settings() -> AuthSettings:
    return AuthSettings()
