"""
This module contains dependency functions for the FastAPI application, 
including database session management and user authentication.

Functions:
- get_db: Dependency function to provide a database session for the request.
- get_current_user: Dependency function to retrieve the currently authenticated user 
    based on the provided JWT token.

Dependencies:
- OAuth2PasswordBearer: Used for token-based authentication.
- jose.jwt: Library for decoding and verifying JWT tokens.
- fastapi.Depends: Used to declare dependencies for FastAPI routes.
- sqlalchemy.orm.Session: Provides database session handling.

Usage:
These dependencies are intended to be used in FastAPI routes to handle 
authentication and database interactions seamlessly.
"""
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import SECRET_KEY, ALGORITHM
from app.db.session import SessionLocal
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.get(User, int(user_id))
    if user is None:
        raise credentials_exception

    return user