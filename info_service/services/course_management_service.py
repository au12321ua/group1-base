"""CourseManagementService — course, offering, schedule, classroom CRUD orchestration."""

import warnings

from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.course_crud import course_crud
from info_service.crud.offering_crud import offering_crud
from info_service.crud.training_program_crud import training_program_crud
from info_service.models.course import Course
from info_service.models.course_offering import CourseOffering
from info_service.models.training_program import TrainingProgram
from info_service.schemas.course_schema import (
    CourseCreateRequest,
    CoursePatchRequest,
    CourseUpdateRequest,
)
from info_service.schemas.offering_schema import (
    OfferingCreateRequest,
    OfferingPatchRequest,
    OfferingUpdateRequest,
)
from info_service.schemas.training_program_schema import (
    TrainingProgramCreateRequest,
    TrainingProgramPatchRequest,
    TrainingProgramUpdateRequest,
)
from shared.exceptions import BusinessRuleError, ResourceNotFoundError


class CourseManagementService:
    """Business logic for courses, offerings, schedules, classrooms, calendars,
    training programs, and base info items."""

    @staticmethod
    def _serialize_string_list(values: list[str]) -> str:
        """Store list-like fields as stable comma-separated text."""
        items: list[str] = []
        seen: set[str] = set()
        for value in values:
            normalized = value.strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                items.append(normalized)
        return ",".join(items)

    @staticmethod
    def _serialize_int_list(values: list[int]) -> str:
        """Store integer list fields as comma-separated text."""
        items: list[str] = []
        seen: set[int] = set()
        for value in values:
            if value not in seen:
                seen.add(value)
                items.append(str(value))
        return ",".join(items)

    async def _ensure_course_exists(self, db: AsyncSession, course_id: int) -> Course:
        """Resolve a visible course or raise not found."""
        course = await course_crud.get(db, course_id)
        if course is None or course.is_deleted:
            raise ResourceNotFoundError("Course", str(course_id))
        return course

    async def _ensure_required_courses_exist(
        self, db: AsyncSession, course_ids: list[int]
    ) -> None:
        """Validate every referenced course exists before storing the snapshot."""
        for course_id in course_ids:
            await self._ensure_course_exists(db, course_id)

    async def _ensure_unique_course_code(
        self,
        db: AsyncSession,
        course_code: str,
        *,
        exclude_id: int | None = None,
    ) -> None:
        """Reject duplicate course codes among non-deleted courses."""
        existing = await course_crud.get_by_course_code(
            db, course_code, include_deleted=True
        )
        if existing is None:
            return
        if exclude_id is not None and existing.id == exclude_id:
            return
        raise BusinessRuleError(f"Course code already exists: {course_code}")

    async def _ensure_unique_offering_identity(
        self,
        db: AsyncSession,
        *,
        course_id: int,
        term_code: str,
        class_no: str,
        exclude_id: int | None = None,
    ) -> None:
        """Reject duplicate offerings for the same course, term, and class number."""
        existing = await offering_crud.get_by_course_and_term(db, course_id, term_code)
        for offering in existing:
            if exclude_id is not None and offering.id == exclude_id:
                continue
            if offering.class_no == class_no:
                raise BusinessRuleError(
                    "Offering already exists for course "
                    f"{course_id} in {term_code} class {class_no}"
                )

    async def _ensure_unique_program_code(
        self,
        db: AsyncSession,
        program_code: str,
        *,
        exclude_id: int | None = None,
    ) -> None:
        """Reject duplicate training program codes."""
        existing = await training_program_crud.get_by_program_code(db, program_code)
        if existing is None:
            return
        if exclude_id is not None and existing.id == exclude_id:
            return
        raise BusinessRuleError(f"Training program code already exists: {program_code}")

    # ---- Courses ----

    async def create_course(
        self, db: AsyncSession, data: CourseCreateRequest
    ) -> Course:
        """Create a course."""
        await self._ensure_unique_course_code(db, data.course_code)
        course = Course(**data.model_dump())
        return await course_crud.create(db, course)

    async def update_course(
        self,
        db: AsyncSession,
        course_id: int,
        data: CourseUpdateRequest | CoursePatchRequest,
    ) -> Course:
        """Update a course."""
        course = await self._ensure_course_exists(db, course_id)
        payload = data.model_dump(exclude_unset=True)
        course_code = payload.get("course_code")
        if course_code:
            await self._ensure_unique_course_code(db, course_code, exclude_id=course_id)
        return await course_crud.update(db, course, **payload)

    async def delete_course(self, db: AsyncSession, course_id: int) -> None:
        """Soft delete a course."""
        await course_crud.logical_delete(db, course_id)

    async def list_courses(self, db: AsyncSession, **filters) -> tuple[list[Course], int]:
        """List courses with filters."""
        return await course_crud.get_multi(db, **filters)

    async def get_course(self, db: AsyncSession, course_id: int) -> Course:
        """Get course detail."""
        return await self._ensure_course_exists(db, course_id)

    # ---- Offerings ----

    async def create_offering(
        self, db: AsyncSession, data: OfferingCreateRequest
    ) -> CourseOffering:
        """Create a course offering."""
        await self._ensure_course_exists(db, data.course_id)
        await self._ensure_unique_offering_identity(
            db,
            course_id=data.course_id,
            term_code=data.term_code,
            class_no=data.class_no,
        )
        offering = CourseOffering(
            course_id=data.course_id,
            term_code=data.term_code,
            class_no=data.class_no,
            teacher_ids=self._serialize_string_list(data.teacher_ids),
            capacity=data.capacity,
        )
        return await offering_crud.create(db, offering)

    async def update_offering(
        self,
        db: AsyncSession,
        offering_id: int,
        data: OfferingUpdateRequest | OfferingPatchRequest,
    ) -> CourseOffering:
        """Update a course offering."""
        offering = await offering_crud.get(db, offering_id)
        if offering is None:
            raise ResourceNotFoundError("Offering", str(offering_id))

        payload = data.model_dump(exclude_unset=True)
        target_course_id = payload.get("course_id", offering.course_id)
        target_term_code = payload.get("term_code", offering.term_code)
        target_class_no = payload.get("class_no", offering.class_no)

        await self._ensure_course_exists(db, target_course_id)
        await self._ensure_unique_offering_identity(
            db,
            course_id=target_course_id,
            term_code=target_term_code,
            class_no=target_class_no,
            exclude_id=offering_id,
        )

        if "teacher_ids" in payload and payload["teacher_ids"] is not None:
            payload["teacher_ids"] = self._serialize_string_list(payload["teacher_ids"])

        return await offering_crud.update(db, offering, **payload)

    async def delete_offering(self, db: AsyncSession, offering_id: int) -> None:
        """Delete a course offering."""
        deleted = await offering_crud.delete(db, offering_id)
        if not deleted:
            raise ResourceNotFoundError("Offering", str(offering_id))

    async def list_offerings(
        self, db: AsyncSession, **filters
    ) -> tuple[list[CourseOffering], int]:
        """List offerings with filters."""
        return await offering_crud.get_multi(db, **filters)

    async def get_offering(self, db: AsyncSession, offering_id: int) -> CourseOffering:
        """Get offering detail."""
        offering = await offering_crud.get(db, offering_id)
        if offering is None:
            raise ResourceNotFoundError("Offering", str(offering_id))
        return offering

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

    async def create_training_program(
        self, db: AsyncSession, data: TrainingProgramCreateRequest
    ) -> TrainingProgram:
        """Create a training program."""
        await self._ensure_unique_program_code(db, data.program_code)
        await self._ensure_required_courses_exist(db, data.required_course_ids)
        program = TrainingProgram(
            program_code=data.program_code,
            major_code=data.major_code,
            grade=data.grade,
            version=data.version,
            required_course_ids=self._serialize_int_list(data.required_course_ids),
        )
        return await training_program_crud.create(db, program)

    async def update_training_program(
        self,
        db: AsyncSession,
        program_id: int,
        data: TrainingProgramUpdateRequest | TrainingProgramPatchRequest,
    ) -> TrainingProgram:
        """Update a training program."""
        program = await training_program_crud.get(db, program_id)
        if program is None:
            raise ResourceNotFoundError("TrainingProgram", str(program_id))

        payload = data.model_dump(exclude_unset=True)
        program_code = payload.get("program_code")
        if program_code:
            await self._ensure_unique_program_code(db, program_code, exclude_id=program_id)
        if "required_course_ids" in payload and payload["required_course_ids"] is not None:
            await self._ensure_required_courses_exist(db, payload["required_course_ids"])
            payload["required_course_ids"] = self._serialize_int_list(
                payload["required_course_ids"]
            )
        return await training_program_crud.update(db, program, **payload)

    async def delete_training_program(self, db: AsyncSession, program_id: int) -> None:
        """Delete a training program."""
        deleted = await training_program_crud.delete(db, program_id)
        if not deleted:
            raise ResourceNotFoundError("TrainingProgram", str(program_id))

    async def list_training_programs(
        self, db: AsyncSession, **filters
    ) -> tuple[list[TrainingProgram], int]:
        """List training programs with filters."""
        return await training_program_crud.get_multi(db, **filters)

    async def get_training_program(self, db: AsyncSession, program_id: int) -> TrainingProgram:
        """Get training program detail."""
        program = await training_program_crud.get(db, program_id)
        if program is None:
            raise ResourceNotFoundError("TrainingProgram", str(program_id))
        return program

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
