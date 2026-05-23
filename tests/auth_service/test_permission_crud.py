"""Tests for PermissionCRUD."""

import pytest

from auth_service.crud.permission_crud import permission_crud
from auth_service.crud.role_crud import role_crud
from auth_service.models.permission import Permission, RolePermission
from auth_service.models.role import Role


@pytest.mark.unit
class TestPermissionCRUD:
    """测试权限点与角色权限、用户权限联查。"""

    async def test_get_by_code_and_role_permissions(self, auth_db_session) -> None:
        """应能按 code 查权限并列出角色下权限。"""
        perm = Permission(
            code="user:read",
            name="Read User",
            resource="user",
            action="read",
        )
        role = Role(code="ACADEMIC_ADMIN", name="Academic Admin")
        auth_db_session.add(perm)
        auth_db_session.add(role)
        await auth_db_session.flush()
        auth_db_session.add(RolePermission(role_id=role.id, permission_id=perm.id))
        await auth_db_session.flush()

        found = await permission_crud.get_by_code(auth_db_session, "user:read")
        role_perms = await permission_crud.get_role_permissions(auth_db_session, role.id)

        assert found is not None
        assert len(role_perms) == 1
        assert role_perms[0].code == "user:read"

    async def test_get_user_permissions_via_roles(self, auth_db_session) -> None:
        """应能通过用户角色聚合权限码（去重）。"""
        p1 = Permission(code="course:read", name="C", resource="course", action="read")
        p2 = Permission(code="user:read", name="U", resource="user", action="read")
        role = Role(code="TEACHER", name="Teacher")
        auth_db_session.add(p1)
        auth_db_session.add(p2)
        auth_db_session.add(role)
        await auth_db_session.flush()
        auth_db_session.add(RolePermission(role_id=role.id, permission_id=p1.id))
        auth_db_session.add(RolePermission(role_id=role.id, permission_id=p2.id))
        await auth_db_session.flush()
        await role_crud.assign_roles(auth_db_session, "perm-u1", [role.id])

        codes = await permission_crud.get_user_permissions(auth_db_session, "perm-u1")
        assert set(codes) == {"course:read", "user:read"}
