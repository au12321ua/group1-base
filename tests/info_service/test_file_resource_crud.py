"""Unit tests for FileResource CRUD."""

import pytest

from info_service.crud.file_resource_crud import file_resource_crud
from info_service.models.file_resource import FileResource


@pytest.mark.unit
class TestFileResourceCRUD:
    """FileResource CRUD operations — inherits BaseCRUD + get_by_owner."""

    async def test_create_file_resource(self, info_db_session):
        resource = await file_resource_crud.create(
            info_db_session,
            FileResource(
                owner_user_id="user-001",
                file_name="test.pdf",
                file_type="pdf",
                file_size=1024,
                storage_path="/uploads/1.pdf",
                checksum="abc123",
            ),
        )
        assert resource.id is not None
        assert resource.file_name == "test.pdf"

    async def test_get_file_resource(self, info_db_session):
        created = await file_resource_crud.create(
            info_db_session,
            FileResource(
                owner_user_id="user-001",
                file_name="test.pdf",
                file_type="pdf",
                file_size=1024,
                storage_path="/uploads/1.pdf",
            ),
        )
        fetched = await file_resource_crud.get(info_db_session, created.id)
        assert fetched is not None
        assert fetched.file_name == "test.pdf"

    async def test_delete_file_resource(self, info_db_session):
        created = await file_resource_crud.create(
            info_db_session,
            FileResource(
                owner_user_id="user-001",
                file_name="test.pdf",
                file_type="pdf",
                file_size=1024,
                storage_path="/uploads/1.pdf",
            ),
        )
        result = await file_resource_crud.delete(info_db_session, created.id)
        assert result is True

        fetched = await file_resource_crud.get(info_db_session, created.id)
        assert fetched is None

    async def test_get_by_owner(self, info_db_session):
        await file_resource_crud.create(
            info_db_session,
            FileResource(
                owner_user_id="user-001",
                file_name="file1.pdf",
                file_type="pdf",
                file_size=100,
                storage_path="/uploads/1.pdf",
            ),
        )
        await file_resource_crud.create(
            info_db_session,
            FileResource(
                owner_user_id="user-001",
                file_name="file2.png",
                file_type="png",
                file_size=200,
                storage_path="/uploads/2.png",
            ),
        )
        await file_resource_crud.create(
            info_db_session,
            FileResource(
                owner_user_id="user-002",
                file_name="file3.jpg",
                file_type="jpg",
                file_size=300,
                storage_path="/uploads/3.jpg",
            ),
        )

        items, total = await file_resource_crud.get_by_owner(
            info_db_session, "user-001"
        )
        assert len(items) == 2
        assert total == 2
        assert all(item.owner_user_id == "user-001" for item in items)

    async def test_get_by_owner_empty(self, info_db_session):
        items, total = await file_resource_crud.get_by_owner(
            info_db_session, "nonexistent"
        )
        assert items == []
        assert total == 0
