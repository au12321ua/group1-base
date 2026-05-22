"""Course CRUD — course master data operations."""

from datetime import UTC, datetime

from sqlalchemy import or_
from sqlmodel import delete, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.base import BaseCRUD
from info_service.models.course import Course
from info_service.models.course_prerequisite import CoursePrerequisite
from shared.exceptions import BusinessRuleError, ResourceNotFoundError


class CourseCRUD(BaseCRUD[Course]):
    """Data access for Course model."""

    def __init__(self) -> None:
        super().__init__(Course)

    async def get_by_course_code(self, db: AsyncSession, code: str) -> Course | None:
        """Get course by course_code (unique)."""
        result = await db.exec(select(Course).where(Course.course_code == code))
        return result.first()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        keyword: str | None = None,
        is_active: bool | None = None,
        include_deleted: bool = False,
    ) -> tuple[list[Course], int]:
        """Get paginated course list. Returns (items, total)."""
        conditions = []
        if not include_deleted:
            conditions.append(Course.is_deleted.is_(False))
        if is_active is not None:
            conditions.append(Course.is_active.is_(is_active))
        if keyword:
            pattern = f"%{keyword}%"
            conditions.append(
                or_(Course.course_code.ilike(pattern), Course.course_name.ilike(pattern))
            )

        stmt = select(Course).where(*conditions).offset(skip).limit(limit).order_by(Course.id)
        count_stmt = select(func.count(Course.id)).where(*conditions)

        items = list((await db.exec(stmt)).all())
        total = (await db.exec(count_stmt)).one()
        return items, total

    async def logical_delete(self, db: AsyncSession, course_id: int) -> None:
        """Soft delete a course."""
        course = await self.get(db, course_id)
        if course is None:
            raise ResourceNotFoundError("Course", str(course_id))

        course.is_deleted = True
        course.is_active = False
        course.updated_at = datetime.now(UTC).replace(tzinfo=None)
        await db.flush()
        await db.refresh(course)

    async def list_prerequisites(
        self, db: AsyncSession, course_id: int
    ) -> list[CoursePrerequisite]:
        """List prerequisite relations for a course."""
        stmt = (
            select(CoursePrerequisite)
            .where(CoursePrerequisite.course_id == course_id)
            .order_by(CoursePrerequisite.id)
        )
        result = await db.exec(stmt)
        return list(result.all())

    async def add_prerequisite(
        self,
        db: AsyncSession,
        *,
        course_id: int,
        prerequisite_course_id: int,
        min_grade: str = "",
    ) -> CoursePrerequisite:
        """Create a prerequisite relation for a course."""
        if course_id == prerequisite_course_id:
            raise BusinessRuleError("Course cannot depend on itself")

        course = await self.get(db, course_id)
        prerequisite = await self.get(db, prerequisite_course_id)
        if course is None:
            raise ResourceNotFoundError("Course", str(course_id))
        if prerequisite is None:
            raise ResourceNotFoundError("Course", str(prerequisite_course_id))

        existing_stmt = select(CoursePrerequisite).where(
            CoursePrerequisite.course_id == course_id,
            CoursePrerequisite.prerequisite_course_id == prerequisite_course_id,
        )
        existing = (await db.exec(existing_stmt)).first()
        if existing is not None:
            raise BusinessRuleError("Prerequisite relation already exists")

        relation = CoursePrerequisite(
            course_id=course_id,
            prerequisite_course_id=prerequisite_course_id,
            min_grade=min_grade,
        )
        db.add(relation)
        await db.flush()
        await db.refresh(relation)
        return relation

    async def remove_prerequisite(
        self, db: AsyncSession, *, course_id: int, prerequisite_course_id: int
    ) -> bool:
        """Delete a prerequisite relation if it exists."""
        stmt = delete(CoursePrerequisite).where(
            CoursePrerequisite.course_id == course_id,
            CoursePrerequisite.prerequisite_course_id == prerequisite_course_id,
        )
        result = await db.exec(stmt)
        await db.flush()
        return result.rowcount > 0


course_crud = CourseCRUD()
