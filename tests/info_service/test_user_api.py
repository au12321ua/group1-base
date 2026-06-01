"""用户 API 集成测试。"""

from unittest.mock import AsyncMock

import pytest

from info_service.services.user_management_service import user_management_service
from tests.utils import build_identity_headers


def _make_user_payload(*, suffix: str) -> dict[str, object]:
    """构造带唯一后缀的用户创建 payload。"""
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

    @pytest.fixture(autouse=True)
    def mock_auth_sync(self, monkeypatch) -> None:
        """Mock Auth 同步调用，确保集成测试可重复且稳定。"""
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
        assert created["role_ids"] == ""
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
        assert updated["role_ids"] == ""
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


@pytest.mark.integration
class TestUserResourceAccess:
    """验证用户资源级授权：非管理员只能访问自己的资料，管理员不受限制。"""

    @pytest.fixture(autouse=True)
    def mock_auth_sync(self, monkeypatch) -> None:
        """Mock Auth 同步调用。"""
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
    async def test_non_admin_can_view_own_profile(
        self, async_client_info, auth_headers
    ) -> None:
        """非管理员用户可以查看自己的资料。"""
        create_resp = await async_client_info.post(
            "/api/v1/users/",
            json=_make_user_payload(suffix="2101"),
            headers=auth_headers,
        )
        user_id = create_resp.json()["data"]["id"]

        own_headers = build_identity_headers(
            user_id=str(user_id), role="STUDENT", permissions=["user:read"]
        )
        resp = await async_client_info.get(
            f"/api/v1/users/{user_id}", headers=own_headers
        )
        assert resp.status_code == 200

    async def test_non_admin_cannot_view_other_profile(
        self, async_client_info, auth_headers
    ) -> None:
        """非管理员用户查看他人资料应返回 403。"""
        create_resp = await async_client_info.post(
            "/api/v1/users/",
            json=_make_user_payload(suffix="2102"),
            headers=auth_headers,
        )
        user_id = create_resp.json()["data"]["id"]

        other_headers = build_identity_headers(
            user_id="other-user", role="STUDENT", permissions=["user:read"]
        )
        resp = await async_client_info.get(
            f"/api/v1/users/{user_id}", headers=other_headers
        )
        assert resp.status_code == 403

    async def test_admin_can_view_any_profile(
        self, async_client_info, auth_headers
    ) -> None:
        """管理员可以查看任意用户资料。"""
        create_resp = await async_client_info.post(
            "/api/v1/users/",
            json=_make_user_payload(suffix="2103"),
            headers=auth_headers,
        )
        user_id = create_resp.json()["data"]["id"]

        admin_headers = build_identity_headers(
            user_id="admin-user", role="SYS_ADMIN", permissions=["user:read"]
        )
        resp = await async_client_info.get(
            f"/api/v1/users/{user_id}", headers=admin_headers
        )
        assert resp.status_code == 200

    async def test_non_admin_cannot_update_other_profile(
        self, async_client_info, auth_headers
    ) -> None:
        """非管理员用户更新他人资料应返回 403。"""
        create_resp = await async_client_info.post(
            "/api/v1/users/",
            json=_make_user_payload(suffix="2104"),
            headers=auth_headers,
        )
        user_id = create_resp.json()["data"]["id"]

        other_headers = build_identity_headers(
            user_id="other-user", role="TEACHER", permissions=["user:update"]
        )
        resp = await async_client_info.put(
            f"/api/v1/users/{user_id}",
            json={
                "user_no": "S20262104",
                "username": "user_2104",
                "role_ids": [2],
                "full_name": "被篡改",
                "gender": "MALE",
                "email": "hacked@test.edu.cn",
                "phone": "13800000000",
                "status": "ACTIVE",
            },
            headers=other_headers,
        )
        assert resp.status_code == 403

    async def test_non_admin_can_update_own_profile(
        self, async_client_info, auth_headers
    ) -> None:
        """非管理员用户可以更新自己的资料。"""
        create_resp = await async_client_info.post(
            "/api/v1/users/",
            json=_make_user_payload(suffix="2105"),
            headers=auth_headers,
        )
        user_id = create_resp.json()["data"]["id"]

        own_headers = build_identity_headers(
            user_id=str(user_id), role="STUDENT", permissions=["user:update"]
        )
        resp = await async_client_info.patch(
            f"/api/v1/users/{user_id}",
            json={"full_name": "自己更新"},
            headers=own_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["profile"]["full_name"] == "自己更新"

    async def test_non_admin_cannot_delete_users(
        self, async_client_info, auth_headers
    ) -> None:
        """非管理员用户删除用户应返回 403（即使删除自己也不行）。"""
        create_resp = await async_client_info.post(
            "/api/v1/users/",
            json=_make_user_payload(suffix="2106"),
            headers=auth_headers,
        )
        user_id = create_resp.json()["data"]["id"]

        own_headers = build_identity_headers(
            user_id=str(user_id), role="TEACHER", permissions=["user:delete"]
        )
        resp = await async_client_info.delete(
            f"/api/v1/users/{user_id}", headers=own_headers
        )
        assert resp.status_code == 403

    async def test_admin_can_delete_users(
        self, async_client_info, auth_headers
    ) -> None:
        """管理员可以删除用户。"""
        create_resp = await async_client_info.post(
            "/api/v1/users/",
            json=_make_user_payload(suffix="2107"),
            headers=auth_headers,
        )
        user_id = create_resp.json()["data"]["id"]

        admin_delete_headers = build_identity_headers(
            user_id="admin-user", role="SYS_ADMIN", permissions=["user:delete"]
        )
        resp = await async_client_info.delete(
            f"/api/v1/users/{user_id}", headers=admin_delete_headers
        )
        assert resp.status_code == 200
