"""CourseManagementService — course, offering, schedule, classroom CRUD orchestration."""

import warnings

from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.base_info_crud import base_info_crud
from info_service.crud.calendar_crud import calendar_crud
from info_service.models.academic_calendar import AcademicCalendar
from info_service.models.base_info_item import BaseInfoItem
from shared.exceptions import ResourceNotFoundError


class CourseManagementService:
    """Business logic for courses, offerings, schedules, classrooms, calendars,
    training programs, and base info items."""

    # ---- Courses ----

    async def create_course(self, db: AsyncSession, data) -> dict:
        """Create a course."""
        warnings.warn("TODO: implement create_course")
        raise NotImplementedError("create_course not implemented")

    async def update_course(self, db: AsyncSession, course_id: int, data) -> dict:
        """Update a course."""
        warnings.warn("TODO: implement update_course")
        raise NotImplementedError("update_course not implemented")

    async def delete_course(self, db: AsyncSession, course_id: int) -> None:
        """Soft delete a course."""
        warnings.warn("TODO: implement delete_course")
        raise NotImplementedError("delete_course not implemented")

    async def list_courses(self, db: AsyncSession, **filters) -> tuple[list, int]:
        """List courses with filters."""
        warnings.warn("TODO: implement list_courses")
        raise NotImplementedError("list_courses not implemented")

    async def get_course(self, db: AsyncSession, course_id: int) -> dict:
        """Get course detail."""
        warnings.warn("TODO: implement get_course")
        raise NotImplementedError("get_course not implemented")

    # ---- Offerings ----

    async def create_offering(self, db: AsyncSession, data) -> dict:
        """Create a course offering."""
        warnings.warn("TODO: implement create_offering")
        raise NotImplementedError("create_offering not implemented")

    async def update_offering(self, db: AsyncSession, offering_id: int, data) -> dict:
        """Update a course offering."""
        warnings.warn("TODO: implement update_offering")
        raise NotImplementedError("update_offering not implemented")

    async def delete_offering(self, db: AsyncSession, offering_id: int) -> None:
        """Delete a course offering."""
        warnings.warn("TODO: implement delete_offering")
        raise NotImplementedError("delete_offering not implemented")

    async def list_offerings(self, db: AsyncSession, **filters) -> tuple[list, int]:
        """List offerings with filters."""
        warnings.warn("TODO: implement list_offerings")
        raise NotImplementedError("list_offerings not implemented")

    async def get_offering(self, db: AsyncSession, offering_id: int) -> dict:
        """Get offering detail."""
        warnings.warn("TODO: implement get_offering")
        raise NotImplementedError("get_offering not implemented")

    # ---- Schedules ----

    async def create_schedule(self, db: AsyncSession, data) -> dict:
        """Create a schedule entry (with conflict check)."""
        warnings.warn("TODO: implement create_schedule")
        raise NotImplementedError("create_schedule not implemented")

    async def update_schedule(self, db: AsyncSession, schedule_id: int, data) -> dict:
        """Update a schedule entry."""
        warnings.warn("TODO: implement update_schedule")
        raise NotImplementedError("update_schedule not implemented")

    async def delete_schedule(self, db: AsyncSession, schedule_id: int) -> None:
        """Delete a schedule entry."""
        warnings.warn("TODO: implement delete_schedule")
        raise NotImplementedError("delete_schedule not implemented")

    async def list_schedules(self, db: AsyncSession, **filters) -> tuple[list, int]:
        """List schedules with filters."""
        warnings.warn("TODO: implement list_schedules")
        raise NotImplementedError("list_schedules not implemented")

    async def get_schedule(self, db: AsyncSession, schedule_id: int) -> dict:
        """Get schedule detail."""
        warnings.warn("TODO: implement get_schedule")
        raise NotImplementedError("get_schedule not implemented")

    # ---- Teacher assignments ----

    async def list_teachers_for_schedule(self, db: AsyncSession, schedule_id: int) -> list:
        """List teachers assigned to a schedule."""
        warnings.warn("TODO: implement list_teachers_for_schedule")
        raise NotImplementedError("list_teachers_for_schedule not implemented")

    async def replace_teachers(
        self, db: AsyncSession, schedule_id: int, teacher_ids: list[str]
    ) -> list:
        """Replace all teacher assignments for a schedule."""
        warnings.warn("TODO: implement replace_teachers")
        raise NotImplementedError("replace_teachers not implemented")

    async def add_teachers(
        self, db: AsyncSession, schedule_id: int, teacher_ids: list[str]
    ) -> list:
        """Add teacher assignments to a schedule."""
        warnings.warn("TODO: implement add_teachers")
        raise NotImplementedError("add_teachers not implemented")

    async def assign_teacher(
        self, db: AsyncSession, schedule_id: int, teacher_id: str, role_type: str
    ) -> dict:
        """Assign a single teacher."""
        warnings.warn("TODO: implement assign_teacher")
        raise NotImplementedError("assign_teacher not implemented")

    async def remove_teacher(self, db: AsyncSession, schedule_id: int, teacher_id: str) -> None:
        """Remove a teacher assignment."""
        warnings.warn("TODO: implement remove_teacher")
        raise NotImplementedError("remove_teacher not implemented")

    # ---- Calendars ----

    async def create_calendar(self, db: AsyncSession, data: BaseModel) -> AcademicCalendar:
        """Create a calendar entry from a Pydantic schema."""
        cal = AcademicCalendar(**data.model_dump())
        return await calendar_crud.create(db, cal)

    async def update_calendar(
        self, db: AsyncSession, calendar_id: int, data: BaseModel
    ) -> AcademicCalendar:
        """Full update an existing calendar entry."""
        cal = await calendar_crud.get(db, calendar_id)
        if not cal:
            raise ResourceNotFoundError("Calendar", str(calendar_id))
        for field, value in data.model_dump().items():
            setattr(cal, field, value)
        return await calendar_crud.update(db, cal)

    async def patch_calendar(
        self, db: AsyncSession, calendar_id: int, data: BaseModel
    ) -> AcademicCalendar:
        """Partial update a calendar entry — only provided (non-None) fields."""
        cal = await calendar_crud.get(db, calendar_id)
        if not cal:
            raise ResourceNotFoundError("Calendar", str(calendar_id))
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(cal, field, value)
        return await calendar_crud.update(db, cal)

    async def delete_calendar(self, db: AsyncSession, calendar_id: int) -> None:
        """Delete a calendar entry."""
        cal = await calendar_crud.get(db, calendar_id)
        if not cal:
            raise ResourceNotFoundError("Calendar", str(calendar_id))
        await calendar_crud.delete(db, calendar_id)

    async def list_calendars(
        self, db: AsyncSession, page: int = 1, page_size: int = 20
    ) -> tuple[list[AcademicCalendar], int]:
        """List calendars with pagination."""
        skip = (page - 1) * page_size
        items = await calendar_crud.get_multi(db, skip=skip, limit=page_size)
        # TODO: get total count properly — for now return length as estimate
        return items, len(items)

    async def get_calendar(self, db: AsyncSession, calendar_id: int) -> AcademicCalendar:
        """Get calendar detail."""
        cal = await calendar_crud.get(db, calendar_id)
        if not cal:
            raise ResourceNotFoundError("Calendar", str(calendar_id))
        return cal

    async def get_calendar_by_term(
        self, db: AsyncSession, term_code: str
    ) -> AcademicCalendar | None:
        """Get calendar by term code."""
        return await calendar_crud.get_by_term_code(db, term_code)

    # ---- Training Programs ----

    async def create_training_program(self, db: AsyncSession, data) -> dict:
        """Create a training program."""
        warnings.warn("TODO: implement create_training_program")
        raise NotImplementedError("create_training_program not implemented")

    async def update_training_program(self, db: AsyncSession, program_id: int, data) -> dict:
        """Update a training program."""
        warnings.warn("TODO: implement update_training_program")
        raise NotImplementedError("update_training_program not implemented")

    async def delete_training_program(self, db: AsyncSession, program_id: int) -> None:
        """Delete a training program."""
        warnings.warn("TODO: implement delete_training_program")
        raise NotImplementedError("delete_training_program not implemented")

    async def list_training_programs(self, db: AsyncSession, **filters) -> tuple[list, int]:
        """List training programs with filters."""
        warnings.warn("TODO: implement list_training_programs")
        raise NotImplementedError("list_training_programs not implemented")

    async def get_training_program(self, db: AsyncSession, program_id: int) -> dict:
        """Get training program detail."""
        warnings.warn("TODO: implement get_training_program")
        raise NotImplementedError("get_training_program not implemented")

    # ---- Base Info ----

    async def create_base_info(self, db: AsyncSession, data: BaseModel) -> BaseInfoItem:
        """Create a base info item from a Pydantic schema."""
        item = BaseInfoItem(**data.model_dump())
        return await base_info_crud.create(db, item)

    async def update_base_info(
        self, db: AsyncSession, item_id: int, data: BaseModel
    ) -> BaseInfoItem:
        """Full update a base info item."""
        item = await base_info_crud.get(db, item_id)
        if not item:
            raise ResourceNotFoundError("BaseInfoItem", str(item_id))
        for field, value in data.model_dump().items():
            setattr(item, field, value)
        return await base_info_crud.update(db, item)

    async def patch_base_info(
        self, db: AsyncSession, item_id: int, data: BaseModel
    ) -> BaseInfoItem:
        """Partial update a base info item — only provided (non-None) fields."""
        item = await base_info_crud.get(db, item_id)
        if not item:
            raise ResourceNotFoundError("BaseInfoItem", str(item_id))
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        return await base_info_crud.update(db, item)

    async def delete_base_info(self, db: AsyncSession, item_id: int) -> None:
        """Delete a base info item."""
        item = await base_info_crud.get(db, item_id)
        if not item:
            raise ResourceNotFoundError("BaseInfoItem", str(item_id))
        await base_info_crud.delete(db, item_id)

    async def list_base_info(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        category: str | None = None,
    ) -> tuple[list[BaseInfoItem], int]:
        """List base info items, optionally filtered by category."""
        skip = (page - 1) * page_size
        if category:
            return await base_info_crud.get_by_category(
                db, category, skip=skip, limit=page_size
            )
        items = await base_info_crud.get_multi(db, skip=skip, limit=page_size)
        return items, len(items)

    async def get_base_info(self, db: AsyncSession, item_id: int) -> BaseInfoItem:
        """Get base info item detail."""
        item = await base_info_crud.get(db, item_id)
        if not item:
            raise ResourceNotFoundError("BaseInfoItem", str(item_id))
        return item


course_management_service = CourseManagementService()
