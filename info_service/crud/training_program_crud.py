"""TrainingProgram CRUD — curriculum plan operations."""

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.base import BaseCRUD
from info_service.models.training_program import TrainingProgram
from info_service.models.training_program_course import TrainingProgramCourse


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

    # ---- Program-Course association ----

    async def get_courses_by_program(
        self, db: AsyncSession, program_id: int
    ) -> list[TrainingProgramCourse]:
        """Get all course associations for a training program."""
        result = await db.exec(
            select(TrainingProgramCourse).where(
                TrainingProgramCourse.program_id == program_id
            )
        )
        return list(result.all())

    async def add_courses_to_program(
        self, db: AsyncSession, program_id: int, course_ids: list[int]
    ) -> list[TrainingProgramCourse]:
        """Add course associations to a program (skip duplicates)."""
        created: list[TrainingProgramCourse] = []
        for course_id in course_ids:
            assoc = TrainingProgramCourse(program_id=program_id, course_id=course_id)
            db.add(assoc)
            created.append(assoc)
        await db.flush()
        return created

    async def replace_courses_for_program(
        self, db: AsyncSession, program_id: int, course_ids: list[int]
    ) -> list[TrainingProgramCourse]:
        """Atomically replace all course associations for a program."""
        # Delete existing associations (flush to emit DELETE before INSERT)
        existing = await db.exec(
            select(TrainingProgramCourse).where(
                TrainingProgramCourse.program_id == program_id
            )
        )
        for assoc in existing.all():
            await db.delete(assoc)
        await db.flush()

        # Create new associations
        created: list[TrainingProgramCourse] = []
        for course_id in course_ids:
            assoc = TrainingProgramCourse(program_id=program_id, course_id=course_id)
            db.add(assoc)
            created.append(assoc)
        await db.flush()
        return created

    async def remove_course_from_program(
        self, db: AsyncSession, program_id: int, course_id: int
    ) -> bool:
        """Remove a single course association from a program."""
        result = await db.exec(
            select(TrainingProgramCourse).where(
                TrainingProgramCourse.program_id == program_id,
                TrainingProgramCourse.course_id == course_id,
            )
        )
        assoc = result.first()
        if assoc:
            await db.delete(assoc)
            await db.flush()
            return True
        return False


training_program_crud = TrainingProgramCRUD()

