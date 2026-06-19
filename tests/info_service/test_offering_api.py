"""开课 API 集成测试。"""

import pytest

from tests.info_service.api_helpers import (
    assert_status_and_data,
    create_classroom,
    create_course,
    create_offering,
    create_schedule,
)
from tests.utils import build_identity_headers


@pytest.mark.integration
class TestOfferingAPI:
    """验证 /api/v1/info/offerings 的 CRUD 及关键约束。"""

    async def test_offering_crud_flow(self, async_client_info, auth_headers) -> None:
        """应支持创建、查询、列表、更新和删除开课记录。"""
        course_id = await create_course(
            async_client_info,
            course_code="CS510",
            course_name="Distributed Systems",
            capacity=120,
        )

        create_resp = await async_client_info.post(
            "/api/v1/info/offerings/",
            json={
                "course_id": course_id,
                "term_code": "2026-FALL",
                "class_no": "01",
                "capacity": 80,
            },
            headers=auth_headers,
        )

        created = assert_status_and_data(create_resp)
        assert created["course_id"] == course_id
        offering_id = created["id"]

        list_resp = await async_client_info.get(
            "/api/v1/info/offerings/",
            params={"course_id": course_id, "term_code": "2026-FALL", "status": "ACTIVE"},
            headers=auth_headers,
        )
        assert list_resp.status_code == 200
        payload = list_resp.json()["data"]
        assert payload["pagination"]["total"] == 1
        assert payload["items"][0]["id"] == offering_id

        get_resp = await async_client_info.get(
            f"/api/v1/info/offerings/{offering_id}", headers=auth_headers
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["class_no"] == "01"

        patch_resp = await async_client_info.patch(
            f"/api/v1/info/offerings/{offering_id}",
            json={"status": "COMPLETED"},
            headers=auth_headers,
        )
        assert patch_resp.status_code == 200
        patched = patch_resp.json()["data"]
        assert patched["status"] == "COMPLETED"

        delete_resp = await async_client_info.delete(
            f"/api/v1/info/offerings/{offering_id}", headers=auth_headers
        )
        assert delete_resp.status_code == 200
        assert delete_resp.json()["data"] is None

        missing_resp = await async_client_info.get(
            f"/api/v1/info/offerings/{offering_id}", headers=auth_headers
        )
        assert missing_resp.status_code == 404

    async def test_create_offering_rejects_duplicate_identity(
        self, async_client_info, auth_headers
    ) -> None:
        """当 course_id + term_code + class_no 重复时应返回 409。"""
        course_id = await create_course(
            async_client_info,
            course_code="CS511",
            course_name="Parallel Computing",
            capacity=100,
        )

        first_offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="01",
            capacity=60,
        )
        assert first_offering_id > 0

        duplicate_resp = await async_client_info.post(
            "/api/v1/info/offerings/",
            json={
                "course_id": course_id,
                "term_code": "2026-FALL",
                "class_no": "01",
                "capacity": 60,
            },
            headers=auth_headers,
        )

        assert duplicate_resp.status_code == 409

    async def test_put_offering_applies_full_replacement_defaults(
        self, async_client_info, auth_headers
    ) -> None:
        """PUT 全量更新时，省略可选字段应回落到 schema 默认值。"""
        course_id = await create_course(
            async_client_info,
            course_code="CS512",
            course_name="Software Testing",
        )

        offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="02",
            capacity=88,
        )

        put_resp = await async_client_info.put(
            f"/api/v1/info/offerings/{offering_id}",
            json={
                "course_id": course_id,
                "term_code": "2026-FALL",
                "class_no": "02",
            },
            headers=auth_headers,
        )

        updated = assert_status_and_data(put_resp)
        assert updated["capacity"] == 0
        assert updated["status"] == "ACTIVE"


@pytest.mark.integration
class TestOfferingResourceAccess:
    """验证开课资源级授权：非分配教师且非管理员应被拒绝写操作。"""

    async def test_assigned_teacher_can_update_offering(
        self, async_client_info, auth_headers
    ) -> None:
        """分配到此开课的教师可以更新开课信息。"""
        classroom_id = await create_classroom(room_no="C-601")
        course_id = await create_course(
            async_client_info,
            course_code="CS601",
            course_name="Teacher Access Test",
        )
        offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="01",
            capacity=60,
        )
        schedule_id = await create_schedule(
            async_client_info,
            offering_id=offering_id,
            classroom_id=classroom_id,
            day_of_week=1,
            start_period=3,
            end_period=4,
        )
        # Assign teacher t-100 via the schedule (creates TeacherCourseAssignment)
        await async_client_info.put(
            f"/api/v1/info/schedules/{schedule_id}/teachers/t-100",
            json={"teacher_id": "t-100", "role_type": "instructor"},
            headers=auth_headers,
        )
        teacher_headers = build_identity_headers(
            user_id="t-100", role="TEACHER", permissions=["offering:update"]
        )
        resp = await async_client_info.patch(
            f"/api/v1/info/offerings/{offering_id}",
            json={"status": "COMPLETED"},
            headers=teacher_headers,
        )
        assert resp.status_code == 200

    async def test_non_assigned_teacher_cannot_update_offering(
        self, async_client_info, auth_headers
    ) -> None:
        """未分配到该开课的教师更新开课应返回 403。"""
        classroom_id = await create_classroom(room_no="C-602")
        course_id = await create_course(
            async_client_info,
            course_code="CS602",
            course_name="Unauthorized Teacher Test",
        )
        offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="01",
            capacity=60,
        )
        schedule_id = await create_schedule(
            async_client_info,
            offering_id=offering_id,
            classroom_id=classroom_id,
            day_of_week=1,
            start_period=5,
            end_period=6,
        )
        # Assign teacher t-200 to the offering via schedule, then try to update as t-999
        await async_client_info.post(
            f"/api/v1/info/schedules/{schedule_id}/teachers/t-200",
            json={"teacher_id": "t-200", "role_type": "instructor"},
            headers=auth_headers,
        )
        other_teacher_headers = build_identity_headers(
            user_id="t-999", role="TEACHER", permissions=["offering:update"]
        )
        resp = await async_client_info.patch(
            f"/api/v1/info/offerings/{offering_id}",
            json={"status": "CANCELLED"},
            headers=other_teacher_headers,
        )
        assert resp.status_code == 403

    async def test_student_cannot_delete_offering(
        self, async_client_info, auth_headers
    ) -> None:
        """学生尝试删除开课应返回 403。"""
        course_id = await create_course(
            async_client_info,
            course_code="CS603",
            course_name="Student Delete Test",
        )
        offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="01",
            capacity=60,
        )
        student_headers = build_identity_headers(
            user_id="student-99", role="STUDENT", permissions=["offering:delete"]
        )
        resp = await async_client_info.delete(
            f"/api/v1/info/offerings/{offering_id}", headers=student_headers
        )
        assert resp.status_code == 403

    async def test_admin_can_delete_any_offering(
        self, async_client_info, auth_headers
    ) -> None:
        """管理员可以删除任意开课。"""
        course_id = await create_course(
            async_client_info,
            course_code="CS604",
            course_name="Admin Delete Test",
        )
        offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="01",
            capacity=60,
        )
        admin_delete_headers = build_identity_headers(
            user_id="admin-user", role="SYS_ADMIN", permissions=["offering:delete"]
        )
        resp = await async_client_info.delete(
            f"/api/v1/info/offerings/{offering_id}", headers=admin_delete_headers
        )
        assert resp.status_code == 200


@pytest.mark.integration
class TestOfferingTeachersAPI:
    """验证 /api/v1/info/offerings/{offering_id}/teachers 只读接口。"""

    async def test_list_offering_teachers_returns_assignments(
        self, async_client_info, auth_headers
    ) -> None:
        classroom_id = await create_classroom(room_no="C-701")
        course_id = await create_course(
            async_client_info,
            course_code="CS701",
            course_name="Offering Teachers Test",
        )
        offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="01",
            capacity=60,
        )
        schedule_id = await create_schedule(
            async_client_info,
            offering_id=offering_id,
            classroom_id=classroom_id,
            day_of_week=2,
            start_period=1,
            end_period=2,
        )
        await async_client_info.put(
            f"/api/v1/info/schedules/{schedule_id}/teachers/t-701",
            json={"teacher_id": "t-701", "role_type": "instructor"},
            headers=auth_headers,
        )

        response = await async_client_info.get(
            f"/api/v1/info/offerings/{offering_id}/teachers",
            headers=build_identity_headers(permissions=["offering:read"]),
        )

        assert response.status_code == 200
        payload = response.json()["data"]
        assert payload["pagination"]["total"] == 1
        assert payload["items"][0]["teacher_id"] == "t-701"
        assert payload["items"][0]["offering_id"] == offering_id
        assert payload["items"][0]["role_type"] == "instructor"

    async def test_list_offering_teachers_empty_list(
        self, async_client_info
    ) -> None:
        course_id = await create_course(
            async_client_info,
            course_code="CS702",
            course_name="Offering Teachers Empty Test",
        )
        offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="01",
            capacity=60,
        )

        response = await async_client_info.get(
            f"/api/v1/info/offerings/{offering_id}/teachers",
            headers=build_identity_headers(permissions=["offering:read"]),
        )

        assert response.status_code == 200
        payload = response.json()["data"]
        assert payload["items"] == []
        assert payload["pagination"]["total"] == 0

    async def test_list_offering_teachers_requires_offering_read(
        self, async_client_info
    ) -> None:
        course_id = await create_course(
            async_client_info,
            course_code="CS703",
            course_name="Offering Teachers Permission Test",
        )
        offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="01",
            capacity=60,
        )

        response = await async_client_info.get(
            f"/api/v1/info/offerings/{offering_id}/teachers",
            headers=build_identity_headers(permissions=[]),
        )

        assert response.status_code == 403
