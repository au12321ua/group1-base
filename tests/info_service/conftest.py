"""Info Service specific test fixtures and overrides.

All shared fixtures (db sessions, clients) are defined in the root tests/conftest.py.
Place info-specific fixtures here when needed.
"""

import pytest

from tests.utils import build_identity_headers


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Shared identity headers with full SYS_ADMIN permissions.

    Defaults cover all known resource:action pairs. Tests that need a
    narrower permission set should build their own headers inline with
    ``build_identity_headers(permissions=[...])`` rather than overriding
    this fixture.
    """
    return build_identity_headers()
