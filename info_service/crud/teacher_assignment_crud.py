"""Teacher assignment CRUD helpers."""

from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.base import BaseCRUD
from info_service.models.teacher_assignment import TeacherCourseAssignment


class TeacherAssignmentCRUD(BaseCRUD[TeacherCourseAssignment]):
    """Data access helpers for teacher-course assignments."""

    def __init__(self) -> None:
        super().__init__(TeacherCourseAssignment)

    async def get_by_offering(
        self, db: AsyncSession, offering_id: int
    ) -> list[TeacherCourseAssignment]:
        """Return assignments for one offering ordered by creation id."""
        stmt = (
            select(TeacherCourseAssignment)
            .where(TeacherCourseAssignment.offering_id == offering_id)
            .order_by(TeacherCourseAssignment.id)
        )
        result = await db.exec(stmt)
        return list(result.all())

    async def get_by_offering_and_teacher(
        self, db: AsyncSession, offering_id: int, teacher_id: str
    ) -> TeacherCourseAssignment | None:
        """Return one teacher assignment for an offering if it exists."""
        stmt = select(TeacherCourseAssignment).where(
            TeacherCourseAssignment.offering_id == offering_id,
            TeacherCourseAssignment.teacher_id == teacher_id,
        )
        result = await db.exec(stmt)
        return result.first()

    async def delete_by_offering(self, db: AsyncSession, offering_id: int) -> int:
        """Delete all assignments for an offering and return affected rows."""
        stmt = delete(TeacherCourseAssignment).where(
            TeacherCourseAssignment.offering_id == offering_id
        )
        result = await db.exec(stmt)
        await db.flush()
        return result.rowcount or 0

    async def delete_by_offering_and_teacher(
        self, db: AsyncSession, offering_id: int, teacher_id: str
    ) -> bool:
        """Delete one teacher assignment if present."""
        stmt = delete(TeacherCourseAssignment).where(
            TeacherCourseAssignment.offering_id == offering_id,
            TeacherCourseAssignment.teacher_id == teacher_id,
        )
        result = await db.exec(stmt)
        await db.flush()
        return (result.rowcount or 0) > 0


teacher_assignment_crud = TeacherAssignmentCRUD()
