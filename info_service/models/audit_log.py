"""AuditLog model — audit trail stored in Log DB (audit.db)."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class AuditLog(SQLModel, table=True):
    """Immutable audit trail record."""

    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    operator_user_id: str = Field(max_length=64, index=True)
    operator_role: str = Field(max_length=64)
    target_type: str = Field(max_length=64, index=True)  # user, course, role, data_provision
    target_id: str = Field(default="", max_length=128)
    action: str = Field(max_length=64, index=True)  # create, update, delete, import, export
    result: str = Field(max_length=32)  # success / failed
    reason: str = Field(default="", max_length=512)
    request_id: str = Field(max_length=64, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class DeadLetterQueue(SQLModel, table=True):
    """Failed cross-service operations pending retry or manual resolution."""

    __tablename__ = "dead_letter_queue"

    id: Optional[int] = Field(default=None, primary_key=True)
    target_service: str = Field(max_length=64)  # auth_service
    operation: str = Field(max_length=128)  # e.g. POST /internal/users
    payload: str = Field(max_length=4096)  # JSON serialized request
    error_message: str = Field(default="", max_length=1024)
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_retry_at: Optional[datetime] = Field(default=None)


class OperationLog(SQLModel, table=True):
    """Log of data provision / snapshot query operations."""

    __tablename__ = "operation_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    caller_id: str = Field(max_length=64, index=True)  # client_id of calling service
    query_condition: str = Field(default="", max_length=1024)
    snapshot_version: str = Field(default="", max_length=64)
    created_at: datetime = Field(default_factory=datetime.utcnow)
