"""回收站 API 集成测试。"""

from unittest.mock import AsyncMock

import pytest

from info_service.services.recycle_bin_service import recycle_bin_service
from info_service.services.user_management_service import user_management_service
from tests.utils import build_identity_headers, make_user_payload


def _recycle_headers() -> dict[str, str]:
    """Build admin headers with recycle-bin permissions."""
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
class TestRecycleBinAPI:
    """验证 /api/v1/info/recycle-bin 的已实现回收站行为。"""

    @pytest.fixture(autouse=True)
    def mock_cross_service_calls(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Mock Auth 同步调用，隔离回收站 API 集成测试。"""
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
            recycle_bin_service,
            "_call_auth_enable",
            AsyncMock(return_value=None),
        )
        monkeypatch.setattr(
            recycle_bin_service,
            "_call_auth_delete",
            AsyncMock(return_value=None),
        )
        monkeypatch.setattr(
            "info_service.services.recycle_bin_service.batch_fetch_role_names",
            AsyncMock(return_value={}),
        )

    async def test_recycle_bin_flow(self, async_client_info) -> None:
        """应支持列出、恢复和物理删除已逻辑删除用户。"""
        headers = _recycle_headers()
        payload = make_user_payload(user_no="RB2026001", username="recycle_user_001")

        create_resp = await async_client_info.post(
            "/api/v1/info/users/",
            json=payload,
            headers=headers,
        )
        assert create_resp.status_code == 201
        user_id = create_resp.json()["data"]["id"]

        delete_resp = await async_client_info.delete(
            f"/api/v1/info/users/{user_id}",
            headers=headers,
        )
        assert delete_resp.status_code == 200

        recycle_list_resp = await async_client_info.get(
            "/api/v1/info/recycle-bin/",
            params={"keyword": "recycle_user_001", "page": 1, "page_size": 10},
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

        get_resp = await async_client_info.get(
            f"/api/v1/info/users/{user_id}",
            headers=headers,
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["is_deleted"] is False

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

        missing_resp = await async_client_info.get(
            f"/api/v1/info/users/{user_id}",
            headers=headers,
        )
        assert missing_resp.status_code == 404

    async def test_batch_physical_delete(self, async_client_info) -> None:
        """批量物理删除后，目标用户应从回收站中消失。"""
        headers = _recycle_headers()
        created_user_ids: list[int] = []

        for suffix in ("11", "12"):
            create_resp = await async_client_info.post(
                "/api/v1/info/users/",
                json=make_user_payload(
                    user_no=f"RB2026{suffix}",
                    username=f"batch_recycle_{suffix}",
                ),
                headers=headers,
            )
            assert create_resp.status_code == 201
            user_id = create_resp.json()["data"]["id"]
            created_user_ids.append(user_id)

            delete_resp = await async_client_info.delete(
                f"/api/v1/info/users/{user_id}",
                headers=headers,
            )
            assert delete_resp.status_code == 200

        before_resp = await async_client_info.get(
            "/api/v1/info/recycle-bin/",
            params={"keyword": "batch_recycle", "page": 1, "page_size": 10},
            headers=headers,
        )
        assert before_resp.status_code == 200
        assert before_resp.json()["data"]["pagination"]["total"] == 2

        batch_delete_resp = await async_client_info.post(
            "/api/v1/info/recycle-bin/batch-delete",
            json={"user_ids": created_user_ids},
            headers=headers,
        )
        assert batch_delete_resp.status_code == 200

        after_resp = await async_client_info.get(
            "/api/v1/info/recycle-bin/",
            params={"keyword": "batch_recycle", "page": 1, "page_size": 10},
            headers=headers,
        )
        assert after_resp.status_code == 200
        assert after_resp.json()["data"]["pagination"]["total"] == 0


@pytest.mark.integration
@pytest.mark.regression
class TestRecycleBinRegressions:
    """回归测试：修复 BUG-RECYCLE-001 — Auth 恢复失败时 Info 侧必须回滚删除状态。"""

    @pytest.fixture(autouse=True)
    def mock_cross_service_calls(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Mock create/disable and selectively fail restore sync when needed."""
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
            recycle_bin_service,
            "_call_auth_delete",
            AsyncMock(return_value=None),
        )
        monkeypatch.setattr(
            "info_service.services.recycle_bin_service.batch_fetch_role_names",
            AsyncMock(return_value={}),
        )

    async def test_restore_rolls_back_when_auth_enable_fails(
        self, async_client_info, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """当 Auth enable 失败时，回收站恢复接口应返回 409 且保留删除状态。"""
        headers = _recycle_headers()
        create_resp = await async_client_info.post(
            "/api/v1/info/users/",
            json=make_user_payload(user_no="RB2026099", username="rollback_restore_99"),
            headers=headers,
        )
        assert create_resp.status_code == 201
        user_id = create_resp.json()["data"]["id"]

        delete_resp = await async_client_info.delete(
            f"/api/v1/info/users/{user_id}",
            headers=headers,
        )
        assert delete_resp.status_code == 200

        monkeypatch.setattr(
            recycle_bin_service,
            "_call_auth_enable",
            AsyncMock(side_effect=RuntimeError("auth enable failed")),
        )

        restore_resp = await async_client_info.post(
            f"/api/v1/info/recycle-bin/{user_id}/restore",
            headers=headers,
        )
        assert restore_resp.status_code == 409

        get_resp = await async_client_info.get(
            f"/api/v1/info/users/{user_id}",
            headers=headers,
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["is_deleted"] is True
