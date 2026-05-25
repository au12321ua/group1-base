"""Integration tests for offering API behavior."""

import pytest


@pytest.mark.integration
class TestOfferingAPI:
    """Verify the /api/v1/offerings CRUD flow."""

    async def test_offering_crud_flow(self, async_client_info) -> None:
        """Should create, read, list, patch, and delete an offering."""
        course_resp = await async_client_info.post(
            "/api/v1/courses/",
            json={
                "course_code": "CS510",
                "course_name": "Distributed Systems",
                "credit": 3,
                "capacity": 120,
            },
        )
        assert course_resp.status_code == 200
        course_id = course_resp.json()["data"]["id"]

        create_resp = await async_client_info.post(
            "/api/v1/offerings/",
            json={
                "course_id": course_id,
                "term_code": "2026-FALL",
                "class_no": "01",
                "teacher_ids": ["t-1", "t-2"],
                "capacity": 80,
            },
        )

        assert create_resp.status_code == 200
        created = create_resp.json()["data"]
        assert created["course_id"] == course_id
        assert created["teacher_ids"] == "t-1,t-2"
        offering_id = created["id"]

        list_resp = await async_client_info.get(
            "/api/v1/offerings/",
            params={"course_id": course_id, "term_code": "2026-FALL", "status": "ACTIVE"},
        )
        assert list_resp.status_code == 200
        payload = list_resp.json()["data"]
        assert payload["pagination"]["total"] == 1
        assert payload["items"][0]["id"] == offering_id

        get_resp = await async_client_info.get(f"/api/v1/offerings/{offering_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["class_no"] == "01"

        patch_resp = await async_client_info.patch(
            f"/api/v1/offerings/{offering_id}",
            json={"teacher_ids": ["t-2", "t-3"], "status": "COMPLETED"},
        )
        assert patch_resp.status_code == 200
        patched = patch_resp.json()["data"]
        assert patched["teacher_ids"] == "t-2,t-3"
        assert patched["status"] == "COMPLETED"

        delete_resp = await async_client_info.delete(f"/api/v1/offerings/{offering_id}")
        assert delete_resp.status_code == 200
        assert delete_resp.json()["data"] is None

        missing_resp = await async_client_info.get(f"/api/v1/offerings/{offering_id}")
        assert missing_resp.status_code == 404

    async def test_create_offering_rejects_duplicate_identity(self, async_client_info) -> None:
        """Should reject duplicate course + term + class combinations."""
        course_resp = await async_client_info.post(
            "/api/v1/courses/",
            json={
                "course_code": "CS511",
                "course_name": "Parallel Computing",
                "credit": 3,
                "capacity": 100,
            },
        )
        course_id = course_resp.json()["data"]["id"]

        first_resp = await async_client_info.post(
            "/api/v1/offerings/",
            json={
                "course_id": course_id,
                "term_code": "2026-FALL",
                "class_no": "01",
                "teacher_ids": [],
                "capacity": 60,
            },
        )
        assert first_resp.status_code == 200

        duplicate_resp = await async_client_info.post(
            "/api/v1/offerings/",
            json={
                "course_id": course_id,
                "term_code": "2026-FALL",
                "class_no": "01",
                "teacher_ids": [],
                "capacity": 60,
            },
        )

        assert duplicate_resp.status_code == 409
