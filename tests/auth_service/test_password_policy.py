"""Tests for password complexity validation."""

import pytest

from auth_service.services.password_policy import validate_new_password
from shared.exceptions import BusinessRuleError


@pytest.mark.unit
class TestPasswordPolicy:
    """Validate admin and non-admin password rules."""

    @pytest.mark.parametrize(
        ("password", "message"),
        [
            ("Short1!", "at least 10 characters"),
            ("lowercase1!", "uppercase"),
            ("UPPERCASE1!", "lowercase"),
            ("NoDigits!!", "digit"),
            ("NoSpecial12", "special character"),
        ],
    )
    def test_admin_password_validation_rejects_invalid_inputs(
        self, password: str, message: str
    ) -> None:
        with pytest.raises(BusinessRuleError, match=message) as exc_info:
            validate_new_password(password, ["SYS_ADMIN"])

        assert exc_info.value.code == 1006

    def test_admin_password_validation_accepts_valid_password(self) -> None:
        validate_new_password("ValidAdmin1!", ["ACADEMIC_ADMIN"])

    @pytest.mark.parametrize(
        ("password", "message"),
        [
            ("Short1", "at least 8 characters"),
            ("password", "letters and digits"),
            ("12345678", "letters and digits"),
        ],
    )
    def test_non_admin_password_validation_rejects_invalid_inputs(
        self, password: str, message: str
    ) -> None:
        with pytest.raises(BusinessRuleError, match=message) as exc_info:
            validate_new_password(password, ["TEACHER"])

        assert exc_info.value.code == 1006

    def test_non_admin_password_validation_accepts_valid_password(self) -> None:
        validate_new_password("Teacher123", ["TEACHER"])
