"""FileResource CRUD — uploaded file metadata operations."""

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.base import BaseCRUD
from info_service.models.file_resource import FileResource


class FileResourceCRUD(BaseCRUD[FileResource]):
    """Data access for FileResource model."""

    def __init__(self) -> None:
        super().__init__(FileResource)

    async def get_by_owner(
        self,
        db: AsyncSession,
        owner_user_id: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[FileResource], int]:
        """Get files owned by a user. Returns (items, total)."""
        conditions = [FileResource.owner_user_id == owner_user_id]

        count_query = (
            select(func.count()).select_from(FileResource).where(*conditions)
        )
        total_result = await db.exec(count_query)
        total = total_result.one()

        items_result = await db.exec(
            select(FileResource)
            .where(*conditions)
            .order_by(FileResource.id)
            .offset(skip)
            .limit(limit)
        )
        return list(items_result.all()), total


file_resource_crud = FileResourceCRUD()
