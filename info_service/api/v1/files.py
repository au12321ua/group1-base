"""Info Service — /files/* endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse

from info_service.api.deps import AuditDbSession, InfoDbSession
from info_service.core.audit import AuditContext
from info_service.core.security import check_resource_access
from info_service.crud.file_resource_crud import file_resource_crud
from info_service.deps import require_permission
from info_service.schemas.file_schema import FileResponse, FileUploadResponse
from info_service.services.file_storage_service import file_storage_service
from shared.exceptions import AppError, AuthorizationError, ResourceNotFoundError
from shared.response import APIResponse
from shared.security import IdentityContext

router = APIRouter(tags=["files"])


@router.post("/", status_code=201, response_model=APIResponse[FileUploadResponse])
async def upload_file(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("file:create"))],
    file: UploadFile = File(...),
) -> APIResponse[FileUploadResponse]:
    """Upload a file (requires file:create permission)."""
    content = await file.read()
    parts = file.filename.rsplit(".", 1) if file.filename else []
    file_type = parts[-1].lower() if len(parts) == 2 else "bin"
    file_name = file.filename or "unnamed"

    audit = AuditContext(audit_db, current_user, "file",
                         action="file_uploaded", reason=f"name={file_name}, size={len(content)}")
    try:
        result = await file_storage_service.upload_file(
            db,
            owner_user_id=current_user.user_id,
            file_name=file_name,
            file_type=file_type,
            file_size=len(content),
            content=content,
        )
        await audit.log_success(target_id=str(result["id"]))
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return APIResponse(data=FileUploadResponse(**result))


@router.get("/{file_id}", response_model=APIResponse[FileResponse])
async def get_file_metadata(
    file_id: int,
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("file:read"))],
) -> APIResponse[FileResponse]:
    """Get file metadata (requires file:read permission, owner or admin)."""
    resource = await file_resource_crud.get(db, file_id)
    if not resource:
        raise ResourceNotFoundError("File", str(file_id))
    if not check_resource_access(
        current_user.user_id, current_user.role,
        resource_owner_id=resource.owner_user_id,
    ):
        raise AuthorizationError("Access denied: not the file owner")
    return APIResponse(
        data=FileResponse(
            id=resource.id,
            owner_user_id=resource.owner_user_id,
            file_name=resource.file_name,
            file_type=resource.file_type,
            file_size=resource.file_size,
            checksum=resource.checksum,
            created_at=resource.created_at,
        )
    )


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("file:read"))],
):
    """Download file content (requires file:read permission, owner or admin)."""
    resource = await file_resource_crud.get(db, file_id)
    if not resource:
        raise ResourceNotFoundError("File", str(file_id))
    if not check_resource_access(
        current_user.user_id, current_user.role,
        resource_owner_id=resource.owner_user_id,
    ):
        raise AuthorizationError("Access denied: not the file owner")
    content, mime_type = await file_storage_service.get_file(db, file_id, resource=resource)
    filename = resource.file_name
    return StreamingResponse(
        iter([content]),
        media_type=mime_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/{file_id}", response_model=APIResponse[None])
async def delete_file(
    file_id: int,
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("file:delete"))],
) -> APIResponse[None]:
    """Delete a file (requires file:delete permission, owner or admin only)."""
    audit = AuditContext(audit_db, current_user, "file",
                         target_id=str(file_id), action="file_deleted")
    try:
        await file_storage_service.delete_file(
            db, file_id, current_user.user_id, current_user.role
        )
        await audit.log_success()
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return APIResponse(data=None)
