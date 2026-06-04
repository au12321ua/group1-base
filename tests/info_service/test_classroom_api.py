"""Classroom API integration tests."""

import pytest

from tests.info_service.api_helpers import assert_status_and_data
from tests.utils import build_identity_headers


def _classroom_headers(*, role: str = "SYS_ADMIN") -> dict[str, str]:
    return build_identity_headers(
        user_id=f"{role.lower()}-classroom",
        role=role,
        permissions=[f"classroom:{action}" for action in ("read", "create", "update", "delete")],
    )


@pytest.mark.integration
class TestClassroomAPI:
    """Validate /api/v1/info/classrooms behavior."""

    async def test_classroom_crud_and_filters(self, async_client_info) -> None:
        """Classroom endpoints should support CRUD plus list filters."""
        headers = _classroom_headers()

        create_resp = await async_client_info.post(
            "/api/v1/info/classrooms/",
            json={
                "room_no": "A-101",
                "building": "Main",
                "capacity": 120,
                "type": "lecture_hall",
            },
            headers=headers,
        )
        created = assert_status_and_data(create_resp)
        classroom_id = created["id"]
        assert created["room_no"] == "A-101"

        await async_client_info.post(
            "/api/v1/info/classrooms/",
            json={
                "room_no": "B-201",
                "building": "Lab",
                "capacity": 40,
                "type": "lab",
            },
            headers=headers,
        )

        list_resp = await async_client_info.get(
            "/api/v1/info/classrooms/",
            params={
                "building": "Main",
                "classroom_type": "lecture_hall",
                "min_capacity": 100,
            },
            headers=headers,
        )
        listed = assert_status_and_data(list_resp)
        assert listed["pagination"]["total"] == 1
        assert listed["items"][0]["room_no"] == "A-101"

        get_resp = await async_client_info.get(
            f"/api/v1/info/classrooms/{classroom_id}",
            headers=headers,
        )
        fetched = assert_status_and_data(get_resp)
        assert fetched["building"] == "Main"

        put_resp = await async_client_info.put(
            f"/api/v1/info/classrooms/{classroom_id}",
            json={
                "room_no": "A-101-R",
                "building": "North",
                "capacity": 150,
                "type": "lecture_hall",
            },
            headers=headers,
        )
        updated = assert_status_and_data(put_resp)
        assert updated["room_no"] == "A-101-R"
        assert updated["capacity"] == 150

        patch_resp = await async_client_info.patch(
            f"/api/v1/info/classrooms/{classroom_id}",
            json={"building": "South", "capacity": 160},
            headers=headers,
        )
        patched = assert_status_and_data(patch_resp)
        assert patched["building"] == "South"
        assert patched["capacity"] == 160

        delete_resp = await async_client_info.delete(
            f"/api/v1/info/classrooms/{classroom_id}",
            headers=headers,
        )
        assert delete_resp.status_code == 200
        assert delete_resp.json()["data"] is None

        missing_resp = await async_client_info.get(
            f"/api/v1/info/classrooms/{classroom_id}",
            headers=headers,
        )
        assert missing_resp.status_code == 404

    async def test_create_classroom_rejects_duplicate_room_no(self, async_client_info) -> None:
        """Duplicate room_no should return 409."""
        headers = _classroom_headers()
        payload = {
            "room_no": "C-301",
            "building": "Main",
            "capacity": 80,
            "type": "standard",
        }

        first_resp = await async_client_info.post(
            "/api/v1/info/classrooms/",
            json=payload,
            headers=headers,
        )
        assert first_resp.status_code == 200

        duplicate_resp = await async_client_info.post(
            "/api/v1/info/classrooms/",
            json=payload,
            headers=headers,
        )
        assert duplicate_resp.status_code == 409

    async def test_patch_classroom_rejects_duplicate_room_no(self, async_client_info) -> None:
        """Changing room_no to an existing one should return 409."""
        headers = _classroom_headers()

        first_resp = await async_client_info.post(
            "/api/v1/info/classrooms/",
            json={"room_no": "D-401", "building": "East", "capacity": 60, "type": "lab"},
            headers=headers,
        )
        first_id = assert_status_and_data(first_resp)["id"]

        second_resp = await async_client_info.post(
            "/api/v1/info/classrooms/",
            json={"room_no": "D-402", "building": "East", "capacity": 60, "type": "lab"},
            headers=headers,
        )
        second_id = assert_status_and_data(second_resp)["id"]
        assert first_id != second_id

        resp = await async_client_info.patch(
            f"/api/v1/info/classrooms/{second_id}",
            json={"room_no": "D-401"},
            headers=headers,
        )
        assert resp.status_code == 409

    async def test_list_classrooms_rejects_invalid_pagination(self, async_client_info) -> None:
        """Invalid pagination should be rejected by validation."""
        resp = await async_client_info.get(
            "/api/v1/info/classrooms/",
            params={"page_size": 101},
            headers=_classroom_headers(),
        )
        assert resp.status_code == 422
