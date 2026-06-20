"""Unit tests for offering route handlers and helpers."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from info_service.api.v1 import offerings as offering_routes
from info_service.schemas.offering_schema import (
    OfferingCreateRequest,
    OfferingPatchRequest,
    OfferingResponse,
    OfferingUpdateRequest,
)
from shared.exceptions import AuthorizationError
from shared.security import IdentityContext


def _identity(*, user_id: str = "teacher-1", role: str = "SYS_ADMIN") -> IdentityContext:
    return IdentityContext(user_id=user_id, role=role, permissions=[])


def _offering(**overrides) -> SimpleNamespace:
    payload = {
        "id": 1,
        "course_id": 10,
        "term_code": "2026-FALL",
        "class_no": "01",
        "capacity": 60,
        "status": "ACTIVE",
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def _offering_response() -> OfferingResponse:
    return OfferingResponse(
        id=1,
        course_id=10,
        course_code="CS101",
        course_name="Algorithms",
        term_code="2026-FALL",
        class_no="01",
        capacity=60,
        status="ACTIVE",
    )


def _assignment(**overrides) -> SimpleNamespace:
    payload = {"id": 1, "teacher_id": "teacher-1", "offering_id": 1, "role_type": "instructor"}
    payload.update(overrides)
    return SimpleNamespace(**payload)


def _patch_audit(monkeypatch: pytest.MonkeyPatch):
    audit = SimpleNamespace(log_success=AsyncMock(), log_failure=AsyncMock())
    monkeypatch.setattr(offering_routes, "AuditContext", lambda *args, **kwargs: audit)
    return audit


@pytest.mark.unit
class TestOfferingRouteHelpers:
    """Validate helper behavior in the offerings router."""

    async def test_check_offering_access_allows_assigned_teacher(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            offering_routes.course_management_service,
            "get_offering",
            AsyncMock(return_value=_offering()),
        )
        monkeypatch.setattr(
            offering_routes.teacher_assignment_crud,
            "get_by_offering",
            AsyncMock(return_value=[_assignment()]),
        )

        offering = await offering_routes._check_offering_access(
            _identity(role="TEACHER"),
            object(),
            1,
        )

        assert offering.id == 1

    async def test_check_offering_access_rejects_unrelated_teacher(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            offering_routes.course_management_service,
            "get_offering",
            AsyncMock(return_value=_offering()),
        )
        monkeypatch.setattr(
            offering_routes.teacher_assignment_crud,
            "get_by_offering",
            AsyncMock(return_value=[_assignment(teacher_id="teacher-2")]),
        )

        with pytest.raises(AuthorizationError):
            await offering_routes._check_offering_access(
                _identity(user_id="teacher-9", role="TEACHER"),
                object(),
                1,
            )

    async def test_enrich_offering_fetches_course_fields(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            offering_routes.course_management_service,
            "batch_get_courses",
            AsyncMock(
                return_value={
                    10: SimpleNamespace(course_code="CS101", course_name="Algorithms")
                }
            ),
        )

        response = await offering_routes._enrich_offering(object(), _offering())

        assert response.course_code == "CS101"
        assert response.course_name == "Algorithms"

    async def test_enrich_teacher_assignment_fetches_name(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            offering_routes.course_management_service,
            "batch_get_teacher_names",
            AsyncMock(return_value={"teacher-1": "Ada Lovelace"}),
        )

        response = await offering_routes._enrich_teacher_assignment(
            object(),
            _assignment(),
        )

        assert response.teacher_name == "Ada Lovelace"

    def test_teacher_assignment_list_response_uses_item_count(self) -> None:
        response = offering_routes._teacher_assignment_list_response([])

        assert response.data.items == []
        assert response.data.pagination.total == 0


@pytest.mark.unit
class TestOfferingRoutes:
    """Validate direct route handler behavior for offerings."""

    async def test_list_offerings_returns_paginated_enriched_items(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            offering_routes.course_management_service,
            "list_offerings",
            AsyncMock(return_value=([_offering()], 1)),
        )
        monkeypatch.setattr(
            offering_routes.course_management_service,
            "batch_get_courses",
            AsyncMock(
                return_value={
                    10: SimpleNamespace(course_code="CS101", course_name="Algorithms")
                }
            ),
        )

        response = await offering_routes.list_offerings(
            db=object(),
            current_user=_identity(),
            page=1,
            page_size=20,
            course_id=10,
            term_code="2026-FALL",
            status="ACTIVE",
        )

        assert response.data.pagination.total == 1
        assert response.data.items[0].course_name == "Algorithms"

    async def test_create_offering_logs_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        audit = _patch_audit(monkeypatch)
        monkeypatch.setattr(
            offering_routes.course_management_service,
            "create_offering",
            AsyncMock(return_value=_offering()),
        )
        monkeypatch.setattr(
            offering_routes,
            "_enrich_offering",
            AsyncMock(return_value=_offering_response()),
        )

        response = await offering_routes.create_offering(
            db=object(),
            audit_db=object(),
            current_user=_identity(),
            request=OfferingCreateRequest(
                course_id=10,
                term_code="2026-FALL",
                class_no="01",
                capacity=60,
            ),
        )

        assert response.data.course_code == "CS101"
        audit.log_success.assert_awaited_once()

    async def test_get_offering_returns_enriched_response(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            offering_routes.course_management_service,
            "get_offering",
            AsyncMock(return_value=_offering()),
        )
        monkeypatch.setattr(
            offering_routes,
            "_enrich_offering",
            AsyncMock(return_value=_offering_response()),
        )

        response = await offering_routes.get_offering(
            db=object(),
            current_user=_identity(),
            offering_id=1,
        )

        assert response.data.course_name == "Algorithms"

    async def test_list_offering_teachers_returns_enriched_items(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            offering_routes.course_management_service,
            "list_teachers_for_offering",
            AsyncMock(return_value=[_assignment()]),
        )
        monkeypatch.setattr(
            offering_routes.course_management_service,
            "batch_get_teacher_names",
            AsyncMock(return_value={"teacher-1": "Ada Lovelace"}),
        )

        response = await offering_routes.list_offering_teachers(
            db=object(),
            current_user=_identity(),
            offering_id=1,
        )

        assert response.data.pagination.total == 1
        assert response.data.items[0].teacher_id == "teacher-1"
        assert response.data.items[0].teacher_name == "Ada Lovelace"

    async def test_list_offering_teachers_allows_empty_list(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            offering_routes.course_management_service,
            "list_teachers_for_offering",
            AsyncMock(return_value=[]),
        )
        monkeypatch.setattr(
            offering_routes.course_management_service,
            "batch_get_teacher_names",
            AsyncMock(return_value={}),
        )

        response = await offering_routes.list_offering_teachers(
            db=object(),
            current_user=_identity(),
            offering_id=1,
        )

        assert response.data.items == []
        assert response.data.pagination.total == 0

    async def test_update_offering_logs_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        audit = _patch_audit(monkeypatch)
        monkeypatch.setattr(
            offering_routes,
            "_check_offering_access",
            AsyncMock(return_value=_offering()),
        )
        monkeypatch.setattr(
            offering_routes.course_management_service,
            "update_offering",
            AsyncMock(return_value=_offering()),
        )
        monkeypatch.setattr(
            offering_routes,
            "_enrich_offering",
            AsyncMock(return_value=_offering_response()),
        )

        response = await offering_routes.update_offering(
            db=object(),
            audit_db=object(),
            current_user=_identity(),
            offering_id=1,
            request=OfferingUpdateRequest(
                course_id=10,
                term_code="2026-FALL",
                class_no="01",
                capacity=60,
                status="ACTIVE",
            ),
        )

        assert response.data.id == 1
        audit.log_success.assert_awaited_once()

    async def test_patch_offering_logs_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        audit = _patch_audit(monkeypatch)
        monkeypatch.setattr(
            offering_routes,
            "_check_offering_access",
            AsyncMock(return_value=_offering()),
        )
        monkeypatch.setattr(
            offering_routes.course_management_service,
            "update_offering",
            AsyncMock(return_value=_offering()),
        )
        monkeypatch.setattr(
            offering_routes,
            "_enrich_offering",
            AsyncMock(return_value=_offering_response()),
        )

        response = await offering_routes.patch_offering(
            db=object(),
            audit_db=object(),
            current_user=_identity(),
            offering_id=1,
            request=OfferingPatchRequest(status="INACTIVE"),
        )

        assert response.data.course_code == "CS101"
        audit.log_success.assert_awaited_once()

    async def test_delete_offering_logs_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        audit = _patch_audit(monkeypatch)
        monkeypatch.setattr(
            offering_routes,
            "_check_offering_access",
            AsyncMock(return_value=_offering()),
        )
        monkeypatch.setattr(
            offering_routes.course_management_service,
            "delete_offering",
            AsyncMock(return_value=None),
        )

        response = await offering_routes.delete_offering(
            db=object(),
            audit_db=object(),
            current_user=_identity(),
            offering_id=1,
        )

        assert response.data is None
        audit.log_success.assert_awaited_once()
