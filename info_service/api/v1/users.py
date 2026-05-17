"""Info Service — /users/* endpoints."""

import warnings

from fastapi import APIRouter, Depends, File, UploadFile

from info_service.schemas.user_schema import (
    UserCreateRequest,
    UserImportResult,
    UserListQuery,
    UserPatchRequest,
    UserResponse,
    UserUpdateRequest,
)
from shared.response import APIResponse, ListResponse, SingleResponse

router = APIRouter(tags=["users"])


@router.get("/", response_model=ListResponse[UserResponse])
async def list_users(query: UserListQuery = Depends()) -> ListResponse[UserResponse]:
    """Get paginated user list with filters."""
    warnings.warn("TODO: implement GET /users")
    raise NotImplementedError("GET /users not implemented")


@router.post("/", response_model=SingleResponse[UserResponse])
async def create_user(request: UserCreateRequest) -> SingleResponse[UserResponse]:
    """Create a new user (cross-service sync with Auth Service)."""
    warnings.warn("TODO: implement POST /users")
    raise NotImplementedError("POST /users not implemented")


@router.get("/{user_id}", response_model=SingleResponse[UserResponse])
async def get_user(user_id: int) -> SingleResponse[UserResponse]:
    """Get user detail with profile."""
    warnings.warn("TODO: implement GET /users/{id}")
    raise NotImplementedError("GET /users/{id} not implemented")


@router.put("/{user_id}", response_model=SingleResponse[UserResponse])
async def update_user(user_id: int, request: UserUpdateRequest) -> SingleResponse[UserResponse]:
    """Full update user."""
    warnings.warn("TODO: implement PUT /users/{id}")
    raise NotImplementedError("PUT /users/{id} not implemented")


@router.patch("/{user_id}", response_model=SingleResponse[UserResponse])
async def patch_user(user_id: int, request: UserPatchRequest) -> SingleResponse[UserResponse]:
    """Partial update user (may trigger role sync)."""
    warnings.warn("TODO: implement PATCH /users/{id}")
    raise NotImplementedError("PATCH /users/{id} not implemented")


@router.delete("/{user_id}", response_model=APIResponse[None])
async def delete_user(user_id: int) -> APIResponse[None]:
    """Logical delete user → recycle bin."""
    warnings.warn("TODO: implement DELETE /users/{id}")
    raise NotImplementedError("DELETE /users/{id} not implemented")


@router.post("/import", response_model=SingleResponse[UserImportResult])
async def batch_import_users(file: UploadFile = File(...)) -> SingleResponse[UserImportResult]:
    """CSV batch import users."""
    warnings.warn("TODO: implement POST /users/import")
    raise NotImplementedError("POST /users/import not implemented")
