"""Tests for KeyService."""

import pytest

from auth_service.services.key_service import key_service


@pytest.mark.unit
class TestKeyService:
    """测试 JWKS 公钥发布。"""

    def test_get_public_keys_returns_hs256_key(self, auth_security_env: None) -> None:
        """应返回含 kid 与 HS256 算法的 JWKS 条目。"""
        jwks = key_service.get_public_keys()

        assert len(jwks.keys) == 1
        assert jwks.keys[0].alg == "HS256"
        assert jwks.keys[0].kid
        assert jwks.keys[0].kty == "oct"

    def test_rotate_keys_is_noop(self, auth_security_env: None) -> None:
        """原型阶段 rotate_keys 不抛错。"""
        key_service.rotate_keys()
