"""Info Service security utilities.

Info Service trusts Gateway-transmitted identity headers and does NOT perform
local JWT verification. This module provides permission-checking helpers.
"""

import warnings


def parse_permissions_header(x_user_permissions: str | None) -> list[str]:
    """Parse comma-separated permissions from X-User-Permissions header."""
    if not x_user_permissions:
        return []
    return [p.strip() for p in x_user_permissions.split(",") if p.strip()]


def check_resource_access(
    current_user_id: str,
    current_role: str,
    resource_owner_id: str | None = None,
    resource_teacher_ids: list[str] | None = None,
) -> bool:
    """Resource-level access control.

    Rules:
    - SYS_ADMIN / ACADEMIC_ADMIN: full access
    - TEACHER: can access if resource_teacher_ids contains current user
    - All: can access own resources
    """
    warnings.warn("TODO: implement check_resource_access — resource-level permission logic")
    admin_roles = {"SYS_ADMIN", "ACADEMIC_ADMIN"}
    if current_role in admin_roles:
        return True
    if resource_owner_id and current_user_id == resource_owner_id:
        return True
    if resource_teacher_ids and current_user_id in resource_teacher_ids:
        return True
    return False
