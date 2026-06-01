"""UserManagementService — user lifecycle, cross-service sync, batch import."""

import csv
import io
import logging

import httpx
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.core.config import get_info_settings
from info_service.crud.user_crud import user_crud
from info_service.crud.user_profile_crud import user_profile_crud
from info_service.models.user import UserInfo
from info_service.models.user_profile import UserProfile
from info_service.schemas.user_schema import (
    UserCreateRequest,
    UserImportResult,
    UserPatchRequest,
    UserProfileSchema,
    UserResponse,
    UserUpdateRequest,
)
from shared.exceptions import BusinessRuleError, ResourceNotFoundError

logger = logging.getLogger("user_management_service")


class UserManagementService:
    """Full user lifecycle management with cross-service coordination."""

    def __init__(self) -> None:
        self._settings = get_info_settings()

    # ------------------------------------------------------------------
    # Auth Service HTTP helpers
    # ------------------------------------------------------------------

    def _auth_url(self, path: str) -> str:
        return f"{self._settings.auth_service_url}/api/v1/internal{path}"

    async def _sync_create_to_auth(
        self, user_id: int, username: str, role_ids: list[int]
    ) -> bool:
        """POST /internal/users — create auth user. Returns True on success."""
        settings = self._settings
        try:
            async with httpx.AsyncClient(timeout=settings.auth_service_timeout) as client:
                resp = await client.post(
                    self._auth_url("/users"),
                    json={
                        "user_id": str(user_id),
                        "username": username,
                        "role_ids": role_ids,
                    },
                )
                return resp.status_code == 201
        except Exception:
            logger.exception("Failed to sync create user %s to Auth", user_id)
            return False

    async def _sync_disable_to_auth(self, user_id: int) -> None:
        """POST /internal/users/{id}/disable. Raises on failure for compensation."""
        settings = self._settings
        try:
            async with httpx.AsyncClient(timeout=settings.auth_service_timeout) as client:
                resp = await client.post(
                    self._auth_url(f"/users/{user_id}/disable")
                )
                if resp.status_code != 200:
                    raise RuntimeError(f"Auth disable returned {resp.status_code}")
        except Exception:
            logger.exception("Failed to sync disable user %s to Auth", user_id)
            raise

    async def _sync_enable_to_auth(self, user_id: int) -> None:
        """POST /internal/users/{id}/enable. Raises on failure."""
        settings = self._settings
        try:
            async with httpx.AsyncClient(timeout=settings.auth_service_timeout) as client:
                resp = await client.post(
                    self._auth_url(f"/users/{user_id}/enable")
                )
                if resp.status_code != 200:
                    raise RuntimeError(f"Auth enable returned {resp.status_code}")
        except Exception:
            logger.exception("Failed to sync enable user %s to Auth", user_id)
            raise

    # ------------------------------------------------------------------
    # Response assembly
    # ------------------------------------------------------------------

    async def _build_response(
        self, db: AsyncSession, user: UserInfo
    ) -> UserResponse:
        """Assemble UserResponse from UserInfo + UserProfile.

        Role information is not stored in Info Service — it comes from
        Auth Service via the Gateway (X-User-Role header). The response
        sets role_ids to an empty string; the frontend should obtain
        role information from the Auth Service or the current session.
        """
        profile = await user_profile_crud.get_by_user_id(db, user.id)
        profile_schema = None
        if profile:
            profile_schema = UserProfileSchema(
                full_name=profile.full_name,
                gender=profile.gender,
                email=profile.email,
                phone=profile.phone,
                status=profile.status,
                avatar_file_id=profile.avatar_file_id,
            )
        return UserResponse(
            id=user.id,
            user_no=user.user_no,
            username=user.username,
            is_deleted=user.is_deleted,
            profile=profile_schema,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    # ------------------------------------------------------------------
    # User CRUD
    # ------------------------------------------------------------------

    async def create_user(
        self,
        db: AsyncSession,
        request: UserCreateRequest,
        current_user: object = None,
    ) -> UserResponse:
        """Create a user: write Info DB → HTTP call Auth /internal/users
        → compensate on failure.

        Role information is passed to Auth Service but not stored in the
        Info Service UserInfo model — roles are Auth Service's
        responsibility.
        """
        role_ids = request.role_ids  # list[int]

        # Check uniqueness
        existing = await user_crud.get_by_user_no(db, request.user_no)
        if existing:
            raise BusinessRuleError(f"User with user_no {request.user_no} already exists")
        existing = await user_crud.get_by_username(db, request.username)
        if existing:
            raise BusinessRuleError(f"User with username {request.username} already exists")

        # Write Info DB — no role_ids stored locally
        user = await user_crud.create(
            db,
            UserInfo(
                user_no=request.user_no,
                username=request.username,
            ),
        )
        await user_profile_crud.create(
            db,
            UserProfile(
                user_id=user.id,
                full_name=request.full_name,
                gender=request.gender,
                email=request.email,
                phone=request.phone,
                status="ACTIVE",
            ),
        )
        await db.flush()

        # Cross-service sync — Auth
        success = await self._sync_create_to_auth(user.id, request.username, role_ids)
        if not success:
            # Compensate: delete Info DB records
            await user_profile_crud.delete(db, user.id)
            await user_crud.physical_delete(db, user.id)
            await db.flush()
            raise BusinessRuleError(
                "Failed to create user in Auth Service; Info DB records rolled back"
            )

        return await self._build_response(db, user)

    async def get_user(self, db: AsyncSession, user_id: int) -> UserResponse:
        """Get user detail with profile."""
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            raise ResourceNotFoundError("User", str(user_id))
        return await self._build_response(db, user)

    async def list_users(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        status: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[UserResponse], int]:
        """List users with pagination and filters. Returns (items, total)."""
        skip = (page - 1) * page_size
        users, total = await user_crud.get_multi(
            db,
            skip=skip,
            limit=page_size,
            keyword=keyword,
            status=status,
            include_deleted=False,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        items = [await self._build_response(db, u) for u in users]
        return items, total

    async def update_user(
        self,
        db: AsyncSession,
        user_id: int,
        request: UserUpdateRequest,
        current_user: object = None,
    ) -> UserResponse:
        """Full update user info and profile.

        Role information is managed by Auth Service — Info Service
        does not store or sync roles.
        """
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            raise ResourceNotFoundError("User", str(user_id))

        # Check uniqueness if changing user_no or username
        if request.user_no != user.user_no:
            existing = await user_crud.get_by_user_no(db, request.user_no)
            if existing and existing.id != user_id:
                raise BusinessRuleError(f"User with user_no {request.user_no} already exists")
        if request.username != user.username:
            existing = await user_crud.get_by_username(db, request.username)
            if existing and existing.id != user_id:
                raise BusinessRuleError(f"User with username {request.username} already exists")

        # Update UserInfo — no role_ids stored locally
        await user_crud.update(
            db,
            user,
            user_no=request.user_no,
            username=request.username,
        )

        # Update / create UserProfile
        profile = await user_profile_crud.get_by_user_id(db, user_id)
        if profile:
            await user_profile_crud.update(
                db,
                profile,
                full_name=request.full_name,
                gender=request.gender,
                email=request.email,
                phone=request.phone,
                status=request.status,
            )
        else:
            await user_profile_crud.create(
                db,
                UserProfile(
                    user_id=user.id,
                    full_name=request.full_name,
                    gender=request.gender,
                    email=request.email,
                    phone=request.phone,
                    status=request.status,
                ),
            )

        return await self._build_response(db, user)

    async def patch_user(
        self,
        db: AsyncSession,
        user_id: int,
        request: UserPatchRequest,
        current_user: object = None,
    ) -> UserResponse:
        """Partial update user info and profile.

        Role information is managed by Auth Service — Info Service
        does not store or sync roles.
        """
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            raise ResourceNotFoundError("User", str(user_id))

        patch_data = request.model_dump(exclude_unset=True)

        # Split fields between UserInfo and UserProfile
        user_fields = {}
        profile_fields = {}
        for field, value in patch_data.items():
            if field == "role_ids":
                # role_ids is accepted in the request for backward
                # compatibility but ignored by Info Service — roles are
                # managed exclusively by Auth Service.
                continue
            elif field in ("user_no", "username"):
                # Check uniqueness
                if field == "user_no" and value != user.user_no:
                    existing = await user_crud.get_by_user_no(db, value)
                    if existing and existing.id != user_id:
                        raise BusinessRuleError(f"User with user_no {value} already exists")
                if field == "username" and value != user.username:
                    existing = await user_crud.get_by_username(db, value)
                    if existing and existing.id != user_id:
                        raise BusinessRuleError(f"User with username {value} already exists")
                user_fields[field] = value
            elif field in ("full_name", "gender", "email", "phone", "status"):
                profile_fields[field] = value

        if user_fields:
            await user_crud.update(db, user, **user_fields)

        if profile_fields:
            profile = await user_profile_crud.get_by_user_id(db, user_id)
            if profile:
                await user_profile_crud.update(db, profile, **profile_fields)
            else:
                await user_profile_crud.create(
                    db,
                    UserProfile(user_id=user.id, **profile_fields),
                )

        return await self._build_response(db, user)

    async def logical_delete_user(
        self,
        db: AsyncSession,
        user_id: int,
        current_user: object = None,
    ) -> None:
        """Logical delete: mark isDeleted=true → HTTP disable Auth account."""
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            raise ResourceNotFoundError("User", str(user_id))
        if user.is_deleted:
            raise BusinessRuleError("User already deleted")

        await user_crud.logical_delete(db, user_id)

        # Sync to Auth — with compensation
        try:
            await self._sync_disable_to_auth(user_id)
        except Exception:
            # Compensate: restore user in Info DB
            await user_crud.restore(db, user_id)
            await db.flush()
            raise BusinessRuleError(
                "Failed to disable user in Auth Service; Info DB rolled back"
            )

    async def disable_user(self, db: AsyncSession, user_id: int) -> None:
        """Disable a user account."""
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            raise ResourceNotFoundError("User", str(user_id))
        profile = await user_profile_crud.get_by_user_id(db, user_id)
        if profile:
            await user_profile_crud.update(db, profile, status="DISABLED")

    async def enable_user(self, db: AsyncSession, user_id: int) -> None:
        """Enable a user account."""
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            raise ResourceNotFoundError("User", str(user_id))
        profile = await user_profile_crud.get_by_user_id(db, user_id)
        if profile:
            await user_profile_crud.update(db, profile, status="ACTIVE")

    async def batch_import_users(
        self, db: AsyncSession, csv_content: bytes
    ) -> UserImportResult:
        """Parse CSV → validate each row → create users one-by-one → return summary."""
        text = csv_content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))

        total = 0
        success_count = 0
        failed_count = 0
        errors: list[dict[str, str]] = []

        for row_index, row in enumerate(reader):
            total += 1
            row_num = str(row_index + 2)  # 1-indexed, header is row 1

            user_no = (row.get("user_no") or "").strip()
            username = (row.get("username") or "").strip()
            full_name = (row.get("full_name") or "").strip()

            if not user_no or not username or not full_name:
                failed_count += 1
                errors.append({
                    "row": row_num,
                    "error": "Missing required field: user_no, username, or full_name",
                })
                continue

            # Check if already exists
            existing = await user_crud.get_by_user_no(db, user_no)
            if existing:
                failed_count += 1
                errors.append({"row": row_num, "error": f"User {user_no} already exists"})
                continue

            existing = await user_crud.get_by_username(db, username)
            if existing:
                failed_count += 1
                errors.append({"row": row_num, "error": f"Username {username} already exists"})
                continue

            # Use nested transaction for each row
            try:
                async with db.begin_nested():
                    await self.create_user(
                        db,
                        UserCreateRequest(
                            user_no=user_no,
                            username=username,
                            role_ids=[],
                            full_name=full_name,
                            gender=row.get("gender", ""),
                            email=row.get("email", ""),
                            phone=row.get("phone", ""),
                        ),
                    )
                success_count += 1
            except Exception as e:
                failed_count += 1
                errors.append({"row": row_num, "error": str(e)})
                # Nested transaction already rolled back

        return UserImportResult(
            total=total,
            success_count=success_count,
            failed_count=failed_count,
            errors=errors[:100],
        )


user_management_service = UserManagementService()
