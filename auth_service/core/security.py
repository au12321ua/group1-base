"""JWT token creation, verification, and password hashing utilities."""

import warnings
from typing import Any


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
    warnings.warn("TODO: implement create_access_token - JWT encoding with HS256")
    # Placeholder — will use python-jose
    raise NotImplementedError("create_access_token not implemented")


def create_refresh_token(user_id: str) -> str:
    """Create a JWT refresh token with longer expiry.

    Payload: {sub, jti, type: "refresh", iat, exp}
    """
    warnings.warn("TODO: implement create_refresh_token - JWT encoding with HS256")
    raise NotImplementedError("create_refresh_token not implemented")


def create_service_token(
    client_id: str,
    scope: str,
    audience: str,
) -> str:
    """Create a JWT service token for inter-service calls.

    Payload: {sub, jti, type: "service", client_id, scope, aud, iat, exp}
    """
    warnings.warn("TODO: implement create_service_token - JWT encoding with HS256")
    raise NotImplementedError("create_service_token not implemented")


def verify_token(token: str) -> dict[str, Any]:
    """Verify and decode a JWT token. Returns the payload dict.

    Raises TokenExpiredError / AuthenticationError on failure.
    """
    warnings.warn("TODO: implement verify_token - JWT decoding with HS256")
    raise NotImplementedError("verify_token not implemented")


def get_password_hash(password: str) -> tuple[str, str]:
    """Hash a password with bcrypt + random salt.

    Returns (password_hash, password_salt).
    """
    warnings.warn("TODO: implement get_password_hash - bcrypt with cost factor")
    raise NotImplementedError("get_password_hash not implemented")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plain password against its bcrypt hash."""
    warnings.warn("TODO: implement verify_password - bcrypt verify")
    raise NotImplementedError("verify_password not implemented")


def generate_key_id() -> str:
    """Generate a unique key ID for JWKS."""
    warnings.warn("TODO: implement generate_key_id")
    raise NotImplementedError("generate_key_id not implemented")
