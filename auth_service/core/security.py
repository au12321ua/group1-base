"""JWT token creation, verification, and password hashing utilities."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import bcrypt
from jose.exceptions import ExpiredSignatureError, JWTError

from auth_service.core.config import get_auth_settings
from auth_service.core.jwt_keys import decode_jwt, encode_jwt
from shared.exceptions import AuthenticationError, TokenExpiredError

_TOKEN_TYPE_ACCESS = "access"
_TOKEN_TYPE_REFRESH = "refresh"
_TOKEN_TYPE_SERVICE = "service"


def _utc_now() -> datetime:
    return datetime.now(UTC)


def create_access_token(
    user_id: str,
    role: str,
    permissions: list[str] | None = None,
    is_admin: bool = False,
) -> str:
    """Create a JWT access token.

    Payload: {sub, jti, type, role, permissions, iat, exp}
    Admin tokens have shorter expiry (ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES).
    """
    settings = get_auth_settings()
    expire_minutes = (
        settings.admin_access_token_expire_minutes
        if is_admin
        else settings.access_token_expire_minutes
    )
    now = _utc_now()
    payload: dict[str, Any] = {
        "sub": user_id,
        "jti": str(uuid4()),
        "type": _TOKEN_TYPE_ACCESS,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=expire_minutes),
    }
    if permissions:
        payload["permissions"] = permissions
    return encode_jwt(payload, settings)


def create_refresh_token(user_id: str) -> str:
    """Create a JWT refresh token with longer expiry.

    Payload: {sub, jti, type: "refresh", iat, exp}
    """
    settings = get_auth_settings()
    now = _utc_now()
    payload: dict[str, Any] = {
        "sub": user_id,
        "jti": str(uuid4()),
        "type": _TOKEN_TYPE_REFRESH,
        "iat": now,
        "exp": now + timedelta(days=settings.refresh_token_expire_days),
    }
    return encode_jwt(payload, settings)


def create_service_token(
    client_id: str,
    audience: str,
) -> str:
    """Create a JWT service token for inter-service calls.

    Payload: {sub, jti, type: "service", client_id, aud, iat, exp}

    Permissions are resolved at verify-time from the SERVICE role in DB,
    not embedded in the token payload.
    """
    settings = get_auth_settings()
    now = _utc_now()
    payload: dict[str, Any] = {
        "sub": client_id,
        "jti": str(uuid4()),
        "type": _TOKEN_TYPE_SERVICE,
        "client_id": client_id,
        "aud": audience,
        "iat": now,
        "exp": now + timedelta(hours=settings.service_token_expire_hours),
    }
    return encode_jwt(payload, settings)


def verify_token(token: str) -> dict[str, Any]:
    """Verify and decode a JWT token. Returns the payload dict.

    Raises TokenExpiredError / AuthenticationError on failure.
    """
    settings = get_auth_settings()
    try:
        return decode_jwt(token, settings)
    except ExpiredSignatureError as exc:
        raise TokenExpiredError() from exc
    except JWTError as exc:
        raise AuthenticationError(message="Invalid token") from exc


def get_password_hash(password: str) -> tuple[str, str]:
    """Hash a password with bcrypt + random salt.

    Returns (password_hash, password_salt).
    """
    settings = get_auth_settings()
    salt = bcrypt.gensalt(rounds=settings.bcrypt_cost_factor)
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    password_salt = salt.decode("utf-8")
    return password_hash, password_salt


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plain password against its bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )
