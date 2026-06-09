"""JWT signing and verification (HS256 / RS256, Auth-internal only)."""

from __future__ import annotations

from typing import Any, Literal

from jose import jwt

from auth_service.core.config import AuthSettings

JwtAlgorithm = Literal["HS256", "RS256"]


def supported_algorithms(settings: AuthSettings) -> list[JwtAlgorithm]:
    """Return enabled JWT algorithms from configuration flags."""
    algorithms: list[JwtAlgorithm] = []
    if settings.jwt_support_hs256:
        algorithms.append("HS256")
    if settings.jwt_support_rs256:
        algorithms.append("RS256")
    return algorithms


def _signing_material(settings: AuthSettings) -> tuple[JwtAlgorithm, str | bytes, str]:
    """Resolve signing algorithm, key, and kid from JWT_SIGNING_ALGORITHM."""
    alg = settings.jwt_signing_algorithm
    if alg not in supported_algorithms(settings):
        raise ValueError(
            f"JWT_SIGNING_ALGORITHM={alg} is not enabled "
            f"(check JWT_SUPPORT_HS256 / JWT_SUPPORT_RS256)"
        )
    if alg == "HS256":
        return "HS256", settings.token_secret_key, settings.jwt_hs256_key_id
    if not settings.jwt_rsa_private_key_pem.strip():
        raise ValueError("RS256 signing requires JWT_RSA_PRIVATE_KEY_PEM")
    return "RS256", settings.jwt_rsa_private_key_pem, settings.jwt_rsa_key_id


def _verification_key(settings: AuthSettings, algorithm: str) -> str | bytes:
    """Resolve verification key for a JWT header algorithm."""
    if algorithm == "HS256":
        if not settings.jwt_support_hs256:
            raise jwt.JWTError("HS256 verification is disabled")
        return settings.token_secret_key
    if algorithm == "RS256":
        if not settings.jwt_support_rs256:
            raise jwt.JWTError("RS256 verification is disabled")
        if not settings.jwt_rsa_public_key_pem.strip():
            raise jwt.JWTError("RS256 verification requires JWT_RSA_PUBLIC_KEY_PEM")
        return settings.jwt_rsa_public_key_pem
    raise jwt.JWTError(f"Unsupported JWT algorithm: {algorithm}")


def encode_jwt(payload: dict[str, Any], settings: AuthSettings) -> str:
    """Sign a JWT using JWT_SIGNING_ALGORITHM."""
    algorithm, signing_key, kid = _signing_material(settings)
    return jwt.encode(
        payload,
        signing_key,
        algorithm=algorithm,
        headers={"kid": kid},
    )


def decode_jwt(token: str, settings: AuthSettings) -> dict[str, Any]:
    """Verify JWT signature; algorithm taken from token header among enabled supports."""
    header = jwt.get_unverified_header(token)
    algorithm = header.get("alg")
    if algorithm not in ("HS256", "RS256"):
        raise jwt.JWTError(f"Unsupported JWT algorithm: {algorithm}")

    verification_key = _verification_key(settings, algorithm)
    return jwt.decode(
        token,
        verification_key,
        algorithms=[algorithm],
        options={"verify_aud": False},
    )
