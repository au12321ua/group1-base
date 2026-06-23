"""Tests for auth_service.core.security — JWT and password hashing."""

from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from auth_service.core.config import get_auth_settings
from auth_service.core.security import (
    create_access_token,
    create_refresh_token,
    create_service_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from shared.exceptions import AuthenticationError, TokenExpiredError

_TEST_TOKEN_SECRET = "test-secret-key-for-unit-tests-only-32chars!"


@pytest.mark.unit
class TestPasswordHashing:
    """测试 bcrypt 密码哈希与校验。"""

    def test_hash_and_verify_roundtrip(self, auth_security_env: None) -> None:
        """哈希后应能用同一明文通过校验。"""
        password_hash, password_salt = get_password_hash("SecurePass1")

        assert password_hash
        assert password_salt
        assert verify_password("SecurePass1", password_hash)
        assert not verify_password("WrongPass1", password_hash)

    def test_verify_wrong_password(self, auth_security_env: None) -> None:
        """错误明文应校验失败。"""
        password_hash, _ = get_password_hash("correct-password")

        assert not verify_password("wrong-password", password_hash)


@pytest.mark.unit
class TestAccessToken:
    """测试 Access Token 签发与验签。"""

    def test_access_token_payload_fields(self, auth_security_env: None) -> None:
        """Access Token 应包含 sub、type、role、jti 等字段。"""
        token = create_access_token(
            user_id="user-001",
            role="STUDENT",
            permissions=["course:read"],
        )
        payload = verify_token(token)

        assert payload["sub"] == "user-001"
        assert payload["type"] == "access"
        assert payload["role"] == "STUDENT"
        assert payload["permissions"] == ["course:read"]
        assert payload["jti"]
        assert payload["iat"]
        assert payload["exp"]

    def test_admin_token_shorter_expiry(self, auth_security_env: None) -> None:
        """管理员 Token 过期时间应短于普通用户。"""
        settings = get_auth_settings()
        user_token = create_access_token("u1", "STUDENT", is_admin=False)
        admin_token = create_access_token("u2", "SYS_ADMIN", is_admin=True)

        user_payload = verify_token(user_token)
        admin_payload = verify_token(admin_token)
        user_exp = datetime.fromtimestamp(user_payload["exp"], tz=UTC)
        admin_exp = datetime.fromtimestamp(admin_payload["exp"], tz=UTC)
        user_iat = datetime.fromtimestamp(user_payload["iat"], tz=UTC)
        admin_iat = datetime.fromtimestamp(admin_payload["iat"], tz=UTC)

        user_ttl = user_exp - user_iat
        admin_ttl = admin_exp - admin_iat
        assert user_ttl == timedelta(minutes=settings.access_token_expire_minutes)
        assert admin_ttl == timedelta(minutes=settings.admin_access_token_expire_minutes)
        assert admin_ttl < user_ttl

    def test_access_token_expired_raises(self, auth_security_env: None) -> None:
        """过期 Token 验签应抛出 TokenExpiredError。"""
        settings = get_auth_settings()
        past = datetime.now(UTC) - timedelta(minutes=1)
        payload = {
            "sub": "user-001",
            "jti": "expired-jti",
            "type": "access",
            "role": "STUDENT",
            "iat": past,
            "exp": past,
        }
        expired_token = jwt.encode(
            payload,
            settings.token_secret_key,
            algorithm=settings.jwt_signing_algorithm,
        )

        with pytest.raises(TokenExpiredError):
            verify_token(expired_token)


@pytest.mark.unit
class TestRefreshToken:
    """测试 Refresh Token。"""

    def test_refresh_token_type_field(self, auth_security_env: None) -> None:
        """Refresh Token 的 type 应为 refresh。"""
        token = create_refresh_token("user-002")
        payload = verify_token(token)

        assert payload["sub"] == "user-002"
        assert payload["type"] == "refresh"


@pytest.mark.unit
class TestServiceToken:
    """测试 Service Token。"""

    def test_service_token_payload(self, auth_security_env: None) -> None:
        """Service Token 应包含 client_id、aud（权限由 DB SERVICE 角色管理，不在 payload 中）。"""
        token = create_service_token(
            client_id="course_arrangement",
            audience="info_service",
        )
        payload = verify_token(token)

        assert payload["type"] == "service"
        assert payload["sub"] == "course_arrangement"
        assert payload["client_id"] == "course_arrangement"
        assert payload["aud"] == "info_service"
        assert "scope" not in payload


@pytest.mark.unit
class TestVerifyTokenErrors:
    """测试验签异常路径。"""

    def test_verify_tampered_token_raises(self, auth_security_env: None) -> None:
        """篡改签名应抛出 AuthenticationError。"""
        token = create_access_token("user-003", "TEACHER")
        parts = token.split(".")
        tampered = f"{parts[0]}.{parts[1]}.invalidsignature"

        with pytest.raises(AuthenticationError):
            verify_token(tampered)

    def test_verify_wrong_secret_raises(self, auth_security_env: None) -> None:
        """使用错误密钥签发的 Token 应验签失败。"""
        token = jwt.encode(
            {"sub": "x", "type": "access", "exp": datetime.now(UTC) + timedelta(hours=1)},
            "wrong-secret",
            algorithm="HS256",
        )

        with pytest.raises(AuthenticationError):
            verify_token(token)


@pytest.mark.unit
class TestRs256Jwt:
    """测试 RS256 签发与验签。"""

    def test_rs256_access_token_roundtrip(self, auth_rs256_env: None) -> None:
        """RS256 Access Token 应能验签并含 kid。"""
        from jose import jwt as jose_jwt

        token = create_access_token("user-rs256", "STUDENT")
        header = jose_jwt.get_unverified_header(token)
        payload = verify_token(token)

        assert header["alg"] == "RS256"
        assert header["kid"] == "test-rs256-key-1"
        assert payload["sub"] == "user-rs256"

    def test_dual_algorithm_verify_hs256_while_signing_rs256(
        self, monkeypatch: pytest.MonkeyPatch, auth_rs256_env: None
    ) -> None:
        """JWT_SUPPORT 双开时，应按 header alg 验签（非仅签发算法）。"""
        monkeypatch.setenv("JWT_SUPPORT_HS256", "true")
        monkeypatch.setenv("TOKEN_SECRET_KEY", _TEST_TOKEN_SECRET)
        get_auth_settings.cache_clear()

        hs256_token = jwt.encode(
            {
                "sub": "dual-u1",
                "type": "access",
                "exp": datetime.now(UTC) + timedelta(hours=1),
            },
            _TEST_TOKEN_SECRET,
            algorithm="HS256",
        )
        assert verify_token(hs256_token)["sub"] == "dual-u1"
