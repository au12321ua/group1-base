"""CourseManagementService — course, offering, schedule, classroom CRUD orchestration."""

import warnings

from sqlmodel.ext.asyncio.session import AsyncSession


class CourseManagementService:
    """Business logic for courses, offerings, schedules, classrooms, calendars,
    training programs, and base info items."""

    def __init__(self) -> None:
        warnings.warn("TODO: CourseManagementService — implement all methods")

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

    async def create_calendar(self, db: AsyncSession, data) -> dict:
        """Create a calendar entry."""
        warnings.warn("TODO: implement create_calendar")
        raise NotImplementedError("create_calendar not implemented")

    async def update_calendar(self, db: AsyncSession, calendar_id: int, data) -> dict:
        """Update a calendar entry."""
        warnings.warn("TODO: implement update_calendar")
        raise NotImplementedError("update_calendar not implemented")

    async def delete_calendar(self, db: AsyncSession, calendar_id: int) -> None:
        """Delete a calendar entry."""
        warnings.warn("TODO: implement delete_calendar")
        raise NotImplementedError("delete_calendar not implemented")

    async def list_calendars(self, db: AsyncSession, **filters) -> tuple[list, int]:
        """List calendars with filters."""
        warnings.warn("TODO: implement list_calendars")
        raise NotImplementedError("list_calendars not implemented")

    async def get_calendar(self, db: AsyncSession, calendar_id: int) -> dict:
        """Get calendar detail."""
        warnings.warn("TODO: implement get_calendar")
        raise NotImplementedError("get_calendar not implemented")

    async def get_calendar_by_term(self, db: AsyncSession, term_code: str) -> dict | None:
        """Get calendar by term code."""
        warnings.warn("TODO: implement get_calendar_by_term")
        raise NotImplementedError("get_calendar_by_term not implemented")

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

    async def create_base_info(self, db: AsyncSession, data) -> dict:
        """Create a base info item."""
        warnings.warn("TODO: implement create_base_info")
        raise NotImplementedError("create_base_info not implemented")

    async def update_base_info(self, db: AsyncSession, item_id: int, data) -> dict:
        """Update a base info item."""
        warnings.warn("TODO: implement update_base_info")
        raise NotImplementedError("update_base_info not implemented")

    async def delete_base_info(self, db: AsyncSession, item_id: int) -> None:
        """Delete a base info item."""
        warnings.warn("TODO: implement delete_base_info")
        raise NotImplementedError("delete_base_info not implemented")

    async def list_base_info(self, db: AsyncSession, **filters) -> tuple[list, int]:
        """List base info items with filters."""
        warnings.warn("TODO: implement list_base_info")
        raise NotImplementedError("list_base_info not implemented")

    async def get_base_info(self, db: AsyncSession, item_id: int) -> dict:
        """Get base info item detail."""
        warnings.warn("TODO: implement get_base_info")
        raise NotImplementedError("get_base_info not implemented")


course_management_service = CourseManagementService()
