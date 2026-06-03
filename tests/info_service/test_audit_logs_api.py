"""审计日志 API 集成测试。"""

import pytest
from sqlmodel import delete
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.main import audit_engine, info_engine
from info_service.models.user import UserInfo
from info_service.models.user_profile import UserProfile
from info_service.services.audit_service import audit_service
from shared.models.audit_log import AuditLog
from tests.utils import build_identity_headers


async def _seed_operator_user(*, user_no: str, username: str, full_name: str) -> None:
    """Insert a user/profile pair for operator_name enrichment assertions."""
    async with AsyncSession(info_engine, expire_on_commit=False) as session:
        user = UserInfo(user_no=user_no, username=username)
        session.add(user)
        await session.flush()
        session.add(
            UserProfile(
                user_id=user.id,
                full_name=full_name,
                email=f"{username}@test.edu.cn",
                phone="13800000000",
                status="ACTIVE",
            )
        )
        await session.commit()


async def _seed_audit_log(
    *,
    operator_user_id: str,
    operator_role: str,
    target_type: str,
    action: str,
    result: str,
    target_id: str = "",
    reason: str = "",
) -> None:
    """Write a real audit log entry into the shared audit DB."""
    async with AsyncSession(audit_engine, expire_on_commit=False) as session:
        await audit_service.write_audit_log(
            session,
            operator_user_id=operator_user_id,
            operator_role=operator_role,
            target_type=target_type,
            target_id=target_id,
            action=action,
            result=result,
            reason=reason,
            request_id=f"req-{operator_user_id}",
        )
        await session.commit()


async def _cleanup_audit_api_tables() -> None:
    """Clear shared tables touched by audit-log API integration tests."""
    async with AsyncSession(audit_engine, expire_on_commit=False) as session:
        await session.exec(delete(AuditLog))
        await session.commit()

    async with AsyncSession(info_engine, expire_on_commit=False) as session:
        await session.exec(delete(UserProfile))
        await session.exec(delete(UserInfo))
        await session.commit()


@pytest.mark.integration
class TestAuditLogsAPI:
    """验证 /api/v1/info/audit-logs 的搜索与导出行为。"""

    @pytest.fixture(autouse=True)
    async def cleanup_tables(self):
        """Ensure stable assertions against the shared in-memory app databases."""
        await _cleanup_audit_api_tables()
        yield
        await _cleanup_audit_api_tables()

    @pytest.fixture
    def audit_headers(self) -> dict[str, str]:
        return build_identity_headers(permissions=["audit:read"])

    @pytest.mark.regression
    async def test_search_audit_logs_enriches_operator_name(
        self, async_client_info, audit_headers
    ) -> None:
        """回归测试：修复 BUG-AUDIT-001 — 审计日志搜索应正确序列化并带上 operator_name。"""
        await _seed_operator_user(
            user_no="AUDIT-OP-001",
            username="audit_operator",
            full_name="审计操作员",
        )
        await _seed_audit_log(
            operator_user_id="AUDIT-OP-001",
            operator_role="SYS_ADMIN",
            target_type="user",
            target_id="42",
            action="user_created",
            result="success",
        )
        await _seed_audit_log(
            operator_user_id="AUDIT-OP-999",
            operator_role="SYS_ADMIN",
            target_type="course",
            target_id="9",
            action="course_created",
            result="success",
        )

        resp = await async_client_info.get(
            "/api/v1/info/audit-logs/",
            params={"action": "user_created", "page": 1, "page_size": 10},
            headers=audit_headers,
        )

        assert resp.status_code == 200
        payload = resp.json()["data"]
        assert payload["pagination"] == {"total": 1, "page": 1, "page_size": 10}
        item = payload["items"][0]
        assert item["operator_user_id"] == "AUDIT-OP-001"
        assert item["operator_name"] == "审计操作员"
        assert item["action"] == "user_created"

    async def test_export_audit_logs_returns_csv(self, async_client_info, audit_headers) -> None:
        """导出接口应返回包含表头和过滤结果的 CSV 内容。"""
        await _seed_audit_log(
            operator_user_id="AUDIT-EXP-001",
            operator_role="SYS_ADMIN",
            target_type="user",
            target_id="7",
            action="user_deleted_logical",
            result="success",
            reason="cleanup",
        )

        resp = await async_client_info.get(
            "/api/v1/info/audit-logs/export",
            params={"operator_user_id": "AUDIT-EXP-001"},
            headers=audit_headers,
        )

        assert resp.status_code == 200
        csv_content = resp.json()["data"]
        assert csv_content.startswith("id,operator_user_id,operator_role")
        assert "AUDIT-EXP-001" in csv_content
        assert "user_deleted_logical" in csv_content
