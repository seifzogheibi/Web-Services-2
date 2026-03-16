from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    daily_calorie_goal: float | None = None
    daily_protein_goal: float | None = None
    daily_carbs_goal: float | None = None
    daily_fat_goal: float | None = None

    model_config = {"from_attributes": True}


class UserGoalsUpdate(BaseModel):
    daily_calorie_goal: float
    daily_protein_goal: float
    daily_carbs_goal: float
    daily_fat_goal: float