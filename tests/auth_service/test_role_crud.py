"""Tests for RoleCRUD."""

import pytest
from sqlmodel import select

from auth_service.crud.role_crud import role_crud
from auth_service.models.role import Role, UserRole


@pytest.mark.unit
class TestRoleCRUD:
    """测试角色与用户角色关联。"""

    async def test_get_by_id(self, auth_db_session) -> None:
        """应能按主键查询角色。"""
        role = Role(code="STUDENT", name="Student")
        auth_db_session.add(role)
        await auth_db_session.flush()

        found = await role_crud.get_by_id(auth_db_session, role.id)
        assert found is not None
        assert found.code == "STUDENT"
        assert await role_crud.get_by_id(auth_db_session, 99999) is None

    async def test_get_by_code_and_list_active(self, auth_db_session) -> None:
        """应能按 code 查询并列出启用角色。"""
        role = Role(code="TEACHER", name="Teacher", is_active=True)
        inactive = Role(code="LEGACY", name="Legacy", is_active=False)
        auth_db_session.add(role)
        auth_db_session.add(inactive)
        await auth_db_session.flush()

        found = await role_crud.get_by_code(auth_db_session, "TEACHER")
        active_list = await role_crud.list_all(auth_db_session)

        assert found is not None
        assert found.code == "TEACHER"
        assert all(r.is_active for r in active_list)
        assert not any(r.code == "LEGACY" for r in active_list)

    async def test_assign_and_get_user_roles(self, auth_db_session) -> None:
        """应能替换用户角色并查询。"""
        r1 = Role(code="STUDENT", name="Student")
        r2 = Role(code="SYS_ADMIN", name="Admin")
        auth_db_session.add(r1)
        auth_db_session.add(r2)
        await auth_db_session.flush()

        await role_crud.assign_roles(auth_db_session, "user-r1", [r1.id])
        roles = await role_crud.get_user_roles(auth_db_session, "user-r1")
        assert len(roles) == 1
        assert roles[0].code == "STUDENT"

        await role_crud.assign_roles(auth_db_session, "user-r1", [r2.id])
        roles = await role_crud.get_user_roles(auth_db_session, "user-r1")
        assert len(roles) == 1
        assert roles[0].code == "SYS_ADMIN"

    async def test_remove_all_roles(self, auth_db_session) -> None:
        """应能移除用户全部角色。"""
        role = Role(code="STUDENT", name="Student")
        auth_db_session.add(role)
        await auth_db_session.flush()
        await role_crud.assign_roles(auth_db_session, "user-r2", [role.id])

        await role_crud.remove_all_roles(auth_db_session, "user-r2")
        result = await auth_db_session.exec(select(UserRole).where(UserRole.user_id == "user-r2"))
        assert result.first() is None
