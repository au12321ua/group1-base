"""Shared CRUD modules — data access layer used by both Auth Service and Info Service."""

from shared.crud.audit_log_crud import AuditLogCRUD, audit_log_crud

__all__ = ["AuditLogCRUD", "audit_log_crud"]
