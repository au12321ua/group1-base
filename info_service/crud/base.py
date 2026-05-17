"""Base CRUD class with common CRUD operations."""

import warnings
from typing import TypeVar

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseCRUD[ModelType]:
    """Generic base CRUD for SQLModel entities."""

    def __init__(self, model: type[ModelType]) -> None:
        self.model = model
        warnings.warn(f"TODO: BaseCRUD<{model.__name__}> — implement all methods")

    async def get(self, db: AsyncSession, id: int) -> ModelType | None:
        """Get a single record by primary key."""
        warnings.warn("TODO: implement BaseCRUD.get")
        # result = await db.exec(select(self.model).where(self.model.id == id))
        # return result.first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """Get multiple records with offset/limit."""
        warnings.warn("TODO: implement BaseCRUD.get_multi")
        result = await db.exec(select(self.model).offset(skip).limit(limit))
        return list(result.all())

    async def create(self, db: AsyncSession, obj: ModelType) -> ModelType:
        """Create a new record."""
        warnings.warn("TODO: implement BaseCRUD.create")
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def update(self, db: AsyncSession, obj: ModelType, **kwargs) -> ModelType:
        """Update fields on an existing record."""
        warnings.warn("TODO: implement BaseCRUD.update")
        for field, value in kwargs.items():
            if hasattr(obj, field):
                setattr(obj, field, value)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def delete(self, db: AsyncSession, id: int) -> bool:
        """Delete a record by primary key. Returns True if deleted."""
        warnings.warn("TODO: implement BaseCRUD.delete")
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.flush()
            return True
        return False
