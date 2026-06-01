"""Info Service database models (SQLModel)."""

# Import all model modules so their tables are registered in SQLModel.metadata
# before lifespan calls metadata.create_all.
import info_service.models.academic_calendar  # noqa: F401
import info_service.models.audit_log  # noqa: F401
import info_service.models.base_info_item  # noqa: F401
import info_service.models.classroom  # noqa: F401
import info_service.models.course  # noqa: F401
import info_service.models.course_offering  # noqa: F401
import info_service.models.course_prerequisite  # noqa: F401
import info_service.models.course_schedule  # noqa: F401
import info_service.models.file_resource  # noqa: F401
import info_service.models.teacher_assignment  # noqa: F401
import info_service.models.training_program  # noqa: F401
import info_service.models.training_program_course  # noqa: F401
import info_service.models.user  # noqa: F401
import info_service.models.user_profile  # noqa: F401
