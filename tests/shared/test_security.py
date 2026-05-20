"""Tests for shared/security.py."""

import pytest

from shared.exceptions import AuthorizationError, MissingIdentityHeaderError
from shared.security import (
    IdentityContext,
    get_current_user_id,
    get_current_user_permissions,
    get_current_user_role,
    require_permission,
)


@pytest.mark.unit
class TestIdentityHeaderDependencies:
    """测试身份请求头解析依赖。"""

    async def test_get_current_user_id_success(self):
        """当 X-User-Id 存在时，应返回原值。"""
        user_id = await get_current_user_id("user-001")
        assert user_id == "user-001"

    async def test_get_current_user_id_missing_raises(self):
        """当 X-User-Id 缺失时，应抛出 MissingIdentityHeaderError。"""
        with pytest.raises(MissingIdentityHeaderError):
            await get_current_user_id(None)

    async def test_get_current_user_role_success(self):
        """当 X-User-Role 存在时，应返回原值。"""
        role = await get_current_user_role("SYS_ADMIN")
        assert role == "SYS_ADMIN"

    async def test_get_current_user_role_missing_raises(self):
        """当 X-User-Role 缺失时，应抛出 MissingIdentityHeaderError。"""
        with pytest.raises(MissingIdentityHeaderError):
            await get_current_user_role(None)

    async def test_get_current_user_permissions_trimmed(self):
        """权限头应按逗号分割并去除首尾空格。"""
        permissions = await get_current_user_permissions("user:read, course:write")
        assert permissions == ["user:read", "course:write"]

    async def test_get_current_user_permissions_empty_returns_list(self):
        """权限头为空时，应返回空列表。"""
        permissions = await get_current_user_permissions(None)
        assert permissions == []


@pytest.mark.unit
class TestPermissionChecker:
    """测试 require_permission 返回的检查器。"""

    def test_checker_returns_permissions_when_authorized(self):
        """当权限包含目标权限时，应返回原权限列表。"""
        checker = require_permission("user:read")
        permissions = checker(["user:read", "user:update"])
        assert permissions == ["user:read", "user:update"]

    def test_checker_raises_when_permission_missing(self):
        """当权限缺失时，应抛出 AuthorizationError。"""
        checker = require_permission("user:delete")
        with pytest.raises(AuthorizationError):
            checker(["user:read"])

    def test_checker_raises_when_permissions_none(self):
        """当权限列表为 None 时，应抛出 AuthorizationError。"""
        checker = require_permission("user:delete")
        with pytest.raises(AuthorizationError):
            checker(None)


@pytest.mark.unit
class TestIdentityContext:
    """测试 IdentityContext 权限判定行为。"""

    def test_has_permission_true(self):
        """当拥有权限时，has_permission 应返回 True。"""
        ctx = IdentityContext("u1", "TEACHER", ["course:read", "course:update"])
        assert ctx.has_permission("course:read") is True

    def test_has_permission_false(self):
        """当缺少权限时，has_permission 应返回 False。"""
        ctx = IdentityContext("u1", "TEACHER", ["course:read"])
        assert ctx.has_permission("course:delete") is False

    def test_has_any_permission_true(self):
        """当候选权限中至少一个命中时，has_any_permission 应返回 True。"""
        ctx = IdentityContext("u1", "TEACHER", ["course:read", "course:update"])
        assert ctx.has_any_permission("user:read", "course:update") is True

    def test_has_any_permission_false(self):
        """当候选权限全部未命中时，has_any_permission 应返回 False。"""
        ctx = IdentityContext("u1", "TEACHER", ["course:read"])
        assert ctx.has_any_permission("user:read", "user:update") is False
