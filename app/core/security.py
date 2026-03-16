"""
This module contains security-related utilities for the application, including
functions for creating and managing JSON Web Tokens (JWTs) for authentication.

Functions:
    create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        Generates a JWT access token with an optional expiration time.

Constants:
    ACCESS_TOKEN_EXPIRE_MINUTES: The default expiration time for access tokens in minutes.
    SECRET_KEY: The secret key used to sign the JWT.
    ALGORITHM: The algorithm used for encoding the JWT.
"""
import os
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)