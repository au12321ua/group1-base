"""Info Service configuration via Pydantic Settings."""

from functools import lru_cache

from shared.config import SharedSettings


class InfoSettings(SharedSettings):
    """Info Service settings loaded from environment/.env file."""

    # Database
    info_database_url: str = "sqlite+aiosqlite:///./data/info.db"
    audit_database_url: str = "sqlite+aiosqlite:///./data/audit.db"

    # Auth Service (cross-service calls)
    auth_service_url: str = "http://localhost:8001"
    auth_service_timeout: int = 10  # seconds
    auth_service_client_id: str = "info_service"
    auth_service_client_secret: str = "change-me-service-secret"

    # Role ID constants (from seed data)
    teacher_role_id: int = 2
    student_role_id: int = 1

    # File upload
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 10
    allowed_upload_types: str = "jpg,jpeg,png,pdf,csv"


@lru_cache
def get_info_settings() -> InfoSettings:
    return InfoSettings()
