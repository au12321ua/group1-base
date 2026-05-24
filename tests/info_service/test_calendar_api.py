"""Integration tests for Calendar API contract."""

import pytest


@pytest.mark.integration
class TestCalendarAPI:
    """测试 /api/v1/calendars 路由契约（当前实现阶段）。"""

    async def test_list_calendars_with_valid_query_raises_not_implemented(
        self, async_client_info
    ) -> None:
        """当请求参数合法时，应命中占位实现并抛出 NotImplementedError。"""
        with pytest.raises(NotImplementedError, match="GET /calendars not implemented"):
            await async_client_info.get(
                "/api/v1/calendars/",
                params={"page": 1, "page_size": 20},
            )

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

    async def test_create_calendar_with_valid_payload_raises_not_implemented(
        self, async_client_info
    ) -> None:
        """当创建载荷合法时，应命中占位实现并抛出 NotImplementedError。"""
        with pytest.raises(NotImplementedError, match="POST /calendars not implemented"):
            await async_client_info.post(
                "/api/v1/calendars/",
                json={
                    "term_code": "2026-FALL",
                    "term_name": "2026 Fall",
                    "start_date": "2026-09-01",
                    "end_date": "2027-01-20",
                    "version": "1.0",
                },
            )

    @pytest.mark.parametrize(
        "path, method, payload, match",
        [
            pytest.param(
                "/api/v1/calendars/1",
                "get",
                None,
                "GET /calendars/{id} not implemented",
                id="get-detail",
            ),
            pytest.param(
                "/api/v1/calendars/1",
                "put",
                {
                    "term_code": "2026-FALL",
                    "term_name": "2026 Fall",
                    "start_date": "2026-09-01",
                    "end_date": "2027-01-20",
                    "version": "1.1",
                },
                "PUT /calendars/{id} not implemented",
                id="put-update",
            ),
            pytest.param(
                "/api/v1/calendars/1",
                "patch",
                {"term_name": "2026 Fall Updated"},
                "PATCH /calendars/{id} not implemented",
                id="patch-update",
            ),
            pytest.param(
                "/api/v1/calendars/1",
                "delete",
                None,
                "DELETE /calendars/{id} not implemented",
                id="delete",
            ),
            pytest.param(
                "/api/v1/calendars/by-term",
                "get",
                None,
                "GET /calendars/by-term not implemented",
                id="by-term",
            ),
        ],
    )
    async def test_calendar_crud_endpoints_raise_not_implemented(
        self,
        async_client_info,
        path: str,
        method: str,
        payload: dict | None,
        match: str,
    ) -> None:
        """当调用 CRUD 端点时，应命中占位实现并抛出对应异常。"""
        with pytest.raises(NotImplementedError, match=match):
            if method == "get":
                params = {"term_code": "2026-FALL"} if path.endswith("/by-term") else None
                await async_client_info.get(path, params=params)
            elif method == "put":
                await async_client_info.put(path, json=payload)
            elif method == "patch":
                await async_client_info.patch(path, json=payload)
            elif method == "delete":
                await async_client_info.delete(path)
            else:
                raise AssertionError(f"Unsupported method: {method}")
