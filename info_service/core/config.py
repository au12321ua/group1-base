"""Info Service configuration via Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class InfoSettings(BaseSettings):
    """Info Service settings loaded from environment/.env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    env: str = "development"

    # Database
    info_database_url: str = "sqlite+aiosqlite:///./data/info.db"
    audit_database_url: str = "sqlite+aiosqlite:///./data/audit.db"

    # Auth Service (cross-service calls)
    auth_service_url: str = "http://localhost:8001"
    auth_service_timeout: int = 10  # seconds
    teacher_role_id: int = 2
    student_role_id: int = 1

    # Course Selection Service (cross-service calls)
    course_selection_service_url: str = "http://localhost:8003"
    course_selection_selected_students_path: str = "/api/v1/selected-students"
    course_selection_service_timeout: int = 10  # seconds

    # File upload
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 10
    allowed_upload_types: str = "jpg,jpeg,png,pdf,csv"

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Logging
    log_level: str = "DEBUG"
    log_output: str = "console"
    log_dir: str = "./logs"
    log_rotation: str = "daily"
    log_retention: int = 30


@lru_cache
def get_info_settings() -> InfoSettings:
    return InfoSettings()
