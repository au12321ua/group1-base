"""AuditService — audit log writing and retrieval."""

import csv
import io
from datetime import datetime

from sqlmodel.ext.asyncio.session import AsyncSession

from shared.crud.audit_log_crud import audit_log_crud


class AuditService:
    """Writes and retrieves immutable audit trail records."""

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
        await audit_log_crud.write(
            db,
            operator_user_id=operator_user_id,
            operator_role=operator_role,
            target_type=target_type,
            target_id=target_id,
            action=action,
            result=result,
            reason=reason,
            request_id=request_id,
        )

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
        skip = (page - 1) * page_size

        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        return await audit_log_crud.search(
            db,
            operator_user_id=operator_user_id,
            target_type=target_type,
            action=action,
            result=result,
            start_date=start_dt,
            end_date=end_dt,
            skip=skip,
            limit=page_size,
        )

    async def export_audit_logs(
        self,
        db: AsyncSession,
        **filters,
    ) -> str:
        """Export audit logs as CSV. Returns CSV content as string."""
        items, _ = await audit_log_crud.search(
            db,
            operator_user_id=filters.get("operator_user_id"),
            target_type=filters.get("target_type"),
            action=filters.get("action"),
            result=filters.get("result"),
            start_date=(
                datetime.fromisoformat(filters["start_date"])
                if filters.get("start_date")
                else None
            ),
            end_date=(
                datetime.fromisoformat(filters["end_date"])
                if filters.get("end_date")
                else None
            ),
            skip=0,
            limit=10000,  # large limit for export
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "id", "operator_user_id", "operator_role", "target_type",
            "target_id", "action", "result", "reason", "request_id", "created_at",
        ])
        for log in items:
            writer.writerow([
                log.id,
                log.operator_user_id,
                log.operator_role,
                log.target_type,
                log.target_id,
                log.action,
                log.result,
                log.reason,
                log.request_id,
                log.created_at.isoformat() if log.created_at else "",
            ])

        return output.getvalue()


audit_service = AuditService()
