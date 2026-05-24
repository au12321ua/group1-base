"""Integration tests for Course API contract."""

import pytest


@pytest.mark.integration
class TestCourseAPI:
    """测试 /api/v1/courses 路由契约（当前实现阶段）。"""

    async def test_list_courses_with_valid_query_raises_not_implemented(
        self, async_client_info
    ) -> None:
        """当查询参数合法时，应命中占位实现并抛出 NotImplementedError。"""
        with pytest.raises(NotImplementedError, match="GET /courses not implemented"):
            await async_client_info.get(
                "/api/v1/courses/",
                params={"page": 1, "page_size": 20, "keyword": "CS", "is_active": True},
            )

    async def test_list_courses_rejects_invalid_query(self, async_client_info) -> None:
        """当分页参数非法时，应在参数校验阶段返回 422。"""
        resp = await async_client_info.get("/api/v1/courses/", params={"page_size": 101})
        assert resp.status_code == 422

    async def test_create_course_rejects_invalid_payload(self, async_client_info) -> None:
        """当缺少必填字段时，应在请求体验证阶段返回 422。"""
        resp = await async_client_info.post(
            "/api/v1/courses/",
            json={
                "course_code": "CS101",
                "credit": 3,
                "capacity": 80,
            },
        )
        assert resp.status_code == 422

    async def test_create_course_with_valid_payload_raises_not_implemented(
        self, async_client_info
    ) -> None:
        """当创建载荷合法时，应命中占位实现并抛出 NotImplementedError。"""
        with pytest.raises(NotImplementedError, match="POST /courses not implemented"):
            await async_client_info.post(
                "/api/v1/courses/",
                json={
                    "course_code": "CS101",
                    "course_name": "Intro to CS",
                    "credit": 3,
                    "capacity": 80,
                    "assessment_method": "exam",
                },
            )

    @pytest.mark.parametrize(
        "path, method, payload, match",
        [
            pytest.param(
                "/api/v1/courses/1",
                "get",
                None,
                "GET /courses/{id} not implemented",
                id="get-detail",
            ),
            pytest.param(
                "/api/v1/courses/1",
                "put",
                {
                    "course_code": "CS101",
                    "course_name": "Intro to CS",
                    "credit": 3,
                    "capacity": 80,
                    "assessment_method": "exam",
                    "is_active": True,
                },
                "PUT /courses/{id} not implemented",
                id="put-update",
            ),
            pytest.param(
                "/api/v1/courses/1",
                "patch",
                {"course_name": "Intro to Computer Science"},
                "PATCH /courses/{id} not implemented",
                id="patch-update",
            ),
            pytest.param(
                "/api/v1/courses/1",
                "delete",
                None,
                "DELETE /courses/{id} not implemented",
                id="delete",
            ),
        ],
    )
    async def test_course_crud_endpoints_raise_not_implemented(
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
                await async_client_info.get(path)
            elif method == "put":
                await async_client_info.put(path, json=payload)
            elif method == "patch":
                await async_client_info.patch(path, json=payload)
            elif method == "delete":
                await async_client_info.delete(path)
            else:
                raise AssertionError(f"Unsupported method: {method}")
