"""AuditLog CRUD — audit trail write & query operations."""

from datetime import datetime

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from shared.models.audit_log import AuditLog


class AuditLogCRUD:
    """Data access for AuditLog model (Log DB)."""

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
        entry = AuditLog(
            operator_user_id=operator_user_id,
            operator_role=operator_role,
            target_type=target_type,
            target_id=target_id,
            action=action,
            result=result,
            reason=reason,
            request_id=request_id,
        )
        db.add(entry)
        await db.flush()
        return entry

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
        conditions = []

        if operator_user_id:
            conditions.append(AuditLog.operator_user_id == operator_user_id)
        if target_type:
            conditions.append(AuditLog.target_type == target_type)
        if action:
            conditions.append(AuditLog.action == action)
        if result:
            conditions.append(AuditLog.result == result)
        if start_date:
            conditions.append(AuditLog.created_at >= start_date)
        if end_date:
            conditions.append(AuditLog.created_at <= end_date)

        base_query = select(AuditLog)
        count_query = select(func.count()).select_from(AuditLog)
        if conditions:
            base_query = base_query.where(*conditions)
            count_query = count_query.where(*conditions)

        total_result = await db.exec(count_query)
        total = total_result.one()

        items_result = await db.exec(
            base_query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
        )
        return list(items_result.all()), total


audit_log_crud = AuditLogCRUD()
