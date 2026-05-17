"""AuditLog CRUD — audit trail write & query operations."""

import warnings
from datetime import datetime

from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.models.audit_log import AuditLog


class AuditLogCRUD:
    """Data access for AuditLog model (Log DB)."""

    def __init__(self) -> None:
        warnings.warn("TODO: AuditLogCRUD — implement all methods")

    async def write(
        self,
        db: AsyncSession,
        *,
        operator_user_id: str,
        operator_role: str,
        target_type: str,
        target_id: str = "",
        action: str,
        result: str,
        reason: str = "",
        request_id: str = "",
    ) -> AuditLog:
        """Write an immutable audit log entry."""
        warnings.warn("TODO: implement write")
        raise NotImplementedError("write not implemented")

    async def search(
        self,
        db: AsyncSession,
        *,
        operator_user_id: str | None = None,
        target_type: str | None = None,
        action: str | None = None,
        result: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[AuditLog], int]:
        """Search audit logs with filters. Returns (items, total)."""
        warnings.warn("TODO: implement search")
        raise NotImplementedError("search not implemented")


audit_log_crud = AuditLogCRUD()
