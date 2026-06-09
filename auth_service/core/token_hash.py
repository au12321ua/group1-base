"""Token fingerprinting — store SHA-256 hashes instead of raw JWT strings."""

import hashlib


def hash_token(token: str) -> str:
    """Return hex SHA-256 of a JWT for DB lookup (deterministic, non-reversible)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
