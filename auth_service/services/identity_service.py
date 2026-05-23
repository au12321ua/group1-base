"""IdentityService — token verification and identity extraction (for Gateway)."""

import re

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_service.core.security import verify_token
from auth_service.crud.permission_crud import permission_crud
from auth_service.crud.role_crud import role_crud
from auth_service.models.user import User, UserStatus
from auth_service.schemas.auth_schema import InternalVerifyRequest, InternalVerifyResponse
from shared.exceptions import AccountDisabledError, AuthenticationError

_SCOPE_SPLIT_RE = re.compile(r"[\s,]+")


def _parse_scope(scope: str) -> list[str]:
    """Parse JWT scope claim (space- or comma-separated permission codes)."""
    return [part for part in _SCOPE_SPLIT_RE.split(scope.strip()) if part]


class IdentityService:
    """Verifies JWT tokens and extracts identity for Gateway."""

    async def verify_token(
        self, db: AsyncSession, request: InternalVerifyRequest
    ) -> InternalVerifyResponse:
        """Verify a JWT (access or service token) and return identity info."""
        payload = verify_token(request.token)
        token_type = payload.get("type", "")
        if token_type not in ("access", "service"):
            raise AuthenticationError(message="Unsupported token type")

        if token_type == "service":
            client_id = str(payload.get("client_id") or payload.get("sub", ""))
            scope = str(payload.get("scope", ""))
            permissions = _parse_scope(scope)
            return InternalVerifyResponse(
                user_id=client_id,
                username=client_id,
                role="SERVICE",
                permissions=permissions,
                token_type=token_type,
            )

        user_id = str(payload.get("sub", ""))
        result = await db.exec(select(User).where(User.user_id == user_id))
        user = result.first()
        if user is None:
            raise AuthenticationError(message="User not found")
        if user.status == UserStatus.DISABLED:
            raise AccountDisabledError()

        roles = await role_crud.get_user_roles(db, user_id)
        role = roles[0].code if roles else str(payload.get("role", "STUDENT"))
        permissions = await permission_crud.get_user_permissions(db, user_id)
        if not permissions and payload.get("permissions"):
            raw = payload["permissions"]
            if isinstance(raw, list):
                permissions = [str(p) for p in raw]

        return InternalVerifyResponse(
            user_id=user.user_id,
            username=user.username,
            role=role,
            permissions=permissions,
            token_type=token_type,
        )


identity_service = IdentityService()
