"""Info Service — /files/* endpoints."""

from fastapi import APIRouter, Depends, File, UploadFile

from info_service.api.deps import InfoDbSession
from info_service.deps import get_current_user
from info_service.schemas.file_schema import FileResponse, FileUploadResponse
from info_service.services.file_storage_service import file_storage_service
from shared.response import APIResponse
from shared.security import IdentityContext

router = APIRouter(tags=["files"])


@router.post("/", status_code=201, response_model=APIResponse[FileUploadResponse])
async def upload_file(
    db: InfoDbSession,
    current_user: IdentityContext = Depends(get_current_user),
    file: UploadFile = File(...),
) -> APIResponse[FileUploadResponse]:
    """Upload a file (requires authentication)."""
    content = await file.read()
    # Determine file type from extension
    parts = file.filename.rsplit(".", 1) if file.filename else []
    file_type = parts[-1].lower() if len(parts) == 2 else "bin"

    result = await file_storage_service.upload_file(
        db,
        owner_user_id=current_user.user_id,
        file_name=file.filename or "unnamed",
        file_type=file_type,
        file_size=len(content),
        content=content,
    )
    return APIResponse(data=FileUploadResponse(**result))


@router.get("/{file_id}", response_model=APIResponse[FileResponse])
async def get_file_metadata(
    file_id: int, db: InfoDbSession
) -> APIResponse[FileResponse]:
    """Get file metadata."""
    from info_service.crud.file_resource_crud import file_resource_crud
    from shared.exceptions import ResourceNotFoundError

    resource = await file_resource_crud.get(db, file_id)
    if not resource:
        raise ResourceNotFoundError("File", str(file_id))
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


@router.delete("/{file_id}", response_model=APIResponse[None])
async def delete_file(
    file_id: int,
    db: InfoDbSession,
    current_user: IdentityContext = Depends(get_current_user),
) -> APIResponse[None]:
    """Delete a file (owner or admin only)."""
    await file_storage_service.delete_file(db, file_id, current_user.user_id)
    return APIResponse(data=None)
