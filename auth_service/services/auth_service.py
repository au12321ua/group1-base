"""AuthService — login, token issuance/refresh/revocation, password management."""

import warnings

from sqlmodel.ext.asyncio.session import AsyncSession

from auth_service.schemas.auth_schema import (
    ChangePasswordRequest,
    LoginResponse,
    RefreshTokenResponse,
)
from auth_service.schemas.user_schema import AuthUserResponse


class AuthService:
    """Core authentication business logic."""

    def __init__(self) -> None:
        warnings.warn("TODO: AuthService — implement all methods")

    async def login(
        self, db: AsyncSession, username: str, password: str, client_ip: str = ""
    ) -> LoginResponse:
        """Authenticate user credentials and issue token pair.

        Steps:
        1. Look up credential by username
        2. Check account locked state (locked_until > now → 423)
        3. Verify password hash with bcrypt
        4. On failure: increment failed_count, lock if >= max attempts
        5. On success: reset failed_count, issue access+refresh tokens, create session
        """
        warnings.warn("TODO: implement login flow")
        raise NotImplementedError("login not implemented")

    async def service_login(
        self, db: AsyncSession, client_id: str, client_secret: str
    ) -> "LoginResponse":
        """Authenticate a service (client_id + client_secret) and issue a Service Token.

        Validates against registered service credentials.
        """
        warnings.warn("TODO: implement service_login")
        raise NotImplementedError("service_login not implemented")

    async def logout(self, db: AsyncSession, refresh_token: str) -> None:
        """Revoke the refresh token and end the associated session."""
        warnings.warn("TODO: implement logout")
        raise NotImplementedError("logout not implemented")

    async def refresh_token(
        self, db: AsyncSession, refresh_token: str
    ) -> RefreshTokenResponse:
        """Validate refresh token, revoke old pair, issue new token pair."""
        warnings.warn("TODO: implement refresh_token — rotate token pair")
        raise NotImplementedError("refresh_token not implemented")

    async def get_current_user(
        self, db: AsyncSession, user_id: str
    ) -> AuthUserResponse:
        """Return minimal user info for /auth/me."""
        warnings.warn("TODO: implement get_current_user")
        raise NotImplementedError("get_current_user not implemented")

    async def change_password(
        self, db: AsyncSession, user_id: str, request: ChangePasswordRequest
    ) -> None:
        """Verify old password, validate new password policy, update hash."""
        warnings.warn("TODO: implement change_password")
        raise NotImplementedError("change_password not implemented")

    # ---- Internal endpoints (called by Info Service) ----

    async def create_internal_user(
        self, db: AsyncSession, user_id: str, username: str, role_ids: list[int]
    ) -> AuthUserResponse:
        """Create a minimal auth user record + credential + role assignments."""
        warnings.warn("TODO: implement create_internal_user")
        raise NotImplementedError("create_internal_user not implemented")

    async def disable_user(self, db: AsyncSession, user_id: str) -> None:
        """Set user status to DISABLED."""
        warnings.warn("TODO: implement disable_user")
        raise NotImplementedError("disable_user not implemented")

    async def enable_user(self, db: AsyncSession, user_id: str) -> None:
        """Set user status to ACTIVE."""
        warnings.warn("TODO: implement enable_user")
        raise NotImplementedError("enable_user not implemented")

    async def sync_user_roles(
        self, db: AsyncSession, user_id: str, role_ids: list[int]
    ) -> None:
        """Replace all role assignments for a user."""
        warnings.warn("TODO: implement sync_user_roles")
        raise NotImplementedError("sync_user_roles not implemented")

    async def delete_user(self, db: AsyncSession, user_id: str) -> None:
        """Physical delete: credentials, tokens, sessions, roles — full cleanup."""
        warnings.warn("TODO: implement delete_user — cascade cleanup")
        raise NotImplementedError("delete_user not implemented")


auth_service = AuthService()
