"""AuditContext — reusable audit log helper for Info Service route handlers.

Encapsulates common audit fields extracted from ``IdentityContext`` and
provides ``log_success`` / ``log_failure`` methods to reduce boilerplate
in write endpoints.

Usage::

    audit = AuditContext(audit_db, current_user, "course",
                         target_id=str(course_id), action="course_updated")
    try:
        result = await service.update_course(db, course_id, request)
        await audit.log_success()
    except AppError as e:
        await audit.log_failure(str(e.message))
        raise
"""

from sqlmodel.ext.asyncio.session import AsyncSession

from shared.security import IdentityContext
from shared.services.audit_service import audit_service


class AuditContext:
    """Holds audit fields for a single operation and persists them on demand.

    Extracts operator identity fields from ``IdentityContext`` so every
    endpoint doesn't repeat the same three lines.  ``target_id`` and other
    fields can be set after construction (useful for create operations where
    the ID is only known after the record is persisted).
    """

    def __init__(
        self,
        db: AsyncSession,
        user: IdentityContext,
        target_type: str,
        *,
        target_id: str = "",
        action: str = "",
        reason: str = "",
    ) -> None:
        self._db = db
        self.operator_user_id = user.user_id
        self.operator_role = user.role
        self.request_id = user.request_id
        self.target_type = target_type
        self.target_id = target_id
        self.action = action
        self.reason = reason

    async def log_success(
        self,
        *,
        target_id: str | None = None,
        action: str | None = None,
        result: str | None = None,
        reason: str | None = None,
    ) -> None:
        """Write an audit log entry; defaults to ``result="success"``.

        Keyword-only arguments override the corresponding instance attributes
        for this call only (the instance is not mutated).  Pass
        ``result="partial"`` for batch operations that partially succeeded.
        """
        await audit_service.write_audit_log(
            self._db,
            operator_user_id=self.operator_user_id,
            operator_role=self.operator_role,
            target_type=self.target_type,
            target_id=target_id if target_id is not None else self.target_id,
            action=action if action is not None else self.action,
            result=result if result is not None else "success",
            reason=reason if reason is not None else self.reason,
            request_id=self.request_id,
        )

    async def log_failure(
        self,
        error_message: str,
        *,
        target_id: str | None = None,
        action: str | None = None,
    ) -> None:
        """Write a ``result="failed"`` audit log entry with the error as reason.

        Keyword-only arguments override the corresponding instance attributes
        for this call only (the instance is not mutated).
        """
        await audit_service.write_audit_log(
            self._db,
            operator_user_id=self.operator_user_id,
            operator_role=self.operator_role,
            target_type=self.target_type,
            target_id=target_id if target_id is not None else self.target_id,
            action=action if action is not None else self.action,
            result="failed",
            reason=error_message,
            request_id=self.request_id,
        )
