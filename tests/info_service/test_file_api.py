"""File API integration tests."""

import shutil
import tempfile

import pytest

from info_service.services.file_storage_service import file_storage_service
from tests.info_service.api_helpers import assert_status_and_data
from tests.utils import build_identity_headers


def _file_headers(
    *,
    user_id: str = "file-owner",
    role: str = "TEACHER",
    permissions: list[str] | None = None,
) -> dict[str, str]:
    if permissions is None:
        permissions = ["file:read", "file:create", "file:delete"]
    return build_identity_headers(user_id=user_id, role=role, permissions=permissions)


@pytest.mark.integration
class TestFileAPI:
    """Validate /api/v1/info/files behavior."""

    @pytest.fixture(autouse=True)
    def _setup_upload_dir(self, monkeypatch: pytest.MonkeyPatch):
        tmpdir = tempfile.mkdtemp()
        monkeypatch.setattr(file_storage_service._settings, "upload_dir", tmpdir)
        yield
        shutil.rmtree(tmpdir, ignore_errors=True)

    async def test_file_upload_metadata_download_and_delete(self, async_client_info) -> None:
        """Owner should be able to upload, inspect, download, and delete a file."""
        owner_headers = _file_headers()

        upload_resp = await async_client_info.post(
            "/api/v1/info/files/",
            files={"file": ("report.pdf", b"report-content", "application/pdf")},
            headers=owner_headers,
        )
        uploaded = assert_status_and_data(upload_resp, 201)
        file_id = uploaded["id"]
        assert uploaded["file_name"] == "report.pdf"
        assert uploaded["file_type"] == "pdf"

        metadata_resp = await async_client_info.get(
            f"/api/v1/info/files/{file_id}",
            headers=owner_headers,
        )
        metadata = assert_status_and_data(metadata_resp)
        assert metadata["owner_user_id"] == "file-owner"
        assert metadata["file_size"] == len(b"report-content")

        download_resp = await async_client_info.get(
            f"/api/v1/info/files/{file_id}/download",
            headers=owner_headers,
        )
        assert download_resp.status_code == 200
        assert download_resp.content == b"report-content"
        assert 'filename="report.pdf"' in download_resp.headers["content-disposition"]

        delete_resp = await async_client_info.delete(
            f"/api/v1/info/files/{file_id}",
            headers=owner_headers,
        )
        assert delete_resp.status_code == 200
        assert delete_resp.json()["data"] is None

        missing_resp = await async_client_info.get(
            f"/api/v1/info/files/{file_id}",
            headers=owner_headers,
        )
        assert missing_resp.status_code == 404

    async def test_file_access_control_and_admin_bypass(self, async_client_info) -> None:
        """Non-owner should be blocked while admin can still access the file."""
        owner_headers = _file_headers()
        other_headers = _file_headers(user_id="other-teacher", role="TEACHER")
        admin_headers = _file_headers(user_id="admin-reader", role="SYS_ADMIN")

        upload_resp = await async_client_info.post(
            "/api/v1/info/files/",
            files={"file": ("grades.csv", b"id,score\n1,90\n", "text/csv")},
            headers=owner_headers,
        )
        file_id = assert_status_and_data(upload_resp, 201)["id"]

        forbidden_metadata = await async_client_info.get(
            f"/api/v1/info/files/{file_id}",
            headers=other_headers,
        )
        assert forbidden_metadata.status_code == 403

        forbidden_download = await async_client_info.get(
            f"/api/v1/info/files/{file_id}/download",
            headers=other_headers,
        )
        assert forbidden_download.status_code == 403

        admin_metadata = await async_client_info.get(
            f"/api/v1/info/files/{file_id}",
            headers=admin_headers,
        )
        assert admin_metadata.status_code == 200

        non_owner_delete = await async_client_info.delete(
            f"/api/v1/info/files/{file_id}",
            headers=other_headers,
        )
        assert non_owner_delete.status_code == 409

    async def test_upload_file_rejects_disallowed_type(self, async_client_info) -> None:
        """Unsupported file extensions should return 409."""
        resp = await async_client_info.post(
            "/api/v1/info/files/",
            files={"file": ("malware.exe", b"bad", "application/octet-stream")},
            headers=_file_headers(),
        )
        assert resp.status_code == 409

    async def test_get_missing_file_returns_404(self, async_client_info) -> None:
        """Metadata lookup for a missing file should return 404."""
        resp = await async_client_info.get(
            "/api/v1/info/files/99999",
            headers=_file_headers(),
        )
        assert resp.status_code == 404
