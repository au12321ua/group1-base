"""TrainingProgram CRUD — curriculum plan operations."""

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.base import BaseCRUD
from info_service.models.training_program import TrainingProgram


class TrainingProgramCRUD(BaseCRUD[TrainingProgram]):
    """Data access for TrainingProgram model."""

    def __init__(self) -> None:
        super().__init__(TrainingProgram)

    async def get_by_program_code(self, db: AsyncSession, code: str) -> TrainingProgram | None:
        """Get program by program_code."""
        result = await db.exec(
            select(TrainingProgram).where(TrainingProgram.program_code == code)
        )
        return result.first()

    async def get_by_major(
        self, db: AsyncSession, major_code: str, grade: str | None = None
    ) -> list[TrainingProgram]:
        """Get programs by major code, optionally filtered by grade."""
        stmt = select(TrainingProgram).where(TrainingProgram.major_code == major_code)
        if grade:
            stmt = stmt.where(TrainingProgram.grade == grade)
        result = await db.exec(stmt.order_by(TrainingProgram.id))
        return list(result.all())

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        major_code: str | None = None,
        grade: str | None = None,
        version: str | None = None,
    ) -> tuple[list[TrainingProgram], int]:
        """Get paginated training program list with optional filters."""
        conditions = []
        if major_code:
            conditions.append(TrainingProgram.major_code == major_code)
        if grade:
            conditions.append(TrainingProgram.grade == grade)
        if version:
            conditions.append(TrainingProgram.version == version)

        stmt = (
            select(TrainingProgram)
            .where(*conditions)
            .offset(skip)
            .limit(limit)
            .order_by(TrainingProgram.id)
        )
        count_stmt = select(func.count(TrainingProgram.id)).where(*conditions)

        items = list((await db.exec(stmt)).all())
        total = (await db.exec(count_stmt)).one()
        return items, total


training_program_crud = TrainingProgramCRUD()
