"""课程 API 集成测试。"""

import pytest

from tests.info_service.api_helpers import assert_status_and_data, create_course
from tests.utils import build_identity_headers


@pytest.mark.integration
class TestCourseAPI:
    """测试 /api/v1/info/courses 已实现的 HTTP 参数校验契约。"""

    async def test_list_courses_rejects_invalid_query(
        self, async_client_info, auth_headers
    ) -> None:
        """当分页参数非法时，应在参数校验阶段返回 422。"""
        resp = await async_client_info.get(
            "/api/v1/info/courses/", params={"page_size": 101}, headers=auth_headers
        )
        assert resp.status_code == 422

    async def test_create_course_rejects_invalid_payload(
        self, async_client_info, auth_headers
    ) -> None:
        """当缺少必填字段时，应在请求体验证阶段返回 422。"""
        resp = await async_client_info.post(
            "/api/v1/info/courses/",
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
            f"/api/v1/info/courses/{course_id}", headers=auth_headers
        )
        assert delete_resp.status_code == 200

        recreate_resp = await async_client_info.post(
            "/api/v1/info/courses/",
            json={
                "course_code": "CS200",
                "course_name": "Another Course",
                "credit": 2,
                "capacity": 60,
            },
            headers=auth_headers,
        )
        assert recreate_resp.status_code == 409

    async def test_course_crud_and_prerequisite_flow(
        self, async_client_info, auth_headers
    ) -> None:
        """应支持课程列表、详情、更新与先修课子资源操作。"""
        target_course_id = await create_course(
            async_client_info,
            course_code="CS240",
            course_name="Algorithms",
        )
        prerequisite_course_id = await create_course(
            async_client_info,
            course_code="CS140",
            course_name="Programming Foundations",
        )

        list_resp = await async_client_info.get(
            "/api/v1/info/courses/",
            params={"keyword": "Algorithms", "page": 1, "page_size": 10, "is_active": True},
            headers=auth_headers,
        )
        list_data = assert_status_and_data(list_resp)
        assert list_data["pagination"]["total"] == 1
        assert list_data["items"][0]["id"] == target_course_id

        get_resp = await async_client_info.get(
            f"/api/v1/info/courses/{target_course_id}",
            headers=auth_headers,
        )
        get_data = assert_status_and_data(get_resp)
        assert get_data["course_name"] == "Algorithms"

        put_resp = await async_client_info.put(
            f"/api/v1/info/courses/{target_course_id}",
            json={
                "course_code": "CS240",
                "course_name": "Algorithms and Design",
                "credit": 4,
                "capacity": 90,
                "assessment_method": "exam",
                "is_active": True,
            },
            headers=auth_headers,
        )
        put_data = assert_status_and_data(put_resp)
        assert put_data["course_name"] == "Algorithms and Design"
        assert put_data["assessment_method"] == "exam"

        patch_resp = await async_client_info.patch(
            f"/api/v1/info/courses/{target_course_id}",
            json={"capacity": 95, "assessment_method": "project"},
            headers=auth_headers,
        )
        patch_data = assert_status_and_data(patch_resp)
        assert patch_data["capacity"] == 95
        assert patch_data["assessment_method"] == "project"

        add_prereq_resp = await async_client_info.post(
            f"/api/v1/info/courses/{target_course_id}/prerequisites",
            json={"prerequisite_course_id": prerequisite_course_id, "min_grade": "B"},
            headers=auth_headers,
        )
        prereq_data = assert_status_and_data(add_prereq_resp)
        assert prereq_data["prerequisite_course_id"] == prerequisite_course_id
        assert prereq_data["prerequisite_course_code"] == "CS140"
        assert prereq_data["prerequisite_course_name"] == "Programming Foundations"

        list_prereq_resp = await async_client_info.get(
            f"/api/v1/info/courses/{target_course_id}/prerequisites",
            headers=auth_headers,
        )
        prereq_list = assert_status_and_data(list_prereq_resp)
        assert prereq_list["pagination"]["total"] == 1
        assert prereq_list["items"][0]["min_grade"] == "B"

        remove_prereq_resp = await async_client_info.delete(
            f"/api/v1/info/courses/{target_course_id}/prerequisites/{prerequisite_course_id}",
            headers=auth_headers,
        )
        assert remove_prereq_resp.status_code == 200
        assert remove_prereq_resp.json()["data"] is None

    async def test_remove_missing_prerequisite_returns_409(
        self, async_client_info, auth_headers
    ) -> None:
        """删除不存在的先修课关联时应返回 409。"""
        target_course_id = await create_course(
            async_client_info,
            course_code="CS241",
            course_name="Operating Systems",
        )
        prerequisite_course_id = await create_course(
            async_client_info,
            course_code="CS141",
            course_name="Computer Organization",
        )

        resp = await async_client_info.delete(
            f"/api/v1/info/courses/{target_course_id}/prerequisites/{prerequisite_course_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 409


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
            f"/api/v1/info/courses/{course_id}",
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
            f"/api/v1/info/courses/{course_id}",
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
            f"/api/v1/info/courses/{course_id}", headers=teacher_headers
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
            f"/api/v1/info/courses/{course_id}",
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
