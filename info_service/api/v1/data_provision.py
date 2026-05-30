"""Info Service — /data-provision/* endpoints (for B/C/F system consumption)."""

from datetime import UTC, datetime

from fastapi import APIRouter, Query

from info_service.api.deps import InfoDbSession
from info_service.schemas.data_provision_schema import DataProvisionWrapper
from info_service.services.data_provision_service import data_provision_service
from shared.response import APIResponse

router = APIRouter(tags=["data-provision"])


def _pagination(total: int, page: int, page_size: int) -> dict[str, int]:
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def _resolve_version(items: list[dict], requested_version: str | None = None) -> str:
    if requested_version:
        return requested_version
    versions = {
        item.get("version")
        for item in items
        if isinstance(item, dict) and item.get("version")
    }
    if len(versions) == 1:
        return versions.pop()
    return "multiple" if versions else "1.0"


@router.get("/teachers", response_model=APIResponse[DataProvisionWrapper])
async def list_teachers(
    db: InfoDbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=500),
) -> APIResponse[DataProvisionWrapper]:
    """Get teacher list with snapshot metadata (for B 排课 system, Service Token auth)."""
    items, total = await data_provision_service.list_teachers(db, page=page, page_size=page_size)
    serialized_items = [item.model_dump() for item in items]
    snapshot_time = await data_provision_service.get_teacher_snapshot_time(db)
    return APIResponse(
        data=DataProvisionWrapper(
            items=serialized_items,
            pagination=_pagination(total=total, page=page, page_size=page_size),
            snapshot_time=snapshot_time,
        )
    )


@router.get("/candidate-students", response_model=APIResponse[DataProvisionWrapper])
async def list_candidate_students(
    db: InfoDbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=500),
) -> APIResponse[DataProvisionWrapper]:
    """Get candidate student list (for B 排课 system, Service Token auth)."""
    items, total = await data_provision_service.list_candidate_students(
        db, page=page, page_size=page_size
    )
    serialized_items = [item.model_dump() for item in items]
    snapshot_time = await data_provision_service.get_candidate_student_snapshot_time(db)
    return APIResponse(
        data=DataProvisionWrapper(
            items=serialized_items,
            pagination=_pagination(total=total, page=page, page_size=page_size),
            snapshot_time=snapshot_time,
        )
    )


@router.get("/calendars", response_model=APIResponse[DataProvisionWrapper])
async def get_calendars(db: InfoDbSession) -> APIResponse[DataProvisionWrapper]:
    """Get academic calendars (for B 排课 system, Service Token auth)."""
    items = await data_provision_service.get_calendars(db)
    serialized_items = [item.model_dump() for item in items]
    snapshot_time = max(
        (item.snapshot_time for item in items),
        default=datetime.now(UTC),
    )
    return APIResponse(
        data=DataProvisionWrapper(
            items=serialized_items,
            pagination=_pagination(total=len(items), page=1, page_size=len(items)),
            snapshot_time=snapshot_time,
        )
    )


@router.get("/training-programs", response_model=APIResponse[DataProvisionWrapper])
async def list_training_programs(
    db: InfoDbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=500),
    major_code: str | None = Query(default=None),
    grade: str | None = Query(default=None),
    version: str | None = Query(default=None),
) -> APIResponse[DataProvisionWrapper]:
    """Get training programs (for C 选课 system, Service Token auth)."""
    items, total = await data_provision_service.list_training_programs(
        db,
        page=page,
        page_size=page_size,
        major_code=major_code,
        grade=grade,
        version=version,
    )
    serialized_items = [item.model_dump() for item in items]
    snapshot_time = max(
        (item.snapshot_time for item in items),
        default=datetime.now(UTC),
    )
    return APIResponse(
        data=DataProvisionWrapper(
            items=serialized_items,
            pagination=_pagination(total=total, page=page, page_size=page_size),
            snapshot_time=snapshot_time,
            version=_resolve_version(serialized_items, version),
        )
    )


@router.get("/selected-students", response_model=APIResponse[DataProvisionWrapper])
async def query_selected_students(
    db: InfoDbSession,
    course_id: int | None = Query(default=None),
    term_code: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=500),
) -> APIResponse[DataProvisionWrapper]:
    """Proxy query selected students from C system (for B 排课 system)."""
    data = await data_provision_service.query_selected_students(
        db,
        course_id=course_id,
        term_code=term_code,
        page=page,
        page_size=page_size,
    )
    return APIResponse(data=DataProvisionWrapper(**data))
