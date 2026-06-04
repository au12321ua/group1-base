"""Base info API integration tests."""

import pytest

from tests.info_service.api_helpers import assert_status_and_data
from tests.utils import build_identity_headers


def _base_info_headers(*, role: str = "SYS_ADMIN") -> dict[str, str]:
    return build_identity_headers(
        user_id=f"{role.lower()}-base-info",
        role=role,
        permissions=[f"base-info:{action}" for action in ("read", "create", "update", "delete")],
    )


@pytest.mark.integration
class TestBaseInfoAPI:
    """Validate /api/v1/info/base-info behavior."""

    async def test_base_info_crud_and_category_filter(self, async_client_info) -> None:
        """Base info endpoints should support CRUD plus category filtering."""
        headers = _base_info_headers()

        create_resp = await async_client_info.post(
            "/api/v1/info/base-info/",
            json={
                "category": "department",
                "item_code": "CS",
                "item_name": "Computer Science",
                "description": "School of Computing",
            },
            headers=headers,
        )
        created = assert_status_and_data(create_resp, 201)
        item_id = created["id"]
        assert created["item_code"] == "CS"

        await async_client_info.post(
            "/api/v1/info/base-info/",
            json={
                "category": "title",
                "item_code": "PROF",
                "item_name": "Professor",
                "description": "Academic title",
            },
            headers=headers,
        )

        list_resp = await async_client_info.get(
            "/api/v1/info/base-info/",
            params={"category": "department"},
            headers=headers,
        )
        listed = assert_status_and_data(list_resp)
        assert listed["pagination"]["total"] == 1
        assert listed["items"][0]["item_name"] == "Computer Science"

        get_resp = await async_client_info.get(
            f"/api/v1/info/base-info/{item_id}",
            headers=headers,
        )
        fetched = assert_status_and_data(get_resp)
        assert fetched["description"] == "School of Computing"

        put_resp = await async_client_info.put(
            f"/api/v1/info/base-info/{item_id}",
            json={
                "category": "department",
                "item_code": "CS-NEW",
                "item_name": "CS Department",
                "description": "Renamed department",
                "is_active": False,
            },
            headers=headers,
        )
        updated = assert_status_and_data(put_resp)
        assert updated["item_code"] == "CS-NEW"
        assert updated["is_active"] is False

        patch_resp = await async_client_info.patch(
            f"/api/v1/info/base-info/{item_id}",
            json={"description": "Patched description", "is_active": True},
            headers=headers,
        )
        patched = assert_status_and_data(patch_resp)
        assert patched["description"] == "Patched description"
        assert patched["is_active"] is True

        delete_resp = await async_client_info.delete(
            f"/api/v1/info/base-info/{item_id}",
            headers=headers,
        )
        assert delete_resp.status_code == 200
        assert delete_resp.json()["data"] is None

        missing_resp = await async_client_info.get(
            f"/api/v1/info/base-info/{item_id}",
            headers=headers,
        )
        assert missing_resp.status_code == 404

    async def test_create_base_info_rejects_duplicate_category_item_code(
        self, async_client_info
    ) -> None:
        """Duplicate (category, item_code) should return 409."""
        headers = _base_info_headers()
        payload = {
            "category": "department",
            "item_code": "EE",
            "item_name": "Electrical Engineering",
            "description": "First row",
        }

        first_resp = await async_client_info.post(
            "/api/v1/info/base-info/",
            json=payload,
            headers=headers,
        )
        assert first_resp.status_code == 201

        duplicate_resp = await async_client_info.post(
            "/api/v1/info/base-info/",
            json=payload,
            headers=headers,
        )
        assert duplicate_resp.status_code == 409

    async def test_base_info_admin_only_mutations_reject_non_admin(
        self, async_client_info
    ) -> None:
        """PUT/PATCH/DELETE should reject non-admin callers."""
        admin_headers = _base_info_headers()
        teacher_headers = _base_info_headers(role="TEACHER")

        create_resp = await async_client_info.post(
            "/api/v1/info/base-info/",
            json={
                "category": "title",
                "item_code": "LECT",
                "item_name": "Lecturer",
                "description": "Teaching role",
            },
            headers=admin_headers,
        )
        item_id = assert_status_and_data(create_resp, 201)["id"]

        put_resp = await async_client_info.put(
            f"/api/v1/info/base-info/{item_id}",
            json={
                "category": "title",
                "item_code": "LECT2",
                "item_name": "Senior Lecturer",
                "description": "Blocked update",
                "is_active": True,
            },
            headers=teacher_headers,
        )
        assert put_resp.status_code == 403

        patch_resp = await async_client_info.patch(
            f"/api/v1/info/base-info/{item_id}",
            json={"item_name": "Blocked patch"},
            headers=teacher_headers,
        )
        assert patch_resp.status_code == 403

        delete_resp = await async_client_info.delete(
            f"/api/v1/info/base-info/{item_id}",
            headers=teacher_headers,
        )
        assert delete_resp.status_code == 403

    async def test_list_base_info_rejects_invalid_pagination(self, async_client_info) -> None:
        """Invalid pagination should be rejected by validation."""
        resp = await async_client_info.get(
            "/api/v1/info/base-info/",
            params={"page": 0},
            headers=_base_info_headers(),
        )
        assert resp.status_code == 422
