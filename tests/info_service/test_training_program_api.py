"""Integration tests for training program API behavior."""

import pytest


@pytest.mark.integration
class TestTrainingProgramAPI:
    """Verify the /api/v1/training-programs CRUD flow."""

    async def test_training_program_crud_flow(self, async_client_info) -> None:
        """Should create, query, update, and delete a training program."""
        course_resp = await async_client_info.post(
            "/api/v1/courses/",
            json={
                "course_code": "CS610",
                "course_name": "Machine Learning Systems",
                "credit": 4,
                "capacity": 80,
            },
        )
        assert course_resp.status_code == 200
        course_id = course_resp.json()["data"]["id"]

        create_resp = await async_client_info.post(
            "/api/v1/training-programs/",
            json={
                "program_code": "CS-AI-2026",
                "major_code": "CS",
                "grade": "2026",
                "version": "1.0",
                "required_course_ids": [course_id],
            },
        )

        assert create_resp.status_code == 200
        created = create_resp.json()["data"]
        assert created["program_code"] == "CS-AI-2026"
        assert created["required_course_ids"] == str(course_id)
        program_id = created["id"]

        list_resp = await async_client_info.get("/api/v1/training-programs/")
        assert list_resp.status_code == 200
        assert list_resp.json()["data"]["pagination"]["total"] == 1

        by_major_resp = await async_client_info.get(
            "/api/v1/training-programs/by-major",
            params={"major_code": "CS", "grade": "2026"},
        )
        assert by_major_resp.status_code == 200
        assert by_major_resp.json()["data"]["items"][0]["id"] == program_id

        get_resp = await async_client_info.get(f"/api/v1/training-programs/{program_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["major_code"] == "CS"

        patch_resp = await async_client_info.patch(
            f"/api/v1/training-programs/{program_id}",
            json={"version": "2.0", "required_course_ids": [course_id]},
        )
        assert patch_resp.status_code == 200
        patched = patch_resp.json()["data"]
        assert patched["version"] == "2.0"
        assert patched["required_course_ids"] == str(course_id)

        delete_resp = await async_client_info.delete(f"/api/v1/training-programs/{program_id}")
        assert delete_resp.status_code == 200
        assert delete_resp.json()["data"] is None

        missing_resp = await async_client_info.get(f"/api/v1/training-programs/{program_id}")
        assert missing_resp.status_code == 404

    async def test_create_training_program_rejects_unknown_course(self, async_client_info) -> None:
        """Should reject snapshots referencing non-existent courses."""
        resp = await async_client_info.post(
            "/api/v1/training-programs/",
            json={
                "program_code": "CS-AI-2027",
                "major_code": "CS",
                "grade": "2027",
                "version": "1.0",
                "required_course_ids": [9999],
            },
        )

        assert resp.status_code == 404
