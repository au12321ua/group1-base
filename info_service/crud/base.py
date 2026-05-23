"""Base CRUD class with common CRUD operations."""

from datetime import UTC, datetime
from typing import TypeVar

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseCRUD[ModelType]:
    """Generic base CRUD for SQLModel entities."""

    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> ModelType | None:
        """Get a single record by primary key."""
        return await db.get(self.model, id)

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """Get multiple records with offset/limit."""
        stmt = select(self.model).order_by(self.model.id).offset(skip).limit(limit)
        result = await db.exec(stmt)
        return list(result.all())

    async def create(self, db: AsyncSession, obj: ModelType) -> ModelType:
        """Create a new record."""
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def update(self, db: AsyncSession, obj: ModelType, **kwargs) -> ModelType:
        """Update fields on an existing record."""
        for field, value in kwargs.items():
            if hasattr(obj, field):
                setattr(obj, field, value)

        if hasattr(obj, "updated_at") and "updated_at" not in kwargs:
            setattr(obj, "updated_at", datetime.now(UTC))

        await db.flush()
        await db.refresh(obj)
        return obj

    async def delete(self, db: AsyncSession, id: int) -> bool:
        """Delete a record by primary key. Returns True if deleted."""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.flush()
            return True
        return False
