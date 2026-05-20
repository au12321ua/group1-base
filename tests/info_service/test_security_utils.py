"""Tests for info_service/core/security.py."""

import pytest

from info_service.core.security import check_resource_access, parse_permissions_header


@pytest.mark.unit
class TestParsePermissionsHeader:
    """测试 X-User-Permissions 请求头解析。"""

    def test_returns_empty_list_when_header_missing(self):
        """当权限头为 None 时，应返回空列表。"""
        assert parse_permissions_header(None) == []

    def test_ignores_blank_items_and_trims_spaces(self):
        """当权限头包含空项与空格时，应过滤空项并去空格。"""
        parsed = parse_permissions_header(" user:read, ,course:write ,, ")
        assert parsed == ["user:read", "course:write"]


@pytest.mark.unit
class TestCheckResourceAccess:
    """测试资源级访问控制规则。"""

    def test_admin_role_has_full_access(self):
        """管理员角色应始终拥有访问权限。"""
        assert check_resource_access("u1", "SYS_ADMIN", resource_owner_id="u2") is True

    def test_owner_can_access_own_resource(self):
        """资源所有者应可以访问自己的资源。"""
        assert check_resource_access("u1", "STUDENT", resource_owner_id="u1") is True

    def test_teacher_in_assignment_can_access(self):
        """教师在教师分配列表中时应可访问。"""
        assert (
            check_resource_access(
                "t-001",
                "TEACHER",
                resource_teacher_ids=["t-002", "t-001"],
            )
            is True
        )

    def test_unrelated_user_cannot_access(self):
        """无管理员角色、非所有者且不在教师分配时应拒绝访问。"""
        assert (
            check_resource_access(
                "u9",
                "STUDENT",
                resource_owner_id="u1",
                resource_teacher_ids=["t-001"],
            )
            is False
        )
