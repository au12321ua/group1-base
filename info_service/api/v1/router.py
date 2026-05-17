"""Info Service v1 router — aggregates all sub-routers."""

import warnings

from fastapi import APIRouter

warnings.warn("TODO: import and include all sub-routers")

router = APIRouter()

# Sub-routers will be included here:
# router.include_router(users_router, prefix="/users", tags=["users"])
# router.include_router(courses_router, prefix="/courses", tags=["courses"])
# router.include_router(offerings_router, prefix="/offerings", tags=["offerings"])
# router.include_router(schedules_router, prefix="/schedules", tags=["schedules"])
# router.include_router(calendars_router, prefix="/calendars", tags=["calendars"])
# router.include_router(
#     training_programs_router, prefix="/training-programs", tags=["training-programs"]
# )
# router.include_router(base_info_router, prefix="/base-info", tags=["base-info"])
# router.include_router(recycle_bin_router, prefix="/recycle-bin", tags=["recycle-bin"])
# router.include_router(files_router, prefix="/files", tags=["files"])
# router.include_router(audit_logs_router, prefix="/audit-logs", tags=["audit-logs"])
# router.include_router(data_provision_router, prefix="/data-provision", tags=["data-provision"])
