"""Identity header reading and permission checking utilities.

Info Service trusts Gateway-transmitted identity headers (X-User-Id, X-User-Role,
X-User-Permissions) and does NOT perform local JWT verification.
"""

from collections.abc import Callable

from fastapi import Header

from shared.exceptions import AuthorizationError, MissingIdentityHeaderError


async def get_current_user_id(
    x_user_id: str | None = Header(None, alias="X-User-Id"),
) -> str:
    """Extract current user ID from Gateway-transmitted header.

    Dependency for FastAPI endpoints. In production, the Gateway guarantees
    this header is present for all authenticated requests.
    """
    if not x_user_id:
        raise MissingIdentityHeaderError("X-User-Id")
    return x_user_id


async def get_current_user_role(
    x_user_role: str | None = Header(None, alias="X-User-Role"),
) -> str:
    """Extract current user role from Gateway-transmitted header."""
    if not x_user_role:
        raise MissingIdentityHeaderError("X-User-Role")
    return x_user_role


async def get_current_user_permissions(
    x_user_permissions: str | None = Header(None, alias="X-User-Permissions"),
) -> list[str]:
    """Extract current user permissions from Gateway-transmitted header.

    Permissions are transmitted as a comma-separated list.
    """
    if not x_user_permissions:
        return []
    return [p.strip() for p in x_user_permissions.split(",")]


def require_permission(permission_code: str) -> Callable:
    """Decorator/factory for permission checks.

    Usage:
        @router.get("/users")
        async def list_users(perms: Annotated[list[str], Depends(require_permission("user:read"))]):
            ...
    """

    def checker(
        permissions: list[str] | None = None,  # noqa: B008
    ) -> list[str]:
        if permissions is None or permission_code not in permissions:
            raise AuthorizationError()
        return permissions

    return checker


class IdentityContext:
    """Holds identity info extracted from Gateway headers for the current request."""

    def __init__(
        self,
        user_id: str,
        role: str,
        permissions: list[str],
        request_id: str = "",
    ) -> None:
        self.user_id = user_id
        self.role = role
        self.permissions = permissions
        self.request_id = request_id

    def has_permission(self, code: str) -> bool:
        """Check if the current identity holds a specific permission."""
        return code in self.permissions

    def has_any_permission(self, *codes: str) -> bool:
        """Check if the current identity holds any of the given permissions."""
        return any(c in self.permissions for c in codes)
