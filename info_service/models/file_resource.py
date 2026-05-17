"""FileResource model — uploaded file metadata."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class FileResource(SQLModel, table=True):
    """Metadata for an uploaded file."""

    __tablename__: str = "file_resources"

    id: int | None = Field(default=None, primary_key=True)
    owner_user_id: str = Field(max_length=64, index=True)
    file_name: str = Field(max_length=256)
    file_type: str = Field(max_length=64)  # e.g. jpg, png, pdf, csv
    file_size: int = Field(default=0)  # bytes
    storage_path: str = Field(max_length=512)
    checksum: str = Field(default="", max_length=128)  # SHA-256 hex
    created_at: datetime = Field(default_factory=datetime.utcnow)
