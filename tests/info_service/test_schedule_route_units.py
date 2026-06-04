"""Unit tests for schedule route handlers and helpers."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from info_service.api.v1 import schedules as schedule_routes
from info_service.schemas.schedule_schema import (
    ScheduleCreateRequest,
    SchedulePatchRequest,
    ScheduleResponse,
    ScheduleUpdateRequest,
    TeacherAssignmentCreateRequest,
    TeacherAssignmentResponse,
)
from shared.exceptions import AuthorizationError
from shared.security import IdentityContext


def _identity(*, user_id: str = "teacher-1", role: str = "SYS_ADMIN") -> IdentityContext:
    return IdentityContext(user_id=user_id, role=role, permissions=[])


def _schedule(**overrides) -> SimpleNamespace:
    payload = {
        "id": 1,
        "offering_id": 10,
        "classroom_id": 20,
        "day_of_week": 2,
        "start_period": 3,
        "end_period": 4,
        "week_range": "1-16",
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def _assignment(**overrides) -> SimpleNamespace:
    payload = {
        "id": 1,
        "teacher_id": "teacher-1",
        "offering_id": 10,
        "role_type": "instructor",
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def _schedule_response(schedule_id: int = 1) -> ScheduleResponse:
    return ScheduleResponse(
        id=schedule_id,
        offering_id=10,
        classroom_id=20,
        day_of_week=2,
        start_period=3,
        end_period=4,
        week_range="1-16",
        course_name="Algorithms",
        offering_term_code="2026-FALL",
        classroom_name="Main A-101",
    )


def _assignment_response(teacher_id: str = "teacher-1") -> TeacherAssignmentResponse:
    return TeacherAssignmentResponse(
        id=1,
        teacher_id=teacher_id,
        teacher_name="Teacher One",
        offering_id=10,
        role_type="instructor",
    )


def _patch_audit(monkeypatch: pytest.MonkeyPatch):
    audit = SimpleNamespace(log_success=AsyncMock(), log_failure=AsyncMock())
    monkeypatch.setattr(schedule_routes, "AuditContext", lambda *args, **kwargs: audit)
    return audit


@pytest.mark.unit
class TestScheduleRouteHelpers:
    """Validate helper behavior in the schedules router."""

    async def test_enrich_schedule_fetches_related_names(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        schedule = _schedule()
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "batch_get_offerings",
            AsyncMock(
                return_value={10: SimpleNamespace(course_id=99, term_code="2026-FALL")}
            ),
        )
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "batch_get_courses",
            AsyncMock(return_value={99: SimpleNamespace(course_name="Algorithms")}),
        )
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "batch_get_classrooms",
            AsyncMock(return_value={20: SimpleNamespace(building="Main", room_no="A-101")}),
        )

        response = await schedule_routes._enrich_schedule(object(), schedule)

        assert response.course_name == "Algorithms"
        assert response.offering_term_code == "2026-FALL"
        assert response.classroom_name == "Main A-101"

    async def test_enrich_teacher_assignment_fetches_name(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "batch_get_teacher_names",
            AsyncMock(return_value={"teacher-1": "Teacher One"}),
        )

        response = await schedule_routes._enrich_teacher_assignment(
            object(),
            _assignment(),
        )

        assert response.teacher_name == "Teacher One"

    def test_teacher_assignment_list_response_uses_item_count(self) -> None:
        response = schedule_routes._teacher_assignment_list_response([_assignment_response()])

        assert response.data.pagination.total == 1
        assert response.data.pagination.page_size == 1

    async def test_check_schedule_access_allows_assigned_teacher(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "get_schedule",
            AsyncMock(return_value=_schedule()),
        )
        monkeypatch.setattr(
            schedule_routes.teacher_assignment_crud,
            "get_by_offering",
            AsyncMock(return_value=[_assignment()]),
        )

        await schedule_routes._check_schedule_access(
            _identity(role="TEACHER"),
            object(),
            1,
        )

    async def test_check_schedule_access_rejects_unrelated_user(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "get_schedule",
            AsyncMock(return_value=_schedule()),
        )
        monkeypatch.setattr(
            schedule_routes.teacher_assignment_crud,
            "get_by_offering",
            AsyncMock(return_value=[_assignment(teacher_id="teacher-2")]),
        )

        with pytest.raises(AuthorizationError):
            await schedule_routes._check_schedule_access(
                _identity(user_id="teacher-9", role="TEACHER"),
                object(),
                1,
            )


@pytest.mark.unit
class TestScheduleRoutes:
    """Validate direct route handler behavior for schedules."""

    async def test_list_schedules_returns_paginated_enriched_items(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "list_schedules",
            AsyncMock(return_value=([_schedule()], 1)),
        )
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "batch_get_offerings",
            AsyncMock(return_value={10: SimpleNamespace(course_id=99, term_code="2026-FALL")}),
        )
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "batch_get_courses",
            AsyncMock(return_value={99: SimpleNamespace(course_name="Algorithms")}),
        )
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "batch_get_classrooms",
            AsyncMock(return_value={20: SimpleNamespace(building="Main", room_no="A-101")}),
        )

        response = await schedule_routes.list_schedules(
            db=object(),
            current_user=_identity(),
            page=1,
            page_size=20,
            offering_id=10,
        )

        assert response.data.pagination.total == 1
        assert response.data.items[0].course_name == "Algorithms"

    async def test_create_schedule_logs_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        audit = _patch_audit(monkeypatch)
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "create_schedule",
            AsyncMock(return_value=_schedule()),
        )
        monkeypatch.setattr(
            schedule_routes,
            "_enrich_schedule",
            AsyncMock(return_value=_schedule_response()),
        )

        response = await schedule_routes.create_schedule(
            db=object(),
            audit_db=object(),
            current_user=_identity(),
            request=ScheduleCreateRequest(
                offering_id=10,
                classroom_id=20,
                day_of_week=2,
                start_period=3,
                end_period=4,
                week_range="1-16",
            ),
        )

        assert response.data.id == 1
        audit.log_success.assert_awaited_once()

    async def test_get_schedule_returns_enriched_response(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "get_schedule",
            AsyncMock(return_value=_schedule()),
        )
        monkeypatch.setattr(
            schedule_routes,
            "_enrich_schedule",
            AsyncMock(return_value=_schedule_response()),
        )

        response = await schedule_routes.get_schedule(
            db=object(),
            current_user=_identity(),
            schedule_id=1,
        )

        assert response.data.classroom_name == "Main A-101"

    async def test_update_schedule_logs_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        audit = _patch_audit(monkeypatch)
        monkeypatch.setattr(schedule_routes, "_check_schedule_access", AsyncMock())
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "update_schedule",
            AsyncMock(return_value=_schedule()),
        )
        monkeypatch.setattr(
            schedule_routes,
            "_enrich_schedule",
            AsyncMock(return_value=_schedule_response()),
        )

        response = await schedule_routes.update_schedule(
            db=object(),
            audit_db=object(),
            current_user=_identity(),
            schedule_id=1,
            request=ScheduleUpdateRequest(
                offering_id=10,
                classroom_id=20,
                day_of_week=2,
                start_period=3,
                end_period=4,
                week_range="1-16",
            ),
        )

        assert response.data.id == 1
        audit.log_success.assert_awaited_once()

    async def test_patch_schedule_logs_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        audit = _patch_audit(monkeypatch)
        monkeypatch.setattr(schedule_routes, "_check_schedule_access", AsyncMock())
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "update_schedule",
            AsyncMock(return_value=_schedule()),
        )
        monkeypatch.setattr(
            schedule_routes,
            "_enrich_schedule",
            AsyncMock(return_value=_schedule_response()),
        )

        response = await schedule_routes.patch_schedule(
            db=object(),
            audit_db=object(),
            current_user=_identity(),
            schedule_id=1,
            request=SchedulePatchRequest(week_range="2-16"),
        )

        assert response.data.week_range == "1-16"
        audit.log_success.assert_awaited_once()

    async def test_delete_schedule_logs_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        audit = _patch_audit(monkeypatch)
        monkeypatch.setattr(schedule_routes, "_check_schedule_access", AsyncMock())
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "delete_schedule",
            AsyncMock(return_value=None),
        )

        response = await schedule_routes.delete_schedule(
            db=object(),
            audit_db=object(),
            current_user=_identity(),
            schedule_id=1,
        )

        assert response.data is None
        audit.log_success.assert_awaited_once()

    async def test_list_teachers_returns_paginated_enriched_items(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "list_teachers_for_schedule",
            AsyncMock(return_value=[_assignment()]),
        )
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "batch_get_teacher_names",
            AsyncMock(return_value={"teacher-1": "Teacher One"}),
        )

        response = await schedule_routes.list_teachers(
            db=object(),
            current_user=_identity(),
            schedule_id=1,
        )

        assert response.data.items[0].teacher_name == "Teacher One"

    async def test_replace_teachers_logs_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        audit = _patch_audit(monkeypatch)
        monkeypatch.setattr(schedule_routes, "_check_schedule_access", AsyncMock())
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "replace_teachers",
            AsyncMock(return_value=[_assignment()]),
        )
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "batch_get_teacher_names",
            AsyncMock(return_value={"teacher-1": "Teacher One"}),
        )

        response = await schedule_routes.replace_teachers(
            db=object(),
            audit_db=object(),
            current_user=_identity(),
            schedule_id=1,
            teacher_ids=["teacher-1"],
        )

        assert response.data.items[0].teacher_name == "Teacher One"
        audit.log_success.assert_awaited_once()

    async def test_add_teachers_logs_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        audit = _patch_audit(monkeypatch)
        monkeypatch.setattr(schedule_routes, "_check_schedule_access", AsyncMock())
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "add_teachers",
            AsyncMock(return_value=[_assignment()]),
        )
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "batch_get_teacher_names",
            AsyncMock(return_value={"teacher-1": "Teacher One"}),
        )

        response = await schedule_routes.add_teachers(
            db=object(),
            audit_db=object(),
            current_user=_identity(),
            schedule_id=1,
            teacher_ids=["teacher-1"],
        )

        assert response.data.items[0].teacher_name == "Teacher One"
        audit.log_success.assert_awaited_once()

    async def test_assign_teacher_logs_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        audit = _patch_audit(monkeypatch)
        monkeypatch.setattr(schedule_routes, "_check_schedule_access", AsyncMock())
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "assign_teacher",
            AsyncMock(return_value=_assignment()),
        )
        monkeypatch.setattr(
            schedule_routes,
            "_enrich_teacher_assignment",
            AsyncMock(return_value=_assignment_response()),
        )

        response = await schedule_routes.assign_teacher(
            db=object(),
            audit_db=object(),
            current_user=_identity(),
            schedule_id=1,
            teacher_id="teacher-1",
            request=TeacherAssignmentCreateRequest(
                teacher_id="teacher-1",
                role_type="assistant",
            ),
        )

        assert response.data.teacher_name == "Teacher One"
        audit.log_success.assert_awaited_once()

    async def test_remove_teacher_logs_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        audit = _patch_audit(monkeypatch)
        monkeypatch.setattr(schedule_routes, "_check_schedule_access", AsyncMock())
        monkeypatch.setattr(
            schedule_routes.course_management_service,
            "remove_teacher",
            AsyncMock(return_value=None),
        )

        response = await schedule_routes.remove_teacher(
            db=object(),
            audit_db=object(),
            current_user=_identity(),
            schedule_id=1,
            teacher_id="teacher-1",
        )

        assert response.data is None
        audit.log_success.assert_awaited_once()
