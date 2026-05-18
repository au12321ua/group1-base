"""Tests for Info Service FastAPI dependencies."""

import pytest

from shared.exceptions import AuthenticationError


class TestGetCurrentUser:
    """Tests for get_current_user dependency — resolves IdentityContext from Gateway headers."""

    async def test_returns_identity_context_with_valid_headers(self):
        """Should return IdentityContext with correct fields when all headers present."""
        from info_service.deps import get_current_user

        ctx = await get_current_user(
            x_user_id="user-001",
            x_user_role="TEACHER",
            x_user_permissions="course:read,offering:read",
            x_request_id="req-123",
        )
        assert ctx.user_id == "user-001"
        assert ctx.role == "TEACHER"
        assert ctx.permissions == ["course:read", "offering:read"]
        assert ctx.request_id == "req-123"

    async def test_raises_when_user_id_missing(self):
        """Should raise AuthenticationError when X-User-Id is None or empty."""
        from info_service.deps import get_current_user

        with pytest.raises(AuthenticationError):
            await get_current_user(x_user_role="TEACHER", x_user_permissions="")

    async def test_raises_when_role_missing(self):
        """Should raise AuthenticationError when X-User-Role is None or empty."""
        from info_service.deps import get_current_user

        with pytest.raises(AuthenticationError):
            await get_current_user(x_user_id="user-001", x_user_permissions="")

    async def test_empty_permissions_when_none(self):
        """Should return empty permissions list when X-User-Permissions is None."""
        from info_service.deps import get_current_user

        ctx = await get_current_user(
            x_user_id="user-001",
            x_user_role="STUDENT",
        )
        assert ctx.permissions == []

    async def test_empty_permissions_when_empty_string(self):
        """Should return empty permissions list when X-User-Permissions is empty string."""
        from info_service.deps import get_current_user

        ctx = await get_current_user(
            x_user_id="user-001",
            x_user_role="STUDENT",
            x_user_permissions="",
        )
        assert ctx.permissions == []

    async def test_default_request_id_when_missing(self):
        """Should use empty string for request_id when X-Request-ID is missing."""
        from info_service.deps import get_current_user

        ctx = await get_current_user(
            x_user_id="user-001",
            x_user_role="STUDENT",
        )
        assert ctx.request_id == ""
