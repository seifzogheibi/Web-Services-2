
"""
This module defines the authentication-related routes for the FastAPI application.

Routes:
    - /auth/register: Register a new user.
    - /auth/login: Authenticate a user and return an access token.
    - /auth/me: Retrieve the current authenticated user's information.
    - /auth/goals: Update the current user's daily nutritional goals.

Dependencies:
    - get_db: Provides a database session.
    - get_current_user: Retrieves the currently authenticated user.

Models:
    - User: Represents a user in the database.

Schemas:
    - UserCreate: Schema for creating a new user.
    - UserOut: Schema for returning user information.
    - Token: Schema for returning an access token.
    - UserGoalsUpdate: Schema for updating user goals.

Utilities:
    - hash_password: Hashes a plain text password.
    - verify_password: Verifies a plain text password against a hashed password.
    - create_access_token: Generates a JWT access token.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token, UserGoalsUpdate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/goals", response_model=UserOut)
def update_my_goals(
    goals_in: UserGoalsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.daily_calorie_goal = goals_in.daily_calorie_goal
    current_user.daily_protein_goal = goals_in.daily_protein_goal
    current_user.daily_carbs_goal = goals_in.daily_carbs_goal
    current_user.daily_fat_goal = goals_in.daily_fat_goal

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user