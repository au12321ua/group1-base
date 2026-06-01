"""课程 API 集成测试。"""

import pytest

from tests.info_service.api_helpers import create_course
from tests.utils import build_identity_headers


@pytest.mark.integration
class TestCourseAPI:
    """测试 /api/v1/courses 已实现的 HTTP 参数校验契约。"""

    async def test_list_courses_rejects_invalid_query(
        self, async_client_info, auth_headers
    ) -> None:
        """当分页参数非法时，应在参数校验阶段返回 422。"""
        resp = await async_client_info.get(
            "/api/v1/courses/", params={"page_size": 101}, headers=auth_headers
        )
        assert resp.status_code == 422

    async def test_create_course_rejects_invalid_payload(
        self, async_client_info, auth_headers
    ) -> None:
        """当缺少必填字段时，应在请求体验证阶段返回 422。"""
        resp = await async_client_info.post(
            "/api/v1/courses/",
            json={
                "course_code": "CS101",
                "credit": 3,
                "capacity": 80,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 422

    async def test_create_course_rejects_code_reuse_after_soft_delete(
        self, async_client_info, auth_headers
    ) -> None:
        """逻辑删除后，原 course_code 仍然不可复用。"""
        course_id = await create_course(
            async_client_info,
            course_code="CS200",
            course_name="Reusable Code Check",
        )

        delete_resp = await async_client_info.delete(
            f"/api/v1/courses/{course_id}", headers=auth_headers
        )
        assert delete_resp.status_code == 200

        recreate_resp = await async_client_info.post(
            "/api/v1/courses/",
            json={
                "course_code": "CS200",
                "course_name": "Another Course",
                "credit": 2,
                "capacity": 60,
            },
            headers=auth_headers,
        )
        assert recreate_resp.status_code == 409


@pytest.mark.integration
class TestCourseResourceAccess:
    """验证课程资源级授权：非管理员写操作应返回 403。"""

    async def test_non_admin_cannot_update_course(
        self, async_client_info, auth_headers
    ) -> None:
        """非管理员用户更新课程应返回 403。"""
        course_id = await create_course(
            async_client_info,
            course_code="CS701",
            course_name="Resource Access Test Course",
        )
        student_headers = build_identity_headers(
            user_id="student-1", role="STUDENT", permissions=["course:update"]
        )
        resp = await async_client_info.put(
            f"/api/v1/courses/{course_id}",
            json={
                "course_code": "CS701",
                "course_name": "Hacked Course",
                "credit": 5,
                "capacity": 999,
                "assessment_method": "",
            },
            headers=student_headers,
        )
        assert resp.status_code == 403

    async def test_non_admin_cannot_patch_course(
        self, async_client_info, auth_headers
    ) -> None:
        """非管理员用户部分更新课程应返回 403。"""
        course_id = await create_course(
            async_client_info,
            course_code="CS702",
            course_name="Patch Access Test",
        )
        student_headers = build_identity_headers(
            user_id="student-2", role="STUDENT", permissions=["course:update"]
        )
        resp = await async_client_info.patch(
            f"/api/v1/courses/{course_id}",
            json={"course_name": "Hacked Name"},
            headers=student_headers,
        )
        assert resp.status_code == 403

    async def test_non_admin_cannot_delete_course(
        self, async_client_info, auth_headers
    ) -> None:
        """非管理员用户删除课程应返回 403。"""
        course_id = await create_course(
            async_client_info,
            course_code="CS703",
            course_name="Delete Access Test",
        )
        teacher_headers = build_identity_headers(
            user_id="teacher-1", role="TEACHER", permissions=["course:delete"]
        )
        resp = await async_client_info.delete(
            f"/api/v1/courses/{course_id}", headers=teacher_headers
        )
        assert resp.status_code == 403

    async def test_admin_can_update_course(
        self, async_client_info, auth_headers
    ) -> None:
        """管理员更新课程应成功。"""
        course_id = await create_course(
            async_client_info,
            course_code="CS704",
            course_name="Admin Access Test",
        )
        resp = await async_client_info.put(
            f"/api/v1/courses/{course_id}",
            json={
                "course_code": "CS704",
                "course_name": "Admin Updated Course",
                "credit": 4,
                "capacity": 100,
                "assessment_method": "exam",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
