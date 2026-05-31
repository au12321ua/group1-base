"""Info Service FastAPI dependencies.

Dependencies in this module are injected into route handlers via Depends().
"""

from typing import Annotated

from fastapi import Depends, Header

from shared.exceptions import AuthenticationError, AuthorizationError
from shared.security import IdentityContext


def _is_missing(value: object) -> bool:
    """True when a header value was not provided.

    When called directly (unit tests), the default FastAPI ``Header(None)``
    is a ``Header`` object rather than ``None``.  The ``isinstance`` guard
    catches both cases so the dependency works in tests and at runtime.
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


class _PermissionChecker:
    """Callable dependency that checks a specific permission on the current user."""

    def __init__(self, permission_code: str) -> None:
        self._code = permission_code

    def __call__(
        self, current_user: Annotated[IdentityContext, Depends(get_current_user)],
    ) -> IdentityContext:
        if not current_user.has_permission(self._code):
            raise AuthorizationError(
                f"Permission '{self._code}' required"
            )
        return current_user


def require_permission(code: str) -> _PermissionChecker:
    """Create a dependency that requires a specific permission.

    Usage:
        @router.get("/users")
        async def list_users(
            db: InfoDbSession,
            current_user: Annotated[IdentityContext, Depends(require_permission("user:read"))],
        ):
            ...
    """
    return _PermissionChecker(code)


async def require_admin(
    current_user: Annotated[IdentityContext, Depends(get_current_user)],
) -> None:
    """Dependency: require admin role (SYS_ADMIN or ACADEMIC_ADMIN).

    Raises ``AuthorizationError`` if the current user is not an administrator.
    Use as a guard dependency on endpoints that should be admin-only::

        async def delete_course(
            ...,
            current_user: Annotated[IdentityContext, Depends(require_permission("course:delete"))],
            _admin: None = Depends(require_admin),
        ):
            ...
    """
    from info_service.core.security import check_resource_access

    if not check_resource_access(current_user.user_id, current_user.role):
        raise AuthorizationError(
            "Access denied: only administrators can perform this action"
        )
