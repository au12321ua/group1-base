"""Shared test utilities — identity headers, data factories, etc."""


# ---------------------------------------------------------------------------
# Identity header builders
# ---------------------------------------------------------------------------


def build_identity_headers(
    user_id: str = "test-user-001",
    role: str = "SYS_ADMIN",
    permissions: list[str] | None = None,
) -> dict[str, str]:
    """Build Gateway-transmitted identity headers for Info Service tests.

    Info Service trusts these headers (set by Gateway after JWT verification)
    and does not hold JWT keys locally.
    """
    if permissions is None:
        permissions = [
            "user:read",
            "user:create",
            "user:update",
            "user:delete",
            "course:read",
            "course:create",
            "course:update",
            "course:delete",
            "offering:read",
            "offering:create",
            "offering:update",
            "offering:delete",
            "schedule:read",
            "schedule:create",
            "schedule:update",
            "schedule:delete",
            "training:read",
            "training:create",
            "training:update",
            "training:delete",
            "calendar:read",
            "calendar:create",
            "calendar:update",
            "calendar:delete",
            "file:read",
            "file:create",
            "file:delete",
            "data-provision:read",
        ]
    return {
        "X-User-Id": user_id,
        "X-User-Role": role,
        "X-User-Permissions": ",".join(permissions),
        "X-Request-ID": f"test-req-{user_id}",
    }


def build_auth_header(token: str) -> dict[str, str]:
    """Build Authorization header with Bearer token (for Auth Service tests)."""
    return {"Authorization": f"Bearer {token}"}


def build_service_token_header(token: str) -> dict[str, str]:
    """Build Authorization header with Bearer service token (for internal endpoint tests)."""
    return {"Authorization": f"Bearer {token}"}


def create_test_service_token(
    client_id: str = "info_service",
    scope: str = "internal",
    audience: str = "auth_service",
) -> str:
    """Create a valid service token for testing internal endpoints."""
    from auth_service.core.security import create_service_token

    return create_service_token(client_id=client_id, scope=scope, audience=audience)


# ---------------------------------------------------------------------------
# Data factories (minimal — expand as tests grow)
# ---------------------------------------------------------------------------


def make_user_payload(
    user_no: str = "S2026001",
    username: str = "testuser",
    full_name: str = "测试用户",
    role_ids: list[int] | None = None,
) -> dict[str, object]:
    """Create a minimal user creation payload."""
    if role_ids is None:
        role_ids = [1]
    return {
        "user_no": user_no,
        "username": username,
        "full_name": full_name,
        "gender": "MALE",
        "email": f"{username}@test.edu.cn",
        "phone": "13800000000",
        "role_ids": role_ids,
    }


def make_course_payload(
    course_code: str = "CS101",
    course_name: str = "Introduction to Computer Science",
    credit: int = 3,
    capacity: int = 80,
    assessment_method: str = "",
) -> dict[str, object]:
    """Create a minimal course creation payload."""
    return {
        "course_code": course_code,
        "course_name": course_name,
        "credit": credit,
        "capacity": capacity,
        "assessment_method": assessment_method,
    }
