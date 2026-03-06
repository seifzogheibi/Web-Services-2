from datetime import datetime
from pydantic import BaseModel
from app.schemas.meal_item import MealItemOut


class MealCreate(BaseModel):
    name: str
    eaten_at: datetime


class MealUpdate(BaseModel):
    name: str | None = None
    eaten_at: datetime | None = None


class MealOut(BaseModel):
    id: int
    name: str
    eaten_at: datetime
    created_at: datetime
    items: list[MealItemOut] = []

    class Config:
        from_attributes = True