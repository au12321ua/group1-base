"""Integration tests for schedule API behavior."""

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.main import info_engine
from info_service.models.classroom import Classroom
from tests.utils import make_course_payload


async def _create_classroom(*, room_no: str, building: str = "Main", capacity: int = 80) -> int:
    """Insert a classroom directly into the Info test database."""
    async with AsyncSession(info_engine, expire_on_commit=False) as session:
        classroom = Classroom(
            room_no=room_no,
            building=building,
            capacity=capacity,
        )
        session.add(classroom)
        await session.commit()
        await session.refresh(classroom)
        return classroom.id


@pytest.mark.integration
class TestScheduleAPI:
    """Verify the /api/v1/schedules CRUD flow and teacher sub-resource."""

    async def test_schedule_crud_and_teacher_assignment_flow(self, async_client_info) -> None:
        """Should manage schedules, detect conflicts, and update teacher assignments."""
        classroom_id = await _create_classroom(room_no="B-201")

        course_resp = await async_client_info.post(
            "/api/v1/courses/",
            json=make_course_payload(
                course_code="CS820",
                course_name="Advanced Scheduling",
            ),
        )
        assert course_resp.status_code == 200
        course_id = course_resp.json()["data"]["id"]

        offering_resp = await async_client_info.post(
            "/api/v1/offerings/",
            json={
                "course_id": course_id,
                "term_code": "2026-FALL",
                "class_no": "01",
                "teacher_ids": [],
                "capacity": 50,
            },
        )
        assert offering_resp.status_code == 200
        offering_id = offering_resp.json()["data"]["id"]

        create_resp = await async_client_info.post(
            "/api/v1/schedules/",
            json={
                "offering_id": offering_id,
                "classroom_id": classroom_id,
                "day_of_week": 2,
                "start_period": 3,
                "end_period": 4,
                "week_range": "1-16",
            },
        )
        assert create_resp.status_code == 200
        created = create_resp.json()["data"]
        schedule_id = created["id"]
        assert created["offering_id"] == offering_id
        assert created["week_range"] == "1-16"

        list_resp = await async_client_info.get(
            "/api/v1/schedules/",
            params={"offering_id": offering_id},
        )
        assert list_resp.status_code == 200
        assert list_resp.json()["data"]["pagination"]["total"] == 1

        get_resp = await async_client_info.get(f"/api/v1/schedules/{schedule_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["classroom_id"] == classroom_id

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
        )
        assert conflict_resp.status_code == 409

        patch_resp = await async_client_info.patch(
            f"/api/v1/schedules/{schedule_id}",
            json={"start_period": 5, "end_period": 6, "week_range": "2-16"},
        )
        assert patch_resp.status_code == 200
        patched = patch_resp.json()["data"]
        assert patched["start_period"] == 5
        assert patched["end_period"] == 6
        assert patched["week_range"] == "2-16"

        replace_resp = await async_client_info.put(
            f"/api/v1/schedules/{schedule_id}/teachers",
            json=["t-1", "t-2"],
        )
        assert replace_resp.status_code == 200
        replaced = replace_resp.json()["data"]["items"]
        assert [item["teacher_id"] for item in replaced] == ["t-1", "t-2"]

        add_resp = await async_client_info.post(
            f"/api/v1/schedules/{schedule_id}/teachers",
            json=["t-2", "t-3"],
        )
        assert add_resp.status_code == 200
        added = add_resp.json()["data"]["items"]
        assert [item["teacher_id"] for item in added] == ["t-1", "t-2", "t-3"]

        assign_resp = await async_client_info.put(
            f"/api/v1/schedules/{schedule_id}/teachers/t-4",
            json={"teacher_id": "t-4", "role_type": "assistant"},
        )
        assert assign_resp.status_code == 200
        assert assign_resp.json()["data"]["role_type"] == "assistant"

        teacher_list_resp = await async_client_info.get(
            f"/api/v1/schedules/{schedule_id}/teachers"
        )
        assert teacher_list_resp.status_code == 200
        teacher_items = teacher_list_resp.json()["data"]["items"]
        assert [item["teacher_id"] for item in teacher_items] == ["t-1", "t-2", "t-3", "t-4"]

        remove_resp = await async_client_info.delete(
            f"/api/v1/schedules/{schedule_id}/teachers/t-2"
        )
        assert remove_resp.status_code == 200

        teacher_list_resp = await async_client_info.get(
            f"/api/v1/schedules/{schedule_id}/teachers"
        )
        assert teacher_list_resp.status_code == 200
        teacher_items = teacher_list_resp.json()["data"]["items"]
        assert [item["teacher_id"] for item in teacher_items] == ["t-1", "t-3", "t-4"]

        delete_resp = await async_client_info.delete(f"/api/v1/schedules/{schedule_id}")
        assert delete_resp.status_code == 200
        assert delete_resp.json()["data"] is None

        missing_resp = await async_client_info.get(f"/api/v1/schedules/{schedule_id}")
        assert missing_resp.status_code == 404

    async def test_create_schedule_rejects_invalid_period_range(self, async_client_info) -> None:
        """Should reject schedules whose end period precedes the start period."""
        classroom_id = await _create_classroom(room_no="B-202")

        course_resp = await async_client_info.post(
            "/api/v1/courses/",
            json=make_course_payload(
                course_code="CS821",
                course_name="Conflict Validation",
            ),
        )
        assert course_resp.status_code == 200
        course_id = course_resp.json()["data"]["id"]

        offering_resp = await async_client_info.post(
            "/api/v1/offerings/",
            json={
                "course_id": course_id,
                "term_code": "2026-FALL",
                "class_no": "02",
                "teacher_ids": [],
                "capacity": 40,
            },
        )
        assert offering_resp.status_code == 200
        offering_id = offering_resp.json()["data"]["id"]

        resp = await async_client_info.post(
            "/api/v1/schedules/",
            json={
                "offering_id": offering_id,
                "classroom_id": classroom_id,
                "day_of_week": 3,
                "start_period": 6,
                "end_period": 5,
            },
        )

        assert resp.status_code == 409

    async def test_patch_schedule_can_change_offering(self, async_client_info) -> None:
        """PATCH should support moving a schedule to another offering."""
        classroom_id = await _create_classroom(room_no="B-203")

        first_course_resp = await async_client_info.post(
            "/api/v1/courses/",
            json=make_course_payload(
                course_code="CS822",
                course_name="Original Offering Course",
            ),
        )
        second_course_resp = await async_client_info.post(
            "/api/v1/courses/",
            json=make_course_payload(
                course_code="CS823",
                course_name="Target Offering Course",
            ),
        )
        assert first_course_resp.status_code == 200
        assert second_course_resp.status_code == 200
        first_course_id = first_course_resp.json()["data"]["id"]
        second_course_id = second_course_resp.json()["data"]["id"]

        first_offering_resp = await async_client_info.post(
            "/api/v1/offerings/",
            json={
                "course_id": first_course_id,
                "term_code": "2026-FALL",
                "class_no": "01",
                "teacher_ids": [],
                "capacity": 40,
            },
        )
        second_offering_resp = await async_client_info.post(
            "/api/v1/offerings/",
            json={
                "course_id": second_course_id,
                "term_code": "2026-FALL",
                "class_no": "02",
                "teacher_ids": [],
                "capacity": 35,
            },
        )
        assert first_offering_resp.status_code == 200
        assert second_offering_resp.status_code == 200
        first_offering_id = first_offering_resp.json()["data"]["id"]
        second_offering_id = second_offering_resp.json()["data"]["id"]

        create_resp = await async_client_info.post(
            "/api/v1/schedules/",
            json={
                "offering_id": first_offering_id,
                "classroom_id": classroom_id,
                "day_of_week": 4,
                "start_period": 7,
                "end_period": 8,
                "week_range": "1-16",
            },
        )
        assert create_resp.status_code == 200
        schedule_id = create_resp.json()["data"]["id"]

        patch_resp = await async_client_info.patch(
            f"/api/v1/schedules/{schedule_id}",
            json={"offering_id": second_offering_id},
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["data"]["offering_id"] == second_offering_id

    async def test_list_teachers_returns_consistent_empty_pagination(
        self, async_client_info
    ) -> None:
        """Teacher list metadata should reflect an empty collection without fake page sizes."""
        classroom_id = await _create_classroom(room_no="B-204")

        course_resp = await async_client_info.post(
            "/api/v1/courses/",
            json=make_course_payload(
                course_code="CS824",
                course_name="Empty Teacher List",
            ),
        )
        assert course_resp.status_code == 200
        course_id = course_resp.json()["data"]["id"]

        offering_resp = await async_client_info.post(
            "/api/v1/offerings/",
            json={
                "course_id": course_id,
                "term_code": "2026-FALL",
                "class_no": "03",
                "teacher_ids": [],
                "capacity": 20,
            },
        )
        assert offering_resp.status_code == 200
        offering_id = offering_resp.json()["data"]["id"]

        schedule_resp = await async_client_info.post(
            "/api/v1/schedules/",
            json={
                "offering_id": offering_id,
                "classroom_id": classroom_id,
                "day_of_week": 5,
                "start_period": 1,
                "end_period": 2,
            },
        )
        assert schedule_resp.status_code == 200
        schedule_id = schedule_resp.json()["data"]["id"]

        resp = await async_client_info.get(f"/api/v1/schedules/{schedule_id}/teachers")
        assert resp.status_code == 200
        assert resp.json()["data"]["pagination"] == {"total": 0, "page": 1, "page_size": 0}
