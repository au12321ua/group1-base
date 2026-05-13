"""AuditService — audit log writing and retrieval."""

import warnings

from sqlmodel.ext.asyncio.session import AsyncSession


class AuditService:
    """Writes and retrieves immutable audit trail records."""

    def __init__(self) -> None:
        warnings.warn("TODO: AuditService — implement all methods")

    async def write_audit_log(
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
    ) -> None:
        """Write an audit log entry for a high-risk operation."""
        warnings.warn("TODO: implement write_audit_log")
        raise NotImplementedError("write_audit_log not implemented")

    async def search_audit_logs(
        self,
        db: AsyncSession,
        *,
        operator_user_id: str | None = None,
        target_type: str | None = None,
        action: str | None = None,
        result: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list, int]:
        """Search audit logs with filters. Returns (items, total)."""
        warnings.warn("TODO: implement search_audit_logs")
        raise NotImplementedError("search_audit_logs not implemented")

    async def export_audit_logs(
        self,
        db: AsyncSession,
        **filters,
    ) -> str:
        """Export audit logs as CSV. Returns download URL."""
        warnings.warn("TODO: implement export_audit_logs")
        raise NotImplementedError("export_audit_logs not implemented")


audit_service = AuditService()
