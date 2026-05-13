"""BaseInfoItem CRUD — generic lookup data operations."""

import warnings

from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.base import BaseCRUD
from info_service.models.base_info_item import BaseInfoItem


class BaseInfoCRUD(BaseCRUD[BaseInfoItem]):
    """Data access for BaseInfoItem model."""

    def __init__(self) -> None:
        super().__init__(BaseInfoItem)
        warnings.warn("TODO: BaseInfoCRUD — implement custom query methods")

    async def get_by_category(
        self,
        db: AsyncSession,
        category: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[BaseInfoItem], int]:
        """Get items by category. Returns (items, total)."""
        warnings.warn("TODO: implement get_by_category")
        raise NotImplementedError("get_by_category not implemented")


base_info_crud = BaseInfoCRUD()
