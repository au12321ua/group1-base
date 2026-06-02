"""AuthService — login, token issuance/refresh/revocation, password management."""

import hmac
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_service.core.config import get_auth_settings
from auth_service.core.security import (
    create_access_token,
    create_refresh_token,
    create_service_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from auth_service.core.time_utils import as_utc, utc_now
from auth_service.crud.credential_crud import credential_crud
from auth_service.crud.permission_crud import permission_crud
from auth_service.crud.role_crud import role_crud
from auth_service.crud.session_crud import session_crud
from auth_service.crud.token_crud import token_crud
from auth_service.models.token import TokenType
from auth_service.models.user import User, UserStatus
from auth_service.schemas.auth_schema import (
    ChangePasswordRequest,
    InternalUserResponse,
    LoginResponse,
    RefreshTokenResponse,
    ServiceLoginResponse,
)
from auth_service.schemas.user_schema import AuthUserResponse
from auth_service.services.password_policy import validate_new_password
from shared.exceptions import (
    AccountDisabledError,
    AccountLockedError,
    AuthenticationError,
    BusinessRuleError,
    ResourceNotFoundError,
    ServiceCredentialInvalidError,
    TokenExpiredError,
)

_ADMIN_ROLES = frozenset({"ACADEMIC_ADMIN", "SYS_ADMIN"})
# 与 UserProfile 禁用同步：凭据长期锁定直至管理员启用（见 state_diagram.md）
_CREDENTIAL_DISABLED_LOCK_UNTIL = datetime(2099, 12, 31, 23, 59, 59, tzinfo=UTC)


def _expires_at_from_payload(payload: dict[str, Any]) -> datetime:
    exp = payload["exp"]
    if isinstance(exp, datetime):
        return exp if exp.tzinfo else exp.replace(tzinfo=UTC)
    return datetime.fromtimestamp(int(exp), tz=UTC)


class AuthService:
    """Core authentication business logic."""

    async def _get_user(self, db: AsyncSession, user_id: str) -> User:
        result = await db.exec(select(User).where(User.user_id == user_id))
        user = result.first()
        if user is None:
            raise ResourceNotFoundError("User", user_id)
        return user

    async def _validate_role_ids(self, db: AsyncSession, role_ids: list[int]) -> None:
        """校验 role_id 均存在，避免静默分配无效角色。"""
        for role_id in role_ids:
            if await role_crud.get_by_id(db, role_id) is None:
                raise BusinessRuleError(f"Role not found: {role_id}", code=4040)

    async def _role_codes(self, db: AsyncSession, user_id: str) -> list[str]:
        roles = await role_crud.get_user_roles(db, user_id)
        return [r.code for r in roles]

    async def _issue_token_pair(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        role: str,
        permissions: list[str],
        is_admin: bool,
        client_ip: str = "",
    ) -> tuple[str, str, int]:
        """签发 access/refresh 对，持久化 Token 与 Session，返回 (access, refresh, expires_in)。"""
        access_jwt = create_access_token(
            user_id, role, permissions=permissions, is_admin=is_admin
        )
        refresh_jwt = create_refresh_token(user_id)
        access_payload = verify_token(access_jwt)
        refresh_payload = verify_token(refresh_jwt)

        access_row = await token_crud.create(
            db,
            user_id=user_id,
            token_type=TokenType.ACCESS,
            token_value=access_jwt,
            expires_at=_expires_at_from_payload(access_payload),
        )
        refresh_row = await token_crud.create(
            db,
            user_id=user_id,
            token_type=TokenType.REFRESH,
            token_value=refresh_jwt,
            expires_at=_expires_at_from_payload(refresh_payload),
        )
        await session_crud.create(
            db,
            user_id=user_id,
            access_token_id=access_row.id,
            refresh_token_id=refresh_row.id,
            client_ip=client_ip or None,
        )
        settings = get_auth_settings()
        expires_in = (
            settings.admin_access_token_expire_minutes * 60
            if is_admin
            else settings.access_token_expire_minutes * 60
        )
        return access_jwt, refresh_jwt, expires_in

    async def login(
        self, db: AsyncSession, username: str, password: str, client_ip: str = ""
    ) -> LoginResponse:
        """Authenticate user credentials and issue token pair."""
        settings = get_auth_settings()
        credential = await credential_crud.get_by_username(db, username)
        if credential is None:
            raise AuthenticationError(message="用户名或密码错误")

        now = utc_now()
        if credential.locked_until is not None and as_utc(credential.locked_until) > now:
            raise AccountLockedError()

        user = await self._get_user(db, credential.user_id)
        if user.status == UserStatus.DISABLED:
            raise AccountDisabledError()

        if not verify_password(password, credential.password_hash):
            failed = await credential_crud.increment_failed_count(db, credential.user_id)
            if failed >= settings.max_login_attempts:
                until = now + timedelta(minutes=settings.account_lock_minutes)
                await credential_crud.lock_account(db, credential.user_id, until)
            raise AuthenticationError(message="用户名或密码错误")

        await credential_crud.reset_failed_count(db, credential.user_id)
        role_codes = await self._role_codes(db, user.user_id)
        primary_role = role_codes[0] if role_codes else "STUDENT"
        permissions = await permission_crud.get_user_permissions(db, user.user_id)
        is_admin = bool(_ADMIN_ROLES.intersection(role_codes))

        access, refresh, expires_in = await self._issue_token_pair(
            db,
            user_id=user.user_id,
            role=primary_role,
            permissions=permissions,
            is_admin=is_admin,
            client_ip=client_ip,
        )
        return LoginResponse(
            access_token=access,
            refresh_token=refresh,
            expires_in=expires_in,
            user_id=user.user_id,
            username=user.username,
            role=primary_role,
            permissions=permissions,
        )

    async def service_login(
        self, db: AsyncSession, client_id: str, client_secret: str
    ) -> ServiceLoginResponse:
        """Authenticate a service client and issue a Service Token."""
        settings = get_auth_settings()
        id_ok = hmac.compare_digest(
            client_id.encode("utf-8"),
            settings.service_client_id.encode("utf-8"),
        )
        secret_ok = hmac.compare_digest(
            client_secret.encode("utf-8"),
            settings.service_client_secret.encode("utf-8"),
        )
        if not (id_ok and secret_ok):
            raise ServiceCredentialInvalidError()

        token = create_service_token(
            client_id=client_id,
            scope=settings.service_token_scope,
            audience=settings.service_token_audience,
        )
        payload = verify_token(token)
        await token_crud.create(
            db,
            user_id=client_id,
            token_type=TokenType.SERVICE,
            token_value=token,
            expires_at=_expires_at_from_payload(payload),
        )
        return ServiceLoginResponse(
            service_token=token,
            expires_in=settings.service_token_expire_hours * 3600,
        )

    async def logout(self, db: AsyncSession, refresh_token: str) -> None:
        """Revoke the refresh token and end the associated session."""
        payload = verify_token(refresh_token)
        if payload.get("type") != "refresh":
            raise AuthenticationError(message="Invalid refresh token")

        row = await token_crud.get_by_value(db, refresh_token)
        if row is None or row.revoked_at is not None:
            raise TokenExpiredError()

        await token_crud.revoke(db, row.id)
        session = await session_crud.get_by_refresh_token_id(db, row.id)
        if session is not None:
            await token_crud.revoke(db, session.access_token_id)
            await session_crud.end_session(db, session.id)

    async def refresh_token(self, db: AsyncSession, refresh_token: str) -> RefreshTokenResponse:
        """Validate refresh token, revoke old pair, issue new token pair."""
        payload = verify_token(refresh_token)
        if payload.get("type") != "refresh":
            raise AuthenticationError(message="Invalid refresh token")

        row = await token_crud.get_by_value(db, refresh_token)
        if row is None or row.revoked_at is not None:
            raise TokenExpiredError()

        user = await self._get_user(db, row.user_id)
        if user.status == UserStatus.DISABLED:
            raise AccountDisabledError()

        await token_crud.revoke(db, row.id)
        session = await session_crud.get_by_refresh_token_id(db, row.id)
        if session is not None:
            await token_crud.revoke(db, session.access_token_id)
            await session_crud.end_session(db, session.id)

        role_codes = await self._role_codes(db, user.user_id)
        primary_role = role_codes[0] if role_codes else "STUDENT"
        permissions = await permission_crud.get_user_permissions(db, user.user_id)
        is_admin = bool(_ADMIN_ROLES.intersection(role_codes))

        access, refresh, expires_in = await self._issue_token_pair(
            db,
            user_id=user.user_id,
            role=primary_role,
            permissions=permissions,
            is_admin=is_admin,
        )
        return RefreshTokenResponse(
            access_token=access,
            refresh_token=refresh,
            expires_in=expires_in,
        )

    async def get_current_user(self, db: AsyncSession, user_id: str) -> AuthUserResponse:
        """Return user info with role and permissions for /auth/me."""
        user = await self._get_user(db, user_id)
        role_codes = await self._role_codes(db, user_id)
        primary_role = role_codes[0] if role_codes else "STUDENT"
        permissions = await permission_crud.get_user_permissions(db, user_id)
        return AuthUserResponse(
            user_id=user.user_id,
            username=user.username,
            status=user.status.value,
            role=primary_role,
            permissions=permissions,
            created_at=user.created_at,
        )

    async def change_password(
        self, db: AsyncSession, user_id: str, request: ChangePasswordRequest
    ) -> None:
        """Verify old password, validate new password policy, update hash."""
        credential = await credential_crud.get_by_user_id(db, user_id)
        if credential is None:
            raise ResourceNotFoundError("Credential", user_id)

        if not verify_password(request.old_password, credential.password_hash):
            raise AuthenticationError(message="旧密码错误", code=1005)

        role_codes = await self._role_codes(db, user_id)
        validate_new_password(request.new_password, role_codes)
        password_hash, password_salt = get_password_hash(request.new_password)
        await credential_crud.update_password(db, user_id, password_hash, password_salt)

    async def create_internal_user(
        self, db: AsyncSession, user_id: str, username: str, role_ids: list[int]
    ) -> InternalUserResponse:
        """Create a minimal auth user record + credential + role assignments."""
        existing_id = await db.exec(select(User).where(User.user_id == user_id))
        if existing_id.first() is not None:
            raise BusinessRuleError(f"User already exists: {user_id}", code=4090)
        existing_name = await db.exec(select(User).where(User.username == username))
        if existing_name.first() is not None:
            raise BusinessRuleError(f"Username already exists: {username}", code=4090)

        user = User(user_id=user_id, username=username, status=UserStatus.ACTIVE)
        db.add(user)
        await db.flush()

        settings = get_auth_settings()
        password_hash, password_salt = get_password_hash(settings.default_initial_password)
        await credential_crud.create(
            db,
            user_id=user_id,
            username=username,
            password_hash=password_hash,
            password_salt=password_salt,
        )
        if role_ids:
            await self._validate_role_ids(db, role_ids)
            await role_crud.assign_roles(db, user_id, role_ids)

        return InternalUserResponse(
            user_id=user.user_id,
            username=user.username,
            status=user.status.value,
        )

    async def disable_user(self, db: AsyncSession, user_id: str) -> None:
        """Set user status to DISABLED and lock credential (sync with UserProfile)."""
        user = await self._get_user(db, user_id)
        user.status = UserStatus.DISABLED
        db.add(user)
        await db.flush()
        await credential_crud.lock_account(db, user_id, _CREDENTIAL_DISABLED_LOCK_UNTIL)

    async def enable_user(self, db: AsyncSession, user_id: str) -> None:
        """Set user status to ACTIVE and unlock credential."""
        user = await self._get_user(db, user_id)
        user.status = UserStatus.ACTIVE
        db.add(user)
        await db.flush()
        await credential_crud.unlock_account(db, user_id)
        await credential_crud.reset_failed_count(db, user_id)

    async def sync_user_roles(
        self, db: AsyncSession, user_id: str, role_ids: list[int]
    ) -> list[int]:
        """Replace all role assignments for a user. Returns synced role_ids."""
        await self._get_user(db, user_id)
        await self._validate_role_ids(db, role_ids)
        await role_crud.assign_roles(db, user_id, role_ids)
        return role_ids

    async def delete_user(self, db: AsyncSession, user_id: str) -> None:
        """Physical delete: credentials, tokens, sessions, roles — full cleanup."""
        user = await self._get_user(db, user_id)
        await session_crud.delete_by_user(db, user_id)
        await token_crud.delete_by_user(db, user_id)
        await role_crud.remove_all_roles(db, user_id)
        await credential_crud.delete(db, user_id)
        await db.delete(user)
        await db.flush()


auth_service = AuthService()
