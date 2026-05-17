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


# ---------------------------------------------------------------------------
# Data factories (minimal — expand as tests grow)
# ---------------------------------------------------------------------------


def make_user_payload(
    user_no: str = "S2026001",
    username: str = "testuser",
    full_name: str = "测试用户",
    role_ids: str = "1",
) -> dict:
    """Create a minimal user creation payload."""
    return {
        "user_no": user_no,
        "username": username,
        "full_name": full_name,
        "gender": "MALE",
        "email": f"{username}@test.edu.cn",
        "phone": "13800000000",
        "role_ids": role_ids,
    }
