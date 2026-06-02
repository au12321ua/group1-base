"""Info Service v1 router — aggregates all sub-routers."""

from fastapi import APIRouter

from info_service.api.v1.audit_logs import router as audit_logs_router
from info_service.api.v1.base_info import router as base_info_router
from info_service.api.v1.calendars import router as calendars_router
from info_service.api.v1.classrooms import router as classrooms_router
from info_service.api.v1.courses import router as courses_router
from info_service.api.v1.data_provision import router as data_provision_router
from info_service.api.v1.files import router as files_router
from info_service.api.v1.offerings import router as offerings_router
from info_service.api.v1.recycle_bin import router as recycle_bin_router
from info_service.api.v1.schedules import router as schedules_router
from info_service.api.v1.training_programs import router as training_programs_router
from info_service.api.v1.users import router as users_router

router = APIRouter()

router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(courses_router, prefix="/courses", tags=["courses"])
router.include_router(offerings_router, prefix="/offerings", tags=["offerings"])
router.include_router(schedules_router, prefix="/schedules", tags=["schedules"])
router.include_router(calendars_router, prefix="/calendars", tags=["calendars"])
router.include_router(classrooms_router, prefix="/classrooms", tags=["classrooms"])
router.include_router(
    training_programs_router, prefix="/training-programs", tags=["training-programs"]
)
router.include_router(base_info_router, prefix="/base-info", tags=["base-info"])
router.include_router(recycle_bin_router, prefix="/recycle-bin", tags=["recycle-bin"])
router.include_router(files_router, prefix="/files", tags=["files"])
router.include_router(audit_logs_router, prefix="/audit-logs", tags=["audit-logs"])
router.include_router(data_provision_router, prefix="/data-provision", tags=["data-provision"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint for Docker / orchestration."""
    return {"status": "ok"}
