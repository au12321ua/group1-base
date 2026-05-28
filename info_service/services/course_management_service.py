"""CourseManagementService — course, offering, schedule, classroom CRUD orchestration."""

import warnings

from pydantic import BaseModel
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.classroom_crud import classroom_crud
from info_service.crud.base_info_crud import base_info_crud
from info_service.crud.calendar_crud import calendar_crud
from info_service.crud.course_crud import course_crud
from info_service.crud.offering_crud import offering_crud
from info_service.crud.schedule_crud import schedule_crud
from info_service.crud.teacher_assignment_crud import teacher_assignment_crud
from info_service.crud.training_program_crud import training_program_crud
from info_service.models.classroom import Classroom
from info_service.models.academic_calendar import AcademicCalendar
from info_service.models.base_info_item import BaseInfoItem
from info_service.models.course import Course
from info_service.models.course_offering import CourseOffering
from info_service.models.course_schedule import CourseSchedule
from info_service.models.teacher_assignment import TeacherCourseAssignment
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
from info_service.schemas.schedule_schema import (
    ScheduleCreateRequest,
    SchedulePatchRequest,
    ScheduleUpdateRequest,
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

    async def _ensure_offering_exists(
        self, db: AsyncSession, offering_id: int
    ) -> CourseOffering:
        """Resolve an offering or raise not found."""
        offering = await offering_crud.get(db, offering_id)
        if offering is None:
            raise ResourceNotFoundError("Offering", str(offering_id))
        return offering

    async def _ensure_classroom_exists(self, db: AsyncSession, classroom_id: int) -> Classroom:
        """Resolve a classroom or raise not found."""
        classroom = await classroom_crud.get(db, classroom_id)
        if classroom is None:
            raise ResourceNotFoundError("Classroom", str(classroom_id))
        return classroom

    async def _ensure_schedule_exists(self, db: AsyncSession, schedule_id: int) -> CourseSchedule:
        """Resolve a schedule or raise not found."""
        schedule = await schedule_crud.get(db, schedule_id)
        if schedule is None:
            raise ResourceNotFoundError("Schedule", str(schedule_id))
        return schedule

    async def _ensure_required_courses_exist(
        self, db: AsyncSession, course_ids: list[int]
    ) -> None:
        """Validate every referenced course exists before storing the snapshot."""
        if not course_ids:
            return

        existing_ids = await course_crud.get_existing_ids(db, course_ids)
        for course_id in course_ids:
            if course_id not in existing_ids:
                raise ResourceNotFoundError("Course", str(course_id))

    async def _ensure_unique_course_code(
        self,
        db: AsyncSession,
        course_code: str,
        *,
        exclude_id: int | None = None,
    ) -> None:
        """Reject duplicate course codes, including logically deleted rows.

        SQLite in this project does not support a partial unique index for
        ``course_code`` scoped to active rows only, so a soft-deleted course
        still reserves its original code.
        """
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

        if isinstance(data, OfferingUpdateRequest):
            payload = data.model_dump(exclude_unset=False)
        else:
            payload = data.model_dump(exclude_unset=True)
        target_course_id = payload.get("course_id", offering.course_id)
        target_term_code = payload.get("term_code", offering.term_code)
        target_class_no = payload.get("class_no", offering.class_no)
        identity_changed = (
            target_course_id != offering.course_id
            or target_term_code != offering.term_code
            or target_class_no != offering.class_no
        )

        if identity_changed:
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
        return await self._ensure_offering_exists(db, offering_id)

    # ---- Schedules ----

    @staticmethod
    def _ensure_valid_period_range(start_period: int, end_period: int) -> None:
        """Reject schedule records whose end period precedes the start period."""
        if start_period > end_period:
            raise BusinessRuleError("end_period must be greater than or equal to start_period")

    async def _ensure_schedule_conflict_free(
        self,
        db: AsyncSession,
        *,
        classroom_id: int,
        day_of_week: int,
        start_period: int,
        end_period: int,
        exclude_id: int | None = None,
    ) -> None:
        """Reject overlapping schedules within the same classroom and weekday."""
        conflict = await schedule_crud.check_conflict(
            db,
            classroom_id=classroom_id,
            day_of_week=day_of_week,
            start_period=start_period,
            end_period=end_period,
            exclude_id=exclude_id,
        )
        if conflict:
            raise BusinessRuleError(
                "Schedule conflicts with another entry in the same classroom and period"
            )

    async def create_schedule(
        self, db: AsyncSession, data: ScheduleCreateRequest
    ) -> CourseSchedule:
        """Create a schedule entry (with conflict check)."""
        self._ensure_valid_period_range(data.start_period, data.end_period)
        await self._ensure_offering_exists(db, data.offering_id)
        await self._ensure_classroom_exists(db, data.classroom_id)
        await self._ensure_schedule_conflict_free(
            db,
            classroom_id=data.classroom_id,
            day_of_week=data.day_of_week,
            start_period=data.start_period,
            end_period=data.end_period,
        )
        schedule = CourseSchedule(**data.model_dump())
        return await schedule_crud.create(db, schedule)

    async def update_schedule(
        self,
        db: AsyncSession,
        schedule_id: int,
        data: ScheduleUpdateRequest | SchedulePatchRequest,
    ) -> CourseSchedule:
        """Update a schedule entry."""
        schedule = await self._ensure_schedule_exists(db, schedule_id)

        if isinstance(data, ScheduleUpdateRequest):
            payload = data.model_dump(exclude_unset=False)
        else:
            payload = data.model_dump(exclude_unset=True)

        target_offering_id = payload.get("offering_id", schedule.offering_id)
        target_classroom_id = payload.get("classroom_id", schedule.classroom_id)
        target_day_of_week = payload.get("day_of_week", schedule.day_of_week)
        target_start_period = payload.get("start_period", schedule.start_period)
        target_end_period = payload.get("end_period", schedule.end_period)

        self._ensure_valid_period_range(target_start_period, target_end_period)

        if target_offering_id != schedule.offering_id:
            await self._ensure_offering_exists(db, target_offering_id)
        if target_classroom_id != schedule.classroom_id:
            await self._ensure_classroom_exists(db, target_classroom_id)

        conflict_identity_changed = (
            target_classroom_id != schedule.classroom_id
            or target_day_of_week != schedule.day_of_week
            or target_start_period != schedule.start_period
            or target_end_period != schedule.end_period
        )
        if conflict_identity_changed:
            await self._ensure_schedule_conflict_free(
                db,
                classroom_id=target_classroom_id,
                day_of_week=target_day_of_week,
                start_period=target_start_period,
                end_period=target_end_period,
                exclude_id=schedule_id,
            )

        return await schedule_crud.update(db, schedule, **payload)

    async def delete_schedule(self, db: AsyncSession, schedule_id: int) -> None:
        """Delete a schedule entry."""
        deleted = await schedule_crud.delete(db, schedule_id)
        if not deleted:
            raise ResourceNotFoundError("Schedule", str(schedule_id))

    async def list_schedules(
        self, db: AsyncSession, **filters
    ) -> tuple[list[CourseSchedule], int]:
        """List schedules with filters."""
        return await schedule_crud.get_multi(db, **filters)

    async def get_schedule(self, db: AsyncSession, schedule_id: int) -> CourseSchedule:
        """Get schedule detail."""
        return await self._ensure_schedule_exists(db, schedule_id)

    # ---- Teacher assignments ----

    async def _get_schedule_offering_id(self, db: AsyncSession, schedule_id: int) -> int:
        """Resolve the offering behind a schedule sub-resource."""
        schedule = await self._ensure_schedule_exists(db, schedule_id)
        return schedule.offering_id

    async def list_teachers_for_schedule(
        self, db: AsyncSession, schedule_id: int
    ) -> list[TeacherCourseAssignment]:
        """List teachers assigned to a schedule."""
        offering_id = await self._get_schedule_offering_id(db, schedule_id)
        return await teacher_assignment_crud.get_by_offering(db, offering_id)

    async def replace_teachers(
        self, db: AsyncSession, schedule_id: int, teacher_ids: list[str]
    ) -> list[TeacherCourseAssignment]:
        """Replace all teacher assignments for a schedule."""
        offering_id = await self._get_schedule_offering_id(db, schedule_id)
        normalized_ids = self._serialize_string_list(teacher_ids).split(",")
        normalized_ids = [teacher_id for teacher_id in normalized_ids if teacher_id]

        await teacher_assignment_crud.delete_by_offering(db, offering_id)

        created: list[TeacherCourseAssignment] = []
        for teacher_id in normalized_ids:
            assignment = TeacherCourseAssignment(
                teacher_id=teacher_id,
                offering_id=offering_id,
                role_type="instructor",
            )
            created.append(await teacher_assignment_crud.create(db, assignment))
        return created

    async def add_teachers(
        self, db: AsyncSession, schedule_id: int, teacher_ids: list[str]
    ) -> list[TeacherCourseAssignment]:
        """Add teacher assignments to a schedule."""
        offering_id = await self._get_schedule_offering_id(db, schedule_id)
        normalized_ids = self._serialize_string_list(teacher_ids).split(",")
        normalized_ids = [teacher_id for teacher_id in normalized_ids if teacher_id]

        existing = await teacher_assignment_crud.get_by_offering(db, offering_id)
        existing_by_teacher = {assignment.teacher_id: assignment for assignment in existing}

        for teacher_id in normalized_ids:
            if teacher_id in existing_by_teacher:
                continue
            assignment = TeacherCourseAssignment(
                teacher_id=teacher_id,
                offering_id=offering_id,
                role_type="instructor",
            )
            existing_by_teacher[teacher_id] = await teacher_assignment_crud.create(db, assignment)

        return list(existing_by_teacher.values())

    async def assign_teacher(
        self, db: AsyncSession, schedule_id: int, teacher_id: str, role_type: str
    ) -> TeacherCourseAssignment:
        """Assign a single teacher."""
        offering_id = await self._get_schedule_offering_id(db, schedule_id)
        normalized_teacher_id = teacher_id.strip()
        if not normalized_teacher_id:
            raise BusinessRuleError("teacher_id cannot be empty")
        normalized_role_type = role_type.strip() or "instructor"

        assignment = await teacher_assignment_crud.get_by_offering_and_teacher(
            db, offering_id, normalized_teacher_id
        )
        if assignment is None:
            assignment = TeacherCourseAssignment(
                teacher_id=normalized_teacher_id,
                offering_id=offering_id,
                role_type=normalized_role_type,
            )
            return await teacher_assignment_crud.create(db, assignment)

        return await teacher_assignment_crud.update(
            db,
            assignment,
            role_type=normalized_role_type,
        )

    async def remove_teacher(self, db: AsyncSession, schedule_id: int, teacher_id: str) -> None:
        """Remove a teacher assignment."""
        offering_id = await self._get_schedule_offering_id(db, schedule_id)
        normalized_teacher_id = teacher_id.strip()
        deleted = await teacher_assignment_crud.delete_by_offering_and_teacher(
            db, offering_id, normalized_teacher_id
        )
        if not deleted:
            raise ResourceNotFoundError(
                "TeacherAssignment",
                f"schedule={schedule_id}, teacher={normalized_teacher_id}",
            )

    # ---- Calendars ----

    async def create_calendar(self, db: AsyncSession, data: BaseModel) -> AcademicCalendar:
        """Create a calendar entry from a Pydantic schema."""
        dump = data.model_dump()
        existing = await calendar_crud.get_by_term_code(db, dump["term_code"])
        if existing:
            raise BusinessRuleError(
                f"Calendar with term_code {dump['term_code']} already exists"
            )
        cal = AcademicCalendar(**dump)
        return await calendar_crud.create(db, cal)

    async def update_calendar(
        self, db: AsyncSession, calendar_id: int, data: BaseModel
    ) -> AcademicCalendar:
        """Full update an existing calendar entry."""
        cal = await calendar_crud.get(db, calendar_id)
        if not cal:
            raise ResourceNotFoundError("Calendar", str(calendar_id))
        dump = data.model_dump()
        if dump.get("term_code") != cal.term_code:
            existing = await calendar_crud.get_by_term_code(db, dump["term_code"])
            if existing and existing.id != calendar_id:
                raise BusinessRuleError(
                    f"Calendar with term_code {dump['term_code']} already exists"
                )
        for field, value in dump.items():
            setattr(cal, field, value)
        return await calendar_crud.update(db, cal)

    async def patch_calendar(
        self, db: AsyncSession, calendar_id: int, data: BaseModel
    ) -> AcademicCalendar:
        """Partial update a calendar entry — only provided (non-None) fields."""
        cal = await calendar_crud.get(db, calendar_id)
        if not cal:
            raise ResourceNotFoundError("Calendar", str(calendar_id))
        dump = data.model_dump(exclude_unset=True)
        if "term_code" in dump and dump["term_code"] != cal.term_code:
            existing = await calendar_crud.get_by_term_code(db, dump["term_code"])
            if existing and existing.id != calendar_id:
                raise BusinessRuleError(
                    f"Calendar with term_code {dump['term_code']} already exists"
                )
        for field, value in dump.items():
            if value is not None:
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
        count_result = await db.exec(
            select(func.count()).select_from(AcademicCalendar)
        )
        total = count_result.one()
        return items, total

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
        count_result = await db.exec(
            select(func.count()).select_from(BaseInfoItem)
        )
        total = count_result.one()
        return items, total

    async def get_base_info(self, db: AsyncSession, item_id: int) -> BaseInfoItem:
        """Get base info item detail."""
        item = await base_info_crud.get(db, item_id)
        if not item:
            raise ResourceNotFoundError("BaseInfoItem", str(item_id))
        return item


course_management_service = CourseManagementService()
