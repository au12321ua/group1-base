"""校历 API 集成测试。"""

import pytest

from tests.utils import build_identity_headers


@pytest.mark.integration
class TestCalendarAPI:
    """测试 /api/v1/calendars 已实现的 HTTP 参数校验契约。"""

    async def test_list_calendars_rejects_invalid_query(
        self, async_client_info, auth_headers
    ) -> None:
        """当分页参数非法时，应在参数校验阶段返回 422。"""
        resp = await async_client_info.get(
            "/api/v1/calendars/", params={"page": 0}, headers=auth_headers
        )
        assert resp.status_code == 422

    async def test_create_calendar_rejects_invalid_payload(
        self, async_client_info, auth_headers
    ) -> None:
        """当缺少必填字段时，应在请求体验证阶段返回 422。"""
        resp = await async_client_info.post(
            "/api/v1/calendars/",
            json={
                "term_code": "2026-FALL",
                "start_date": "2026-09-01",
                "end_date": "2027-01-20",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 422


@pytest.mark.integration
class TestCalendarResourceAccess:
    """验证校历资源级授权：非管理员写操作应返回 403。"""

    async def test_non_admin_cannot_update_calendar(
        self, async_client_info, auth_headers
    ) -> None:
        """非管理员用户更新校历应返回 403。"""
        create_resp = await async_client_info.post(
            "/api/v1/calendars/",
            json={
                "term_code": "2026-FALL-TEST",
                "term_name": "2026 Fall Semester Test",
                "start_date": "2026-09-01",
                "end_date": "2027-01-15",
            },
            headers=auth_headers,
        )
        cal_id = create_resp.json()["data"]["id"]

        student_headers = build_identity_headers(
            user_id="student-1", role="STUDENT", permissions=["calendar:update"]
        )
        resp = await async_client_info.put(
            f"/api/v1/calendars/{cal_id}",
            json={
                "term_code": "2026-FALL-HACKED",
                "term_name": "Hacked Calendar",
                "start_date": "2026-09-01",
                "end_date": "2027-01-15",
                "version": "1.0",
            },
            headers=student_headers,
        )
        assert resp.status_code == 403
        # Cleanup
        await async_client_info.delete(
            f"/api/v1/calendars/{cal_id}", headers=auth_headers
        )

    async def test_non_admin_cannot_delete_calendar(
        self, async_client_info, auth_headers
    ) -> None:
        """非管理员用户删除校历应返回 403。"""
        create_resp = await async_client_info.post(
            "/api/v1/calendars/",
            json={
                "term_code": "2026-SPRING-TEST",
                "term_name": "2026 Spring Test",
                "start_date": "2026-02-15",
                "end_date": "2026-07-01",
            },
            headers=auth_headers,
        )
        cal_id = create_resp.json()["data"]["id"]

        teacher_headers = build_identity_headers(
            user_id="teacher-1", role="TEACHER", permissions=["calendar:delete"]
        )
        resp = await async_client_info.delete(
            f"/api/v1/calendars/{cal_id}", headers=teacher_headers
        )
        assert resp.status_code == 403
        # Cleanup
        await async_client_info.delete(
            f"/api/v1/calendars/{cal_id}", headers=auth_headers
        )

    async def test_admin_can_update_calendar(
        self, async_client_info, auth_headers
    ) -> None:
        """管理员更新校历应成功。"""
        create_resp = await async_client_info.post(
            "/api/v1/calendars/",
            json={
                "term_code": "2026-WINTER-TEST",
                "term_name": "2026 Winter Test",
                "start_date": "2026-01-01",
                "end_date": "2026-02-28",
            },
            headers=auth_headers,
        )
        cal_id = create_resp.json()["data"]["id"]

        admin_update_headers = build_identity_headers(
            user_id="admin-user", role="SYS_ADMIN", permissions=["calendar:update"]
        )
        resp = await async_client_info.put(
            f"/api/v1/calendars/{cal_id}",
            json={
                "term_code": "2026-WINTER-UPDATED",
                "term_name": "Updated Winter Calendar",
                "start_date": "2026-01-15",
                "end_date": "2026-03-15",
                "version": "2.0",
            },
            headers=admin_update_headers,
        )
        assert resp.status_code == 200
        # Cleanup
        await async_client_info.delete(
            f"/api/v1/calendars/{cal_id}", headers=auth_headers
        )
