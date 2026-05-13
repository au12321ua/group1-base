"""Info Service — /files/* endpoints."""

import warnings

from fastapi import APIRouter, File, UploadFile

from info_service.schemas.file_schema import FileResponse, FileUploadResponse
from shared.response import APIResponse, SingleResponse

router = APIRouter(tags=["files"])


@router.post("/", response_model=SingleResponse[FileUploadResponse])
async def upload_file(file: UploadFile = File(...)) -> SingleResponse[FileUploadResponse]:
    """Upload a file (requires authentication)."""
    warnings.warn("TODO: implement POST /files")
    raise NotImplementedError("POST /files not implemented")


@router.get("/{file_id}", response_model=SingleResponse[FileResponse])
async def download_file(file_id: int) -> SingleResponse[FileResponse]:
    """Download/get file metadata and access URL."""
    warnings.warn("TODO: implement GET /files/{id}")
    raise NotImplementedError("GET /files/{id} not implemented")


@router.delete("/{file_id}", response_model=APIResponse[None])
async def delete_file(file_id: int) -> APIResponse[None]:
    """Delete a file (owner or admin only)."""
    warnings.warn("TODO: implement DELETE /files/{id}")
    raise NotImplementedError("DELETE /files/{id} not implemented")
