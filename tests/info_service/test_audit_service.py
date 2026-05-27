"""Unit tests for AuditService."""

import pytest

from info_service.services.audit_service import audit_service


@pytest.mark.unit
class TestAuditService:
    """AuditService unit tests using in-memory audit DB."""

    async def test_write_and_search(self, audit_db_session):
        await audit_service.write_audit_log(
            audit_db_session,
            operator_user_id="user-001",
            operator_role="SYS_ADMIN",
            target_type="user",
            target_id="1",
            action="user_created",
            result="success",
            request_id="req-001",
        )

        items, total = await audit_service.search_audit_logs(audit_db_session)
        assert total == 1
        assert items[0].operator_user_id == "user-001"
        assert items[0].action == "user_created"

    async def test_search_by_operator(self, audit_db_session):
        await audit_service.write_audit_log(
            audit_db_session,
            operator_user_id="user-001",
            operator_role="SYS_ADMIN",
            target_type="user",
            action="user_created",
            result="success",
        )
        await audit_service.write_audit_log(
            audit_db_session,
            operator_user_id="user-002",
            operator_role="TEACHER",
            target_type="course",
            action="course_updated",
            result="success",
        )

        items, total = await audit_service.search_audit_logs(
            audit_db_session, operator_user_id="user-001"
        )
        assert total == 1
        assert items[0].operator_user_id == "user-001"

    async def test_search_by_target_type(self, audit_db_session):
        await audit_service.write_audit_log(
            audit_db_session,
            operator_user_id="user-001",
            operator_role="SYS_ADMIN",
            target_type="user",
            action="user_created",
            result="success",
        )
        await audit_service.write_audit_log(
            audit_db_session,
            operator_user_id="user-001",
            operator_role="SYS_ADMIN",
            target_type="course",
            action="course_created",
            result="success",
        )

        items, total = await audit_service.search_audit_logs(
            audit_db_session, target_type="user"
        )
        assert total == 1
        assert items[0].target_type == "user"

    async def test_search_by_action(self, audit_db_session):
        await audit_service.write_audit_log(
            audit_db_session,
            operator_user_id="user-001",
            operator_role="SYS_ADMIN",
            target_type="user",
            action="user_created",
            result="success",
        )
        await audit_service.write_audit_log(
            audit_db_session,
            operator_user_id="user-001",
            operator_role="SYS_ADMIN",
            target_type="user",
            action="user_deleted",
            result="success",
        )

        items, total = await audit_service.search_audit_logs(
            audit_db_session, action="user_deleted"
        )
        assert total == 1
        assert items[0].action == "user_deleted"

    async def test_search_empty(self, audit_db_session):
        items, total = await audit_service.search_audit_logs(audit_db_session)
        assert items == []
        assert total == 0

    async def test_export_csv(self, audit_db_session):
        await audit_service.write_audit_log(
            audit_db_session,
            operator_user_id="user-001",
            operator_role="SYS_ADMIN",
            target_type="user",
            target_id="1",
            action="user_created",
            result="success",
            request_id="req-001",
        )

        csv_content = await audit_service.export_audit_logs(audit_db_session)
        assert "user-001" in csv_content
        assert "user_created" in csv_content
        assert csv_content.startswith("id,operator_user_id")
