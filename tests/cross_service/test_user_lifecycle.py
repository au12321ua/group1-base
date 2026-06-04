"""跨服务用户生命周期集成测试。"""

import pytest

from auth_service.core.config import get_auth_settings
from tests.utils import build_identity_headers


def _cross_service_headers() -> dict[str, str]:
    """Build admin headers covering user + recycle-bin lifecycle operations."""
    return build_identity_headers(
        permissions=[
            "user:read",
            "user:create",
            "user:delete",
            "recycle:read",
            "recycle:restore",
            "recycle:delete",
        ]
    )


@pytest.mark.integration
@pytest.mark.regression
class TestCrossServiceUserLifecycle:
    """回归测试：修复 BUG-XSERVICE-001 — Info/Auth 用户生命周期必须保持跨服务一致。"""

    async def test_user_lifecycle_syncs_with_auth_service(
        self,
        async_client_info,
        async_client_auth,
        auth_service_bridge,
    ) -> None:
        """创建、逻辑删除、恢复、物理删除都应同步反映到 Auth 登录结果。"""
        headers = _cross_service_headers()
        username = "cross_service_user_001"
        password = get_auth_settings().default_initial_password

        create_resp = await async_client_info.post(
            "/api/v1/info/users/",
            json={
                "user_no": "XS2026001",
                "username": username,
                "role_ids": [],
                "full_name": "跨服务联调用户",
                "gender": "MALE",
                "email": "cross_service_user_001@test.edu.cn",
                "phone": "13800000001",
            },
            headers=headers,
        )
        assert create_resp.status_code == 201
        user_id = create_resp.json()["data"]["id"]

        login_resp = await async_client_auth.post(
            "/api/v1/auth/login",
            json={"username": username, "password": password},
        )
        assert login_resp.status_code == 200

        delete_resp = await async_client_info.delete(
            f"/api/v1/info/users/{user_id}",
            headers=headers,
        )
        assert delete_resp.status_code == 200

        disabled_login_resp = await async_client_auth.post(
            "/api/v1/auth/login",
            json={"username": username, "password": password},
        )
        assert disabled_login_resp.status_code == 423

        recycle_list_resp = await async_client_info.get(
            "/api/v1/info/recycle-bin/",
            params={"keyword": username, "page": 1, "page_size": 10},
            headers=headers,
        )
        assert recycle_list_resp.status_code == 200
        recycle_data = recycle_list_resp.json()["data"]
        assert recycle_data["pagination"]["total"] == 1
        assert recycle_data["items"][0]["id"] == user_id

        restore_resp = await async_client_info.post(
            f"/api/v1/info/recycle-bin/{user_id}/restore",
            headers=headers,
        )
        assert restore_resp.status_code == 200

        restored_login_resp = await async_client_auth.post(
            "/api/v1/auth/login",
            json={"username": username, "password": password},
        )
        assert restored_login_resp.status_code == 200

        delete_again_resp = await async_client_info.delete(
            f"/api/v1/info/users/{user_id}",
            headers=headers,
        )
        assert delete_again_resp.status_code == 200

        physical_delete_resp = await async_client_info.delete(
            f"/api/v1/info/recycle-bin/{user_id}",
            headers=headers,
        )
        assert physical_delete_resp.status_code == 200

        removed_login_resp = await async_client_auth.post(
            "/api/v1/auth/login",
            json={"username": username, "password": password},
        )
        assert removed_login_resp.status_code == 401

        missing_user_resp = await async_client_info.get(
            f"/api/v1/info/users/{user_id}",
            headers=headers,
        )
        assert missing_user_resp.status_code == 404
