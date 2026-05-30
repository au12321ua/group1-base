"""DataProvisionService — serve master data snapshots to B/C/F systems."""

import re
from datetime import UTC, datetime

import httpx
from sqlalchemy import or_
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.core.config import get_info_settings
from info_service.models.academic_calendar import AcademicCalendar
from info_service.models.training_program import TrainingProgram
from info_service.models.user import UserInfo
from info_service.models.user_profile import UserProfile
from info_service.schemas.data_provision_schema import (
    AcademicCalendarDataResponse,
    CandidateStudentResponse,
    SelectedStudentsResponse,
    TeacherDataResponse,
    TrainingProgramDataResponse,
)
from shared.exceptions import ExternalServiceError


class DataProvisionService:
    """Provides teacher lists, calendars, training programs, etc. to B/C/F systems."""

    def __init__(self) -> None:
        self._settings = get_info_settings()

    def _role_token_filter(self, role_id: int):
        token = str(role_id)
        return or_(
            UserInfo.role_ids == token,
            UserInfo.role_ids.like(f"{token},%"),
            UserInfo.role_ids.like(f"%,{token},%"),
            UserInfo.role_ids.like(f"%,{token}"),
        )

    def _active_user_conditions(self, role_id: int) -> list:
        return [
            UserInfo.is_deleted == False,  # noqa: E712
            self._role_token_filter(role_id),
            or_(UserProfile.status.is_(None), UserProfile.status == "ACTIVE"),
        ]

    @staticmethod
    def _paginate(page: int, page_size: int) -> tuple[int, int]:
        return (page - 1) * page_size, page_size

    @staticmethod
    def _parse_required_course_ids(value: str) -> list[int]:
        items: list[int] = []
        for token in value.split(","):
            token = token.strip()
            if token.isdigit():
                items.append(int(token))
        return items

    @staticmethod
    def _infer_grade(user_no: str) -> str:
        match = re.match(r"^(\d{4})", user_no)
        return match.group(1) if match else ""

    def _selected_students_url(self) -> str:
        base_url = self._settings.course_selection_service_url.rstrip("/")
        path = self._settings.course_selection_selected_students_path
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{base_url}{path}"

    @staticmethod
    def _ensure_utc(value: datetime | str) -> datetime:
        if isinstance(value, str):
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value if value.tzinfo is not None else value.replace(tzinfo=UTC)

    async def get_user_snapshot_time(self, db: AsyncSession, role_id: int) -> datetime:
        """Return the latest update time for the requested role dataset."""
        conditions = self._active_user_conditions(role_id)
        user_ts = (
            await db.exec(
                select(func.max(UserInfo.updated_at))
                .select_from(UserInfo)
                .join(UserProfile, UserProfile.user_id == UserInfo.id, isouter=True)
                .where(*conditions)
            )
        ).one()
        profile_ts = (
            await db.exec(
                select(func.max(UserProfile.updated_at))
                .select_from(UserInfo)
                .join(UserProfile, UserProfile.user_id == UserInfo.id, isouter=True)
                .where(*conditions)
            )
        ).one()
        candidates = [ts for ts in (user_ts, profile_ts) if ts is not None]
        if not candidates:
            return datetime.now(UTC)
        return self._ensure_utc(max(candidates))

    async def get_teacher_snapshot_time(self, db: AsyncSession) -> datetime:
        """Return the latest update time for teacher data."""
        return await self.get_user_snapshot_time(db, self._settings.teacher_role_id)

    async def get_candidate_student_snapshot_time(self, db: AsyncSession) -> datetime:
        """Return the latest update time for candidate student data."""
        return await self.get_user_snapshot_time(db, self._settings.student_role_id)

    async def list_teachers(
        self, db: AsyncSession, page: int = 1, page_size: int = 100
    ) -> tuple[list[TeacherDataResponse], int]:
        """List all active teachers for B system consumption."""
        skip, limit = self._paginate(page, page_size)
        conditions = self._active_user_conditions(self._settings.teacher_role_id)

        stmt = (
            select(UserInfo, UserProfile)
            .join(UserProfile, UserProfile.user_id == UserInfo.id, isouter=True)
            .where(*conditions)
            .order_by(UserInfo.id)
            .offset(skip)
            .limit(limit)
        )
        count_stmt = (
            select(func.count(UserInfo.id))
            .select_from(UserInfo)
            .join(UserProfile, UserProfile.user_id == UserInfo.id, isouter=True)
            .where(*conditions)
        )

        rows = (await db.exec(stmt)).all()
        total = (await db.exec(count_stmt)).one()
        items = [
            TeacherDataResponse(
                user_id=str(user.id),
                user_no=user.user_no,
                username=user.username,
                full_name=profile.full_name if profile else "",
                email=profile.email if profile else "",
                phone=profile.phone if profile else "",
            )
            for user, profile in rows
        ]
        return items, total

    async def list_candidate_students(
        self, db: AsyncSession, page: int = 1, page_size: int = 100
    ) -> tuple[list[CandidateStudentResponse], int]:
        """List all active candidate students for B system."""
        skip, limit = self._paginate(page, page_size)
        conditions = self._active_user_conditions(self._settings.student_role_id)

        stmt = (
            select(UserInfo, UserProfile)
            .join(UserProfile, UserProfile.user_id == UserInfo.id, isouter=True)
            .where(*conditions)
            .order_by(UserInfo.id)
            .offset(skip)
            .limit(limit)
        )
        count_stmt = (
            select(func.count(UserInfo.id))
            .select_from(UserInfo)
            .join(UserProfile, UserProfile.user_id == UserInfo.id, isouter=True)
            .where(*conditions)
        )

        rows = (await db.exec(stmt)).all()
        total = (await db.exec(count_stmt)).one()
        items = [
            CandidateStudentResponse(
                user_id=str(user.id),
                user_no=user.user_no,
                username=user.username,
                full_name=profile.full_name if profile else "",
                grade=self._infer_grade(user.user_no),
            )
            for user, profile in rows
        ]
        return items, total

    async def get_calendars(
        self, db: AsyncSession
    ) -> list[AcademicCalendarDataResponse]:
        """Get all academic calendars for B system."""
        stmt = select(AcademicCalendar).order_by(AcademicCalendar.id)
        calendars = list((await db.exec(stmt)).all())
        return [
            AcademicCalendarDataResponse(
                id=calendar.id,
                term_code=calendar.term_code,
                term_name=calendar.term_name,
                start_date=calendar.start_date,
                end_date=calendar.end_date,
                version=calendar.version,
                snapshot_time=self._ensure_utc(calendar.snapshot_time),
            )
            for calendar in calendars
        ]

    async def list_training_programs(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 100,
        major_code: str | None = None,
        grade: str | None = None,
        version: str | None = None,
    ) -> tuple[list[TrainingProgramDataResponse], int]:
        """List training programs for C system."""
        skip, limit = self._paginate(page, page_size)
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
            .order_by(TrainingProgram.id)
            .offset(skip)
            .limit(limit)
        )
        count_stmt = select(func.count(TrainingProgram.id)).where(*conditions)

        programs = list((await db.exec(stmt)).all())
        total = (await db.exec(count_stmt)).one()
        items = [
            TrainingProgramDataResponse(
                id=program.id,
                program_code=program.program_code,
                major_code=program.major_code,
                grade=program.grade,
                version=program.version,
                required_course_ids=self._parse_required_course_ids(
                    program.required_course_ids
                ),
                snapshot_time=self._ensure_utc(program.snapshot_time),
            )
            for program in programs
        ]
        return items, total

    async def query_selected_students(self, db: AsyncSession, **filters) -> dict:
        """Proxy to C system for selected students query. Not stored locally."""
        del db

        params = {
            key: value
            for key, value in filters.items()
            if value is not None
        }
        try:
            async with httpx.AsyncClient(
                timeout=self._settings.course_selection_service_timeout
            ) as client:
                response = await client.get(self._selected_students_url(), params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            raise ExternalServiceError(
                f"Course selection service returned {exc.response.status_code}"
            ) from exc
        except httpx.HTTPError as exc:
            raise ExternalServiceError("Course selection service is unavailable") from exc
        except ValueError as exc:
            raise ExternalServiceError("Course selection service returned invalid JSON") from exc

        data = payload.get("data", payload) if isinstance(payload, dict) else {}
        if not isinstance(data, dict):
            raise ExternalServiceError("Course selection service returned invalid payload")

        selected_students = SelectedStudentsResponse(
            items=data.get("items", []),
            pagination=data.get("pagination")
            or {
                "total": len(data.get("items", [])),
                "page": filters.get("page", 1),
                "page_size": filters.get("page_size", len(data.get("items", []))),
            },
            snapshot_time=self._ensure_utc(
                data.get("snapshot_time")
                or data.get("snapshotTime")
                or datetime.now(UTC)
            ),
            version=data.get("version", "1.0"),
        )
        return selected_students.model_dump()


data_provision_service = DataProvisionService()
