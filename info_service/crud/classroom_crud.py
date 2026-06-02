"""Classroom CRUD — classroom resource operations."""

from sqlalchemy import or_
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.base import BaseCRUD
from info_service.models.classroom import Classroom


class ClassroomCRUD(BaseCRUD[Classroom]):
    """Data access for Classroom model."""

    def __init__(self) -> None:
        super().__init__(Classroom)

    async def batch_get_by_ids(
        self, db: AsyncSession, ids: set[int]
    ) -> dict[int, Classroom]:
        """Batch-fetch classrooms by IDs in a single query, returning {id: Classroom} map."""
        if not ids:
            return {}
        stmt = select(Classroom).where(Classroom.id.in_(ids))
        result = await db.exec(stmt)
        return {c.id: c for c in result.all()}

    async def get_by_room_no(self, db: AsyncSession, room_no: str) -> Classroom | None:
        """Get classroom by unique room number."""
        result = await db.exec(select(Classroom).where(Classroom.room_no == room_no))
        return result.first()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        keyword: str | None = None,
        building: str | None = None,
        classroom_type: str | None = None,
        min_capacity: int | None = None,
    ) -> tuple[list[Classroom], int]:
        """Get paginated classroom list with basic filters."""
        conditions = []
        if keyword:
            pattern = f"%{keyword}%"
            conditions.append(
                or_(Classroom.room_no.ilike(pattern), Classroom.building.ilike(pattern))
            )
        if building:
            conditions.append(Classroom.building == building)
        if classroom_type:
            conditions.append(Classroom.type == classroom_type)
        if min_capacity is not None:
            conditions.append(Classroom.capacity >= min_capacity)

        stmt = select(Classroom).where(*conditions).offset(skip).limit(limit).order_by(Classroom.id)
        count_stmt = select(func.count(Classroom.id)).where(*conditions)

        items = list((await db.exec(stmt)).all())
        total = (await db.exec(count_stmt)).one()
        return items, total


classroom_crud = ClassroomCRUD()
