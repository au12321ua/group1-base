"""Integration tests for user API behavior."""

from unittest.mock import AsyncMock

import pytest

from info_service.services.user_management_service import user_management_service
from tests.utils import build_identity_headers


def _make_user_payload(*, suffix: str) -> dict[str, object]:
    """Build a deterministic user payload with a unique suffix."""
    return {
        "user_no": f"S2026{suffix}",
        "username": f"user_{suffix}",
        "role_ids": [1, 2],
        "full_name": f"集成测试用户{suffix}",
        "gender": "FEMALE",
        "email": f"user_{suffix}@test.edu.cn",
        "phone": "13800000000",
    }


@pytest.mark.integration
class TestUserAPI:
    """验证 /api/v1/users 的 CRUD、鉴权和跨服务补偿行为。"""

    @pytest.fixture
    def auth_headers(self) -> dict[str, str]:
        return build_identity_headers(
            permissions=["user:read", "user:create", "user:update", "user:delete"]
        )

    @pytest.fixture(autouse=True)
    def mock_auth_sync(self, monkeypatch) -> None:
        """Mock Auth sync calls to keep integration tests deterministic."""
        monkeypatch.setattr(
            user_management_service,
            "_sync_create_to_auth",
            AsyncMock(return_value=True),
        )
        monkeypatch.setattr(
            user_management_service,
            "_sync_disable_to_auth",
            AsyncMock(return_value=None),
        )
        monkeypatch.setattr(
            user_management_service,
            "_sync_roles_to_auth",
            AsyncMock(return_value=None),
        )

    async def test_user_crud_flow(self, async_client_info, auth_headers) -> None:
        """应支持创建、查询、更新、部分更新和逻辑删除用户。"""
        create_resp = await async_client_info.post(
            "/api/v1/users/",
            json=_make_user_payload(suffix="1101"),
            headers=auth_headers,
        )
        assert create_resp.status_code == 201
        created = create_resp.json()["data"]
        user_id = created["id"]
        assert created["user_no"] == "S20261101"
        assert created["username"] == "user_1101"
        assert created["role_ids"] == "1,2"
        assert created["is_deleted"] is False
        assert created["profile"]["full_name"] == "集成测试用户1101"

        list_resp = await async_client_info.get(
            "/api/v1/users/",
            params={"keyword": "1101", "page": 1, "page_size": 10},
            headers=auth_headers,
        )
        assert list_resp.status_code == 200
        list_payload = list_resp.json()["data"]
        assert list_payload["pagination"]["total"] == 1
        assert list_payload["items"][0]["id"] == user_id

        get_resp = await async_client_info.get(
            f"/api/v1/users/{user_id}",
            headers=auth_headers,
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["username"] == "user_1101"

        put_resp = await async_client_info.put(
            f"/api/v1/users/{user_id}",
            json={
                "user_no": "S20261101-U",
                "username": "user_1101_u",
                "role_ids": [3],
                "full_name": "用户1101更新",
                "gender": "MALE",
                "email": "user_1101_u@test.edu.cn",
                "phone": "13900000000",
                "status": "ACTIVE",
            },
            headers=auth_headers,
        )
        assert put_resp.status_code == 200
        updated = put_resp.json()["data"]
        assert updated["user_no"] == "S20261101-U"
        assert updated["username"] == "user_1101_u"
        assert updated["role_ids"] == "3"
        assert updated["profile"]["full_name"] == "用户1101更新"

        patch_resp = await async_client_info.patch(
            f"/api/v1/users/{user_id}",
            json={"full_name": "用户1101补丁", "phone": "13700000000"},
            headers=auth_headers,
        )
        assert patch_resp.status_code == 200
        patched = patch_resp.json()["data"]
        assert patched["profile"]["full_name"] == "用户1101补丁"
        assert patched["profile"]["phone"] == "13700000000"

        delete_resp = await async_client_info.delete(
            f"/api/v1/users/{user_id}",
            headers=auth_headers,
        )
        assert delete_resp.status_code == 200
        assert delete_resp.json()["data"] is None

        get_deleted_resp = await async_client_info.get(
            f"/api/v1/users/{user_id}",
            headers=auth_headers,
        )
        assert get_deleted_resp.status_code == 200
        assert get_deleted_resp.json()["data"]["is_deleted"] is True

        list_after_delete_resp = await async_client_info.get(
            "/api/v1/users/",
            params={"keyword": "1101", "page": 1, "page_size": 10},
            headers=auth_headers,
        )
        assert list_after_delete_resp.status_code == 200
        assert list_after_delete_resp.json()["data"]["pagination"]["total"] == 0

    async def test_create_user_rejects_duplicates(self, async_client_info, auth_headers) -> None:
        """重复 user_no 或 username 应返回 409。"""
        payload = _make_user_payload(suffix="1102")
        first_resp = await async_client_info.post(
            "/api/v1/users/",
            json=payload,
            headers=auth_headers,
        )
        assert first_resp.status_code == 201

        duplicate_no_resp = await async_client_info.post(
            "/api/v1/users/",
            json={**_make_user_payload(suffix="2202"), "user_no": payload["user_no"]},
            headers=auth_headers,
        )
        assert duplicate_no_resp.status_code == 409

        duplicate_name_resp = await async_client_info.post(
            "/api/v1/users/",
            json={**_make_user_payload(suffix="3302"), "username": payload["username"]},
            headers=auth_headers,
        )
        assert duplicate_name_resp.status_code == 409

    async def test_delete_user_rolls_back_when_auth_sync_fails(
        self, async_client_info, auth_headers, monkeypatch
    ) -> None:
        """当 Auth 禁用失败时，应补偿回滚 is_deleted 状态。"""
        create_resp = await async_client_info.post(
            "/api/v1/users/",
            json=_make_user_payload(suffix="1103"),
            headers=auth_headers,
        )
        assert create_resp.status_code == 201
        user_id = create_resp.json()["data"]["id"]

        monkeypatch.setattr(
            user_management_service,
            "_sync_disable_to_auth",
            AsyncMock(side_effect=RuntimeError("auth sync failed")),
        )

        delete_resp = await async_client_info.delete(
            f"/api/v1/users/{user_id}",
            headers=auth_headers,
        )
        assert delete_resp.status_code == 409

        get_resp = await async_client_info.get(
            f"/api/v1/users/{user_id}",
            headers=auth_headers,
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["is_deleted"] is False

    async def test_user_routes_enforce_auth_and_validation(self, async_client_info) -> None:
        """用户接口应正确返回 401/403/422。"""
        missing_header_resp = await async_client_info.get("/api/v1/users/")
        assert missing_header_resp.status_code == 401

        low_perm_headers = build_identity_headers(permissions=["user:read"])
        forbidden_resp = await async_client_info.post(
            "/api/v1/users/",
            json=_make_user_payload(suffix="1104"),
            headers=low_perm_headers,
        )
        assert forbidden_resp.status_code == 403

        invalid_query_resp = await async_client_info.get(
            "/api/v1/users/",
            params={"page": 0},
            headers=low_perm_headers,
        )
        assert invalid_query_resp.status_code == 422

        invalid_payload_resp = await async_client_info.post(
            "/api/v1/users/",
            json={
                "user_no": "",
                "username": "invalid_user",
                "role_ids": [],
                "full_name": "",
                "gender": "",
                "email": "",
                "phone": "",
            },
            headers=build_identity_headers(
                permissions=["user:create", "user:read", "user:update", "user:delete"]
            ),
        )
        assert invalid_payload_resp.status_code == 422
