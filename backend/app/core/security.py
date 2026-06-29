"""
Security utilities: password hashing (bcrypt) and JWT creation/validation.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

settings = get_settings()


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt. Never store plaintext passwords."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(subject: str, role: str, expires_minutes: int | None = None) -> str:
    """
    Create a signed JWT access token.

    subject: unique identifier of the user (we use mobile number for customers,
             and "admin" for the admin token) encoded in the 'sub' claim.
    role:    "customer" or "admin" — used for authorization checks.
    """
    expire_minutes = expires_minutes or settings.access_token_expire_minutes
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)

    to_encode: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT. Raises jwt.PyJWTError subclasses on failure
    (e.g. jwt.ExpiredSignatureError, jwt.InvalidTokenError) which callers
    should catch and convert into HTTP 401 responses.
    """
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    return payload
