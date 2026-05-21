"""KeyService — JWKS public key management and key rotation support."""

from auth_service.core.config import get_auth_settings
from auth_service.core.security import generate_key_id
from auth_service.schemas.auth_schema import JwksKey, JwksResponse


class KeyService:
    """Manages signing keys and JWKS endpoint."""

    def get_public_keys(self) -> JwksResponse:
        """Return JWKS-formatted public key set (HS256 metadata for prototype)."""
        settings = get_auth_settings()
        return JwksResponse(
            keys=[
                JwksKey(
                    kid=settings.jwt_key_id or generate_key_id(),
                    alg=settings.jwt_algorithm,
                )
            ]
        )

    def rotate_keys(self) -> None:
        """预留密钥轮换；原型阶段不实现具体轮换逻辑。"""
        return None


key_service = KeyService()
