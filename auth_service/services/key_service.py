"""KeyService — JWKS public key management and key rotation support."""

import warnings

from auth_service.schemas.auth_schema import JwksKey, JwksResponse


class KeyService:
    """Manages signing keys and JWKS endpoint."""

    def __init__(self) -> None:
        warnings.warn("TODO: KeyService — implement all methods")

    def get_public_keys(self) -> JwksResponse:
        """Return JWKS-formatted public key set.

        Currently HS256 (symmetric), returns key metadata only.
        Reserved for future RS256 migration — interface stays the same.
        """
        warnings.warn("TODO: implement get_public_keys")
        raise NotImplementedError("get_public_keys not implemented")

    def rotate_keys(self) -> None:
        """Rotate signing keys: retire current, promote new.

        Keeps previous key active for a grace period so in-flight tokens
        are not invalidated.
        """
        warnings.warn("TODO: implement rotate_keys — key rotation")
        raise NotImplementedError("rotate_keys not implemented")


key_service = KeyService()
