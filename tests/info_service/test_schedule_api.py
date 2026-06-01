"""排课 API 集成测试。"""

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
class TestScheduleAPI:
    """验证 /api/v1/schedules 的 CRUD 与教师分配行为。"""

    async def test_schedule_crud_and_teacher_assignment_flow(
        self, async_client_info, auth_headers
    ) -> None:
        """应支持排课 CRUD、冲突检测与教师分配子资源操作。"""
        classroom_id = await create_classroom(room_no="B-201")
        course_id = await create_course(
            async_client_info,
            course_code="CS820",
            course_name="Advanced Scheduling",
        )
        offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="01",
            capacity=50,
        )

        schedule_id = await create_schedule(
            async_client_info,
            offering_id=offering_id,
            classroom_id=classroom_id,
            day_of_week=2,
            start_period=3,
            end_period=4,
            week_range="1-16",
        )

        list_resp = await async_client_info.get(
            "/api/v1/schedules/",
            params={"offering_id": offering_id},
            headers=auth_headers,
        )
        assert list_resp.status_code == 200
        assert list_resp.json()["data"]["pagination"]["total"] == 1

        get_resp = await async_client_info.get(
            f"/api/v1/schedules/{schedule_id}", headers=auth_headers
        )
        schedule_data = assert_status_and_data(get_resp)
        assert schedule_data["classroom_id"] == classroom_id
        assert schedule_data["week_range"] == "1-16"

        conflict_resp = await async_client_info.post(
            "/api/v1/schedules/",
            json={
                "offering_id": offering_id,
                "classroom_id": classroom_id,
                "day_of_week": 2,
                "start_period": 4,
                "end_period": 5,
                "week_range": "1-16",
            },
            headers=auth_headers,
        )
        assert conflict_resp.status_code == 409

        patch_resp = await async_client_info.patch(
            f"/api/v1/schedules/{schedule_id}",
            json={"start_period": 5, "end_period": 6, "week_range": "2-16"},
            headers=auth_headers,
        )
        patched = assert_status_and_data(patch_resp)
        assert patched["start_period"] == 5
        assert patched["end_period"] == 6
        assert patched["week_range"] == "2-16"

        replace_resp = await async_client_info.put(
            f"/api/v1/schedules/{schedule_id}/teachers",
            json=["t-1", "t-2"],
            headers=auth_headers,
        )
        replaced = assert_status_and_data(replace_resp)["items"]
        assert [item["teacher_id"] for item in replaced] == ["t-1", "t-2"]

        add_resp = await async_client_info.post(
            f"/api/v1/schedules/{schedule_id}/teachers",
            json=["t-2", "t-3"],
            headers=auth_headers,
        )
        added = assert_status_and_data(add_resp)["items"]
        assert [item["teacher_id"] for item in added] == ["t-1", "t-2", "t-3"]

        assign_resp = await async_client_info.put(
            f"/api/v1/schedules/{schedule_id}/teachers/t-4",
            json={"teacher_id": "t-4", "role_type": "assistant"},
            headers=auth_headers,
        )
        assigned = assert_status_and_data(assign_resp)
        assert assigned["role_type"] == "assistant"

        teacher_list_resp = await async_client_info.get(
            f"/api/v1/schedules/{schedule_id}/teachers", headers=auth_headers
        )
        teacher_items = assert_status_and_data(teacher_list_resp)["items"]
        assert [item["teacher_id"] for item in teacher_items] == ["t-1", "t-2", "t-3", "t-4"]

        remove_resp = await async_client_info.delete(
            f"/api/v1/schedules/{schedule_id}/teachers/t-2", headers=auth_headers
        )
        assert remove_resp.status_code == 200

        teacher_list_resp = await async_client_info.get(
            f"/api/v1/schedules/{schedule_id}/teachers", headers=auth_headers
        )
        teacher_items = assert_status_and_data(teacher_list_resp)["items"]
        assert [item["teacher_id"] for item in teacher_items] == ["t-1", "t-3", "t-4"]

        delete_resp = await async_client_info.delete(
            f"/api/v1/schedules/{schedule_id}", headers=auth_headers
        )
        assert delete_resp.status_code == 200
        assert delete_resp.json()["data"] is None

        missing_resp = await async_client_info.get(
            f"/api/v1/schedules/{schedule_id}", headers=auth_headers
        )
        assert missing_resp.status_code == 404

    async def test_create_schedule_rejects_invalid_period_range(
        self, async_client_info, auth_headers
    ) -> None:
        """当 end_period 小于 start_period 时应返回 409。"""
        classroom_id = await create_classroom(room_no="B-202")
        course_id = await create_course(
            async_client_info,
            course_code="CS821",
            course_name="Conflict Validation",
        )
        offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="02",
            capacity=40,
        )

        resp = await async_client_info.post(
            "/api/v1/schedules/",
            json={
                "offering_id": offering_id,
                "classroom_id": classroom_id,
                "day_of_week": 3,
                "start_period": 6,
                "end_period": 5,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 409

    async def test_patch_schedule_can_change_offering(
        self, async_client_info, auth_headers
    ) -> None:
        """PATCH 应支持将排课调整到其他开课记录。"""
        classroom_id = await create_classroom(room_no="B-203")
        first_course_id = await create_course(
            async_client_info,
            course_code="CS822",
            course_name="Original Offering Course",
        )
        second_course_id = await create_course(
            async_client_info,
            course_code="CS823",
            course_name="Target Offering Course",
        )

        first_offering_id = await create_offering(
            async_client_info,
            course_id=first_course_id,
            term_code="2026-FALL",
            class_no="01",
            capacity=40,
        )
        second_offering_id = await create_offering(
            async_client_info,
            course_id=second_course_id,
            term_code="2026-FALL",
            class_no="02",
            capacity=35,
        )

        schedule_id = await create_schedule(
            async_client_info,
            offering_id=first_offering_id,
            classroom_id=classroom_id,
            day_of_week=4,
            start_period=7,
            end_period=8,
            week_range="1-16",
        )

        patch_resp = await async_client_info.patch(
            f"/api/v1/schedules/{schedule_id}",
            json={"offering_id": second_offering_id},
            headers=auth_headers,
        )
        patched = assert_status_and_data(patch_resp)
        assert patched["offering_id"] == second_offering_id

    async def test_assign_teacher_rejects_path_body_mismatch(
        self, async_client_info, auth_headers
    ) -> None:
        """路径 teacher_id 与 body teacher_id 不一致时应返回 409。"""
        classroom_id = await create_classroom(room_no="B-205")
        course_id = await create_course(
            async_client_info,
            course_code="CS825",
            course_name="Teacher ID Validation",
        )
        offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="04",
            capacity=20,
        )
        schedule_id = await create_schedule(
            async_client_info,
            offering_id=offering_id,
            classroom_id=classroom_id,
            day_of_week=2,
            start_period=1,
            end_period=2,
        )

        resp = await async_client_info.put(
            f"/api/v1/schedules/{schedule_id}/teachers/t-6",
            json={"teacher_id": "t-7", "role_type": "assistant"},
            headers=auth_headers,
        )
        assert resp.status_code == 409

    async def test_list_schedules_rejects_invalid_pagination(
        self, async_client_info, auth_headers
    ) -> None:
        """分页参数非法时应返回 422。"""
        resp = await async_client_info.get(
            "/api/v1/schedules/", params={"page": 0}, headers=auth_headers
        )
        assert resp.status_code == 422


@pytest.mark.integration
class TestScheduleResourceAccess:
    """验证排课资源级授权：只有关联开课的分配教师或管理员可以修改排课。"""

    async def test_assigned_teacher_can_update_schedule(
        self, async_client_info, auth_headers
    ) -> None:
        """关联开课的分配教师可以更新排课。"""
        classroom_id = await create_classroom(room_no="C-301")
        course_id = await create_course(
            async_client_info, course_code="CS901", course_name="Schedule Auth Test"
        )
        offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="01",
            capacity=50,
        )
        schedule_id = await create_schedule(
            async_client_info,
            offering_id=offering_id,
            classroom_id=classroom_id,
            day_of_week=1,
            start_period=1,
            end_period=2,
        )
        # Assign the teacher to the schedule (creates TeacherCourseAssignment)
        await async_client_info.put(
            f"/api/v1/schedules/{schedule_id}/teachers/t-auth-1",
            json={"teacher_id": "t-auth-1", "role_type": "instructor"},
            headers=auth_headers,
        )
        teacher_headers = build_identity_headers(
            user_id="t-auth-1", role="TEACHER", permissions=["schedule:update"]
        )
        resp = await async_client_info.patch(
            f"/api/v1/schedules/{schedule_id}",
            json={"week_range": "1-8"},
            headers=teacher_headers,
        )
        assert resp.status_code == 200

    async def test_non_assigned_teacher_cannot_update_schedule(
        self, async_client_info, auth_headers
    ) -> None:
        """未分配到关联开课的教师更新排课应返回 403。"""
        classroom_id = await create_classroom(room_no="C-302")
        course_id = await create_course(
            async_client_info, course_code="CS902", course_name="Schedule Deny Test"
        )
        offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="01",
            capacity=50,
        )
        schedule_id = await create_schedule(
            async_client_info,
            offering_id=offering_id,
            classroom_id=classroom_id,
            day_of_week=3,
            start_period=5,
            end_period=6,
        )
        other_teacher_headers = build_identity_headers(
            user_id="t-unauthorized", role="TEACHER", permissions=["schedule:update"]
        )
        resp = await async_client_info.patch(
            f"/api/v1/schedules/{schedule_id}",
            json={"day_of_week": 4},
            headers=other_teacher_headers,
        )
        assert resp.status_code == 403

    async def test_student_cannot_delete_schedule(
        self, async_client_info, auth_headers
    ) -> None:
        """学生尝试删除排课应返回 403。"""
        classroom_id = await create_classroom(room_no="C-303")
        course_id = await create_course(
            async_client_info, course_code="CS903", course_name="Student Schedule Test"
        )
        offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="01",
            capacity=40,
        )
        schedule_id = await create_schedule(
            async_client_info,
            offering_id=offering_id,
            classroom_id=classroom_id,
            day_of_week=5,
            start_period=7,
            end_period=8,
        )
        student_headers = build_identity_headers(
            user_id="student-1", role="STUDENT", permissions=["schedule:delete"]
        )
        resp = await async_client_info.delete(
            f"/api/v1/schedules/{schedule_id}", headers=student_headers
        )
        assert resp.status_code == 403

    async def test_non_assigned_cannot_manage_teachers(
        self, async_client_info, auth_headers
    ) -> None:
        """未分配教师不能管理排课教师分配。"""
        classroom_id = await create_classroom(room_no="C-304")
        course_id = await create_course(
            async_client_info, course_code="CS904", course_name="Teacher Mgmt Test"
        )
        offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="01",
            capacity=50,
        )
        schedule_id = await create_schedule(
            async_client_info,
            offering_id=offering_id,
            classroom_id=classroom_id,
            day_of_week=1,
            start_period=1,
            end_period=2,
        )
        other_headers = build_identity_headers(
            user_id="t-other", role="TEACHER", permissions=["schedule:update"]
        )
        resp = await async_client_info.put(
            f"/api/v1/schedules/{schedule_id}/teachers",
            json=["t-other"],
            headers=other_headers,
        )
        assert resp.status_code == 403

    async def test_admin_can_delete_schedule(
        self, async_client_info, auth_headers
    ) -> None:
        """管理员可以删除任意排课。"""
        classroom_id = await create_classroom(room_no="C-305")
        course_id = await create_course(
            async_client_info, course_code="CS905", course_name="Admin Schedule Test"
        )
        offering_id = await create_offering(
            async_client_info,
            course_id=course_id,
            term_code="2026-FALL",
            class_no="01",
            capacity=40,
        )
        schedule_id = await create_schedule(
            async_client_info,
            offering_id=offering_id,
            classroom_id=classroom_id,
            day_of_week=2,
            start_period=3,
            end_period=4,
        )
        admin_delete_headers = build_identity_headers(
            user_id="admin-user", role="SYS_ADMIN", permissions=["schedule:delete"]
        )
        resp = await async_client_info.delete(
            f"/api/v1/schedules/{schedule_id}", headers=admin_delete_headers
        )
        assert resp.status_code == 200
