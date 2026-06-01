"""Shared service modules — business logic used by both Auth Service and Info Service."""

from shared.services.audit_service import AuditService, audit_service

__all__ = ["AuditService", "audit_service"]
