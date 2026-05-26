"""Integration tests for Course API contract."""

import pytest


@pytest.mark.integration
class TestCourseAPI:
    """测试 /api/v1/courses 已实现的 HTTP 参数校验契约。"""

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

    async def test_create_course_rejects_code_reuse_after_soft_delete(
        self, async_client_info
    ) -> None:
        """逻辑删除后，原 course_code 仍然不可复用。"""
        create_resp = await async_client_info.post(
            "/api/v1/courses/",
            json={
                "course_code": "CS200",
                "course_name": "Reusable Code Check",
                "credit": 3,
                "capacity": 80,
            },
        )
        assert create_resp.status_code == 200
        course_id = create_resp.json()["data"]["id"]

        delete_resp = await async_client_info.delete(f"/api/v1/courses/{course_id}")
        assert delete_resp.status_code == 200

        recreate_resp = await async_client_info.post(
            "/api/v1/courses/",
            json={
                "course_code": "CS200",
                "course_name": "Another Course",
                "credit": 2,
                "capacity": 60,
            },
        )

        assert recreate_resp.status_code == 409
