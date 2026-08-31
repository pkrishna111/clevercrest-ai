import hashlib
import secrets


def generate_token() -> str:
    """Generate a cryptographically secure URL-safe bearer token."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Return the SHA-256 hexadecimal digest of a token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()