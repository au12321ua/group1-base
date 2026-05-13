"""FileStorageService — file upload, download, and management."""

import warnings

from sqlmodel.ext.asyncio.session import AsyncSession


class FileStorageService:
    """File upload/download with type/size validation."""

    def __init__(self) -> None:
        warnings.warn("TODO: FileStorageService — implement all methods")

    async def upload_file(
        self,
        db: AsyncSession,
        *,
        owner_user_id: str,
        file_name: str,
        file_type: str,
        file_size: int,
        content: bytes,
    ) -> dict:
        """Validate file type/size → write to disk → save metadata → return access info."""
        warnings.warn("TODO: implement upload_file")
        raise NotImplementedError("upload_file not implemented")

    async def get_file(self, db: AsyncSession, file_id: int) -> tuple[bytes, str]:
        """Retrieve file content and MIME type."""
        warnings.warn("TODO: implement get_file")
        raise NotImplementedError("get_file not implemented")

    async def delete_file(self, db: AsyncSession, file_id: int, owner_user_id: str) -> None:
        """Delete file (owner or admin only)."""
        warnings.warn("TODO: implement delete_file")
        raise NotImplementedError("delete_file not implemented")

    async def generate_access_url(self, db: AsyncSession, file_id: int) -> str:
        """Generate a time-limited access URL for a file."""
        warnings.warn("TODO: implement generate_access_url")
        raise NotImplementedError("generate_access_url not implemented")


file_storage_service = FileStorageService()
