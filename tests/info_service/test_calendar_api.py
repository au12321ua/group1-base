"""Integration tests for Calendar API contract."""

import pytest


@pytest.mark.integration
class TestCalendarAPI:
    """测试 /api/v1/calendars 已实现的 HTTP 参数校验契约。"""

    async def test_list_calendars_rejects_invalid_query(self, async_client_info) -> None:
        """当分页参数非法时，应在参数校验阶段返回 422。"""
        resp = await async_client_info.get("/api/v1/calendars/", params={"page": 0})
        assert resp.status_code == 422

    async def test_create_calendar_rejects_invalid_payload(self, async_client_info) -> None:
        """当缺少必填字段时，应在请求体验证阶段返回 422。"""
        resp = await async_client_info.post(
            "/api/v1/calendars/",
            json={
                "term_code": "2026-FALL",
                "start_date": "2026-09-01",
                "end_date": "2027-01-20",
            },
        )
        assert resp.status_code == 422
