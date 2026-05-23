"""BaseInfoItem CRUD — generic lookup data operations."""

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.base import BaseCRUD
from info_service.models.base_info_item import BaseInfoItem


class BaseInfoCRUD(BaseCRUD[BaseInfoItem]):
    """Data access for BaseInfoItem model."""

    def __init__(self) -> None:
        super().__init__(BaseInfoItem)

    async def get_by_category(
        self,
        db: AsyncSession,
        category: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[BaseInfoItem], int]:
        """Get items by category. Returns (items, total)."""
        base_query = select(BaseInfoItem).where(BaseInfoItem.category == category)
        count_query = select(func.count()).select_from(BaseInfoItem).where(
            BaseInfoItem.category == category
        )

        total_result = await db.exec(count_query)
        total = total_result.one()

        items_result = await db.exec(base_query.offset(skip).limit(limit))
        items = list(items_result.all())

        return items, total


base_info_crud = BaseInfoCRUD()
