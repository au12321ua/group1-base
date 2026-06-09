"""Auth Service specific test fixtures and overrides.

All shared fixtures (db sessions, clients) are defined in the root tests/conftest.py.
Place auth-specific fixtures here when needed.
"""

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from auth_service.core.config import get_auth_settings

_TEST_TOKEN_SECRET = "test-secret-key-for-unit-tests-only-32chars!"


def _generate_rsa_pem_pair() -> tuple[str, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    return private_pem, public_pem


@pytest.fixture
def auth_security_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """固定 JWT 密钥，避免测试依赖本地 .env。"""
    monkeypatch.setenv("JWT_SUPPORT_HS256", "true")
    monkeypatch.setenv("JWT_SUPPORT_RS256", "false")
    monkeypatch.setenv("JWT_SIGNING_ALGORITHM", "HS256")
    monkeypatch.setenv("TOKEN_SECRET_KEY", _TEST_TOKEN_SECRET)
    get_auth_settings.cache_clear()
    yield
    get_auth_settings.cache_clear()


@pytest.fixture
def auth_rs256_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """RS256 测试用临时 RSA 密钥对。"""
    private_pem, public_pem = _generate_rsa_pem_pair()
    monkeypatch.setenv("JWT_SUPPORT_HS256", "false")
    monkeypatch.setenv("JWT_SUPPORT_RS256", "true")
    monkeypatch.setenv("JWT_SIGNING_ALGORITHM", "RS256")
    monkeypatch.setenv("JWT_RSA_KEY_ID", "test-rs256-key-1")
    monkeypatch.setenv("JWT_RSA_PRIVATE_KEY_PEM", private_pem)
    monkeypatch.setenv("JWT_RSA_PUBLIC_KEY_PEM", public_pem)
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
