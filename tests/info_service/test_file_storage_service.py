"""Unit tests for FileStorageService."""

import os
import tempfile

import pytest

from info_service.crud.file_resource_crud import file_resource_crud
from info_service.services.file_storage_service import file_storage_service
from shared.exceptions import BusinessRuleError, ResourceNotFoundError


@pytest.mark.unit
class TestFileStorageService:
    """FileStorageService unit tests using temp directory and in-memory DB."""

    @pytest.fixture(autouse=True)
    def _setup_upload_dir(self, monkeypatch):
        """Use a temp directory for uploads during tests."""
        tmpdir = tempfile.mkdtemp()
        monkeypatch.setattr(
            file_storage_service._settings, "upload_dir", tmpdir
        )
        yield
        # Cleanup
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)

    async def test_upload_file_success(self, info_db_session):
        result = await file_storage_service.upload_file(
            info_db_session,
            owner_user_id="user-001",
            file_name="test.pdf",
            file_type="pdf",
            file_size=100,
            content=b"hello world",
        )
        assert result["id"] is not None
        assert result["file_name"] == "test.pdf"
        assert result["file_type"] == "pdf"
        assert "/download" in result["access_url"]

        # Verify file is on disk
        resource = await file_resource_crud.get(info_db_session, result["id"])
        assert os.path.exists(resource.storage_path)

    async def test_upload_file_disallowed_type(self, info_db_session):
        with pytest.raises(BusinessRuleError, match="not allowed"):
            await file_storage_service.upload_file(
                info_db_session,
                owner_user_id="user-001",
                file_name="test.exe",
                file_type="exe",
                file_size=100,
                content=b"bad",
            )

    async def test_upload_file_oversize(self, info_db_session):
        max_mb = file_storage_service._settings.max_upload_size_mb
        huge_size = (max_mb + 1) * 1024 * 1024
        with pytest.raises(BusinessRuleError, match="exceeds limit"):
            await file_storage_service.upload_file(
                info_db_session,
                owner_user_id="user-001",
                file_name="huge.pdf",
                file_type="pdf",
                file_size=huge_size,
                content=b"x",
            )

    async def test_upload_file_invalid_chars_in_type(self, info_db_session):
        with pytest.raises(BusinessRuleError, match="invalid characters"):
            await file_storage_service.upload_file(
                info_db_session,
                owner_user_id="user-001",
                file_name="bad.pdf",
                file_type="pd/f",
                file_size=100,
                content=b"x",
            )

    async def test_get_file_success(self, info_db_session):
        result = await file_storage_service.upload_file(
            info_db_session,
            owner_user_id="user-001",
            file_name="test.png",
            file_type="png",
            file_size=200,
            content=b"png content",
        )
        content, mime = await file_storage_service.get_file(
            info_db_session, result["id"]
        )
        assert content == b"png content"
        assert mime == "image/png"

    async def test_get_file_not_found(self, info_db_session):
        with pytest.raises(ResourceNotFoundError):
            await file_storage_service.get_file(info_db_session, 99999)

    async def test_delete_file_owner(self, info_db_session):
        result = await file_storage_service.upload_file(
            info_db_session,
            owner_user_id="user-001",
            file_name="test.jpg",
            file_type="jpg",
            file_size=300,
            content=b"jpg content",
        )
        file_id = result["id"]
        resource = await file_resource_crud.get(info_db_session, file_id)
        assert os.path.exists(resource.storage_path)

        await file_storage_service.delete_file(
            info_db_session, file_id, "user-001"
        )
        # Verify metadata gone
        assert await file_resource_crud.get(info_db_session, file_id) is None
        # Verify disk file gone
        assert not os.path.exists(resource.storage_path)

    async def test_delete_file_not_owner(self, info_db_session):
        result = await file_storage_service.upload_file(
            info_db_session,
            owner_user_id="user-001",
            file_name="test.jpg",
            file_type="jpg",
            file_size=300,
            content=b"jpg content",
        )
        with pytest.raises(BusinessRuleError, match="owner or admin"):
            await file_storage_service.delete_file(
                info_db_session, result["id"], "user-002"
            )

    async def test_delete_file_admin_bypass(self, info_db_session):
        result = await file_storage_service.upload_file(
            info_db_session,
            owner_user_id="user-001",
            file_name="test.jpg",
            file_type="jpg",
            file_size=300,
            content=b"jpg content",
        )
        # Admin can delete even if not owner
        await file_storage_service.delete_file(
            info_db_session, result["id"], "admin-user", user_role="SYS_ADMIN"
        )
        assert await file_resource_crud.get(info_db_session, result["id"]) is None

    async def test_delete_file_not_found(self, info_db_session):
        with pytest.raises(ResourceNotFoundError):
            await file_storage_service.delete_file(
                info_db_session, 99999, "user-001"
            )
