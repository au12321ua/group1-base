"""Password complexity validation for change-password and provisioning."""

import re

from shared.exceptions import BusinessRuleError

_ADMIN_ROLE_CODES = frozenset({"ACADEMIC_ADMIN", "SYS_ADMIN"})


def validate_new_password(new_password: str, role_codes: list[str]) -> None:
    """校验新密码复杂度；不符合时抛出 BusinessRuleError(1006)。"""
    is_admin = bool(_ADMIN_ROLE_CODES.intersection(role_codes))
    if is_admin:
        if len(new_password) < 10:
            raise BusinessRuleError("Password must be at least 10 characters", code=1006)
        if not re.search(r"[A-Z]", new_password):
            raise BusinessRuleError("Password must contain uppercase letter", code=1006)
        if not re.search(r"[a-z]", new_password):
            raise BusinessRuleError("Password must contain lowercase letter", code=1006)
        if not re.search(r"\d", new_password):
            raise BusinessRuleError("Password must contain a digit", code=1006)
        if not re.search(r"[^A-Za-z0-9]", new_password):
            raise BusinessRuleError("Password must contain a special character", code=1006)
        return
    if len(new_password) < 8:
        raise BusinessRuleError("Password must be at least 8 characters", code=1006)
    if not re.search(r"[A-Za-z]", new_password) or not re.search(r"\d", new_password):
        raise BusinessRuleError("Password must contain letters and digits", code=1006)
