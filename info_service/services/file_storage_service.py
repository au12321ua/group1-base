"""FileStorageService — file upload, download, and management."""

import hashlib
import os

from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.core.config import get_info_settings
from info_service.crud.file_resource_crud import file_resource_crud
from info_service.models.file_resource import FileResource
from shared.exceptions import BusinessRuleError, ResourceNotFoundError


class FileStorageService:
    """File upload/download with type/size validation."""

    def __init__(self) -> None:
        self._settings = get_info_settings()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_file(self, file_type: str, file_size: int) -> None:
        """Validate file type and size against allowed limits."""
        # Path traversal defense: only allow alphanumeric characters
        if not file_type.isalnum():
            raise BusinessRuleError(
                f"File type '{file_type}' contains invalid characters"
            )
        allowed = set(
            t.strip().lower()
            for t in self._settings.allowed_upload_types.split(",")
        )
        if file_type.lower() not in allowed:
            raise BusinessRuleError(
                f"File type '{file_type}' not allowed. Allowed: {', '.join(sorted(allowed))}"
            )

        max_bytes = self._settings.max_upload_size_mb * 1024 * 1024
        if file_size > max_bytes:
            raise BusinessRuleError(
                f"File size {file_size} exceeds limit of {self._settings.max_upload_size_mb} MB"
            )

    def _storage_path(self, file_id: int, file_type: str) -> str:
        """Build the on-disk storage path for a file."""
        ext = file_type.lower()
        filename = f"{file_id}.{ext}"
        # os.path.join handles parent dir traversal by ignoring previous path
        # when the second argument starts with /, so sanitize first
        if filename.startswith("/") or ".." in filename:
            raise BusinessRuleError(f"Invalid file name generated: {filename}")
        return os.path.join(self._settings.upload_dir, filename)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

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
        """Validate file type/size → save metadata → commit DB → write to disk."""
        self._validate_file(file_type, file_size)

        checksum = hashlib.sha256(content).hexdigest()

        # Save metadata first to get an ID
        resource = await file_resource_crud.create(
            db,
            FileResource(
                owner_user_id=owner_user_id,
                file_name=file_name,
                file_type=file_type.lower(),
                file_size=file_size,
                storage_path="",
                checksum=checksum,
            ),
        )

        # Update storage_path in DB and flush
        storage_path = self._storage_path(resource.id, file_type)
        resource.storage_path = storage_path
        await db.flush()

        # Write file to disk AFTER DB is committed
        try:
            os.makedirs(self._settings.upload_dir, exist_ok=True)
            with open(storage_path, "wb") as f:
                f.write(content)
        except Exception:
            # Clean up DB record on disk write failure
            await file_resource_crud.delete(db, resource.id)
            raise BusinessRuleError("Failed to write file to disk; metadata rolled back")

        return {
            "id": resource.id,
            "file_name": file_name,
            "file_type": file_type,
            "file_size": file_size,
            "access_url": f"/api/v1/files/{resource.id}/download",
        }

    async def get_file(self, db: AsyncSession, file_id: int) -> tuple[bytes, str]:
        """Retrieve file content and MIME type from disk."""
        resource = await file_resource_crud.get(db, file_id)
        if not resource:
            raise ResourceNotFoundError("File", str(file_id))

        path = resource.storage_path
        if not os.path.exists(path):
            raise ResourceNotFoundError("File content", str(file_id))

        with open(path, "rb") as f:
            content = f.read()

        mime_map = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "pdf": "application/pdf",
            "csv": "text/csv",
        }
        mime_type = mime_map.get(resource.file_type, "application/octet-stream")
        return content, mime_type

    async def delete_file(
        self, db: AsyncSession, file_id: int, owner_user_id: str, user_role: str = ""
    ) -> None:
        """Delete file — owner or admin only."""
        resource = await file_resource_crud.get(db, file_id)
        if not resource:
            raise ResourceNotFoundError("File", str(file_id))

        is_admin = user_role in ("SYS_ADMIN", "ACADEMIC_ADMIN")
        if resource.owner_user_id != owner_user_id and not is_admin:
            raise BusinessRuleError("Only the file owner or admin can delete this file")

        # Remove from disk
        if resource.storage_path and os.path.exists(resource.storage_path):
            os.remove(resource.storage_path)

        # Remove metadata
        await file_resource_crud.delete(db, file_id)

    async def generate_access_url(self, db: AsyncSession, file_id: int) -> str:
        """Generate an access URL for a file."""
        resource = await file_resource_crud.get(db, file_id)
        if not resource:
            raise ResourceNotFoundError("File", str(file_id))
        return f"/api/v1/files/{file_id}/download"


file_storage_service = FileStorageService()
