"""Smoke tests to verify test infrastructure is correctly wired up."""



# ---------------------------------------------------------------------------
# HTTP client fixtures
# ---------------------------------------------------------------------------


class TestAuthClient:
    """Verify auth_service async client can connect."""

    async def test_app_is_accessible(self, async_client_auth):
        """Auth Service app responds to HTTP requests."""
        response = await async_client_auth.get("/docs")
        assert response.status_code == 200

    async def test_openapi_schema(self, async_client_auth):
        """Auth Service exposes OpenAPI schema."""
        response = await async_client_auth.get("/openapi.json")
        assert response.status_code == 200
        body = response.json()
        assert "info" in body
        assert body["info"]["title"] == "STSS Auth Service"


class TestInfoClient:
    """Verify info_service async client can connect."""

    async def test_app_is_accessible(self, async_client_info):
        """Info Service app responds to HTTP requests."""
        response = await async_client_info.get("/docs")
        assert response.status_code == 200

    async def test_openapi_schema(self, async_client_info):
        """Info Service exposes OpenAPI schema."""
        response = await async_client_info.get("/openapi.json")
        assert response.status_code == 200
        body = response.json()
        assert "info" in body
        assert body["info"]["title"] == "STSS Info Service"


# ---------------------------------------------------------------------------
# Database fixtures
# ---------------------------------------------------------------------------


class TestAuthDB:
    """Verify Auth DB session can perform basic CRUD."""

    async def test_create_and_read_user(self, auth_db_session):
        """Can insert and query a User record."""
        from auth_service.models.user import User, UserStatus

        user = User(user_id="u-001", username="alice", status=UserStatus.ACTIVE)
        auth_db_session.add(user)
        await auth_db_session.flush()

        assert user.id is not None
        assert user.user_id == "u-001"

    async def test_create_credential(self, auth_db_session):
        """Can insert a Credential record."""
        from datetime import UTC, datetime

        from auth_service.models.credential import Credential

        cred = Credential(
            user_id="u-001",
            username="alice",
            password_hash="hashed",
            password_salt="salt",
            failed_login_count=0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        auth_db_session.add(cred)
        await auth_db_session.flush()

        assert cred.id is not None


class TestInfoDB:
    """Verify Info DB session can perform basic CRUD."""

    async def test_create_and_read_user(self, info_db_session):
        """Can insert and query a UserInfo record."""
        from info_service.models.user import UserInfo

        user = UserInfo(user_no="S001", username="bob")
        info_db_session.add(user)
        await info_db_session.flush()

        assert user.id is not None
        assert user.user_no == "S001"

    async def test_create_course(self, info_db_session):
        """Can insert a Course record."""
        from info_service.models.course import Course

        course = Course(
            course_code="CS101",
            course_name="计算机科学导论",
            credit=3,
            capacity=100,
            assessment_method="考试",
            is_active=True,
            is_deleted=False,
        )
        info_db_session.add(course)
        await info_db_session.flush()

        assert course.id is not None
        assert course.course_code == "CS101"


class TestAuditDB:
    """Verify Audit DB session can perform basic CRUD."""

    async def test_create_audit_log(self, audit_db_session):
        """Can insert an AuditLog record."""
        from info_service.models.audit_log import AuditLog

        log_entry = AuditLog(
            operator_user_id="u-001",
            operator_role="SYS_ADMIN",
            target_type="user",
            target_id=1,
            action="user_created",
            result="success",
            request_id="req-001",
        )
        audit_db_session.add(log_entry)
        await audit_db_session.flush()

        assert log_entry.id is not None
        assert log_entry.action == "user_created"


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


class TestUtils:
    """Verify shared test utilities work correctly."""

    def test_build_identity_headers_defaults(self):
        """build_identity_headers returns correct default headers."""
        from tests.utils import build_identity_headers

        headers = build_identity_headers()
        assert headers["X-User-Id"] == "test-user-001"
        assert headers["X-User-Role"] == "SYS_ADMIN"
        assert "user:read" in headers["X-User-Permissions"]

    def test_build_identity_headers_custom(self):
        """build_identity_headers accepts custom values."""
        from tests.utils import build_identity_headers

        headers = build_identity_headers(
            user_id="u-custom",
            role="TEACHER",
            permissions=["schedule:read"],
        )
        assert headers["X-User-Id"] == "u-custom"
        assert headers["X-User-Role"] == "TEACHER"
        assert headers["X-User-Permissions"] == "schedule:read"

    def test_build_auth_header(self):
        """build_auth_header returns correct Authorization header."""
        from tests.utils import build_auth_header

        headers = build_auth_header("my-test-token")
        assert headers["Authorization"] == "Bearer my-test-token"

    def test_make_user_payload_defaults(self):
        """make_user_payload returns plausible default payload."""
        from tests.utils import make_user_payload

        payload = make_user_payload()
        assert payload["username"] == "testuser"
        assert payload["user_no"] == "S2026001"
        assert payload["role_ids"] == "1"

    def test_make_user_payload_custom(self):
        """make_user_payload accepts custom values."""
        from tests.utils import make_user_payload

        payload = make_user_payload(user_no="T001", username="teacher1")
        assert payload["user_no"] == "T001"
        assert payload["username"] == "teacher1"
