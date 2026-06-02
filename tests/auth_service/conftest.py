"""Auth Service specific test fixtures and overrides.

All shared fixtures (db sessions, clients) are defined in the root tests/conftest.py.
Place auth-specific fixtures here when needed.
"""

import pytest

from auth_service.core.config import get_auth_settings

_TEST_TOKEN_SECRET = "test-secret-key-for-unit-tests-only-32chars!"


@pytest.fixture
def auth_security_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """固定 JWT 密钥，避免测试依赖本地 .env。"""
    monkeypatch.setenv("TOKEN_SECRET_KEY", _TEST_TOKEN_SECRET)
    get_auth_settings.cache_clear()
    yield
    get_auth_settings.cache_clear()


@pytest.fixture
def auth_service_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    """固定系统服务登录凭据，供 service_login 测试使用。"""
    monkeypatch.setenv("SERVICE_CLIENT_TEST_CLIENT_ID", "test-client")
    monkeypatch.setenv("SERVICE_CLIENT_TEST_CLIENT_SECRET", "test-secret")
    monkeypatch.setenv("SERVICE_CLIENT_TEST_CLIENT_SCOPE", "test:scope")
    monkeypatch.setenv("SERVICE_CLIENT_TEST_CLIENT_AUDIENCE", "test-audience")
    get_auth_settings.cache_clear()
    yield
    get_auth_settings.cache_clear()


@pytest.fixture
async def seeded_auth_user(auth_db_session, auth_security_env):
    """创建可登录的学生用户（含角色与凭据）。"""
    from auth_service.core.security import get_password_hash
    from auth_service.crud.credential_crud import credential_crud
    from auth_service.crud.role_crud import role_crud
    from auth_service.models.permission import Permission, RolePermission
    from auth_service.models.role import Role
    from auth_service.models.user import User

    role = Role(code="STUDENT", name="Student")
    perm = Permission(
        code="course:read",
        name="Read Course",
        resource="course",
        action="read",
    )
    auth_db_session.add(role)
    auth_db_session.add(perm)
    await auth_db_session.flush()
    auth_db_session.add(RolePermission(role_id=role.id, permission_id=perm.id))

    user = User(user_id="seed-u1", username="seeduser")
    auth_db_session.add(user)
    await auth_db_session.flush()

    password_hash, password_salt = get_password_hash("SeedPass1")
    await credential_crud.create(
        auth_db_session,
        user_id="seed-u1",
        username="seeduser",
        password_hash=password_hash,
        password_salt=password_salt,
    )
    await role_crud.assign_roles(auth_db_session, "seed-u1", [role.id])
    return {
        "user_id": "seed-u1",
        "username": "seeduser",
        "password": "SeedPass1",
        "role_id": role.id,
    }
