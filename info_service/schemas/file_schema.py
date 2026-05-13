"""File upload/download request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FileResponse(BaseModel):
    id: int
    owner_user_id: str
    file_name: str
    file_type: str
    file_size: int
    checksum: str = ""
    created_at: Optional[datetime] = None


class FileUploadResponse(BaseModel):
    id: int
    file_name: str
    file_type: str
    file_size: int
    access_url: str
