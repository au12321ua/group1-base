"""FileResource CRUD — uploaded file metadata operations."""

import warnings

from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.base import BaseCRUD
from info_service.models.file_resource import FileResource


class FileResourceCRUD(BaseCRUD[FileResource]):
    """Data access for FileResource model."""

    def __init__(self) -> None:
        super().__init__(FileResource)
        warnings.warn("TODO: FileResourceCRUD — implement custom query methods")

    async def get_by_owner(
        self,
        db: AsyncSession,
        owner_user_id: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[FileResource], int]:
        """Get files owned by a user. Returns (items, total)."""
        warnings.warn("TODO: implement get_by_owner")
        raise NotImplementedError("get_by_owner not implemented")


file_resource_crud = FileResourceCRUD()
