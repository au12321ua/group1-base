"""Info Service FastAPI dependencies.

Dependencies in this module are injected into route handlers via Depends().
"""

from fastapi import Header

from shared.exceptions import AuthenticationError
from shared.security import IdentityContext


def _is_missing(value: object) -> bool:
    """True when a dependency value was not provided.

    When called via FastAPI DI, missing headers resolve to None.
    When called directly, the Header(...) default object is passed as-is.
    """
    return value is None or not isinstance(value, str)


async def get_current_user(
    x_user_id: str | None = Header(None, alias="X-User-Id"),
    x_user_role: str | None = Header(None, alias="X-User-Role"),
    x_user_permissions: str | None = Header(None, alias="X-User-Permissions"),
    x_request_id: str | None = Header(None, alias="X-Request-ID"),
) -> IdentityContext:
    """Dependency: resolve current user identity from Gateway-transmitted headers.

    Gateway validates JWT via Auth Service and injects identity headers.
    Info Service trusts these headers without local JWT verification.
    """
    if _is_missing(x_user_id) or not x_user_id:
        raise AuthenticationError("X-User-Id header is required")
    if _is_missing(x_user_role) or not x_user_role:
        raise AuthenticationError("X-User-Role header is required")

    permissions: list[str] = []
    if not _is_missing(x_user_permissions) and x_user_permissions:
        permissions = [p.strip() for p in x_user_permissions.split(",") if p.strip()]

    request_id = x_request_id if not _is_missing(x_request_id) and x_request_id else ""

    return IdentityContext(
        user_id=x_user_id,
        role=x_user_role,
        permissions=permissions,
        request_id=request_id,
    )
