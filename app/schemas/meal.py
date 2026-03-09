from datetime import datetime
from typing import Literal
from pydantic import BaseModel

from app.schemas.meal_item import MealItemOut


MealName = Literal["Breakfast", "Lunch", "Dinner", "Snack"]


class MealCreate(BaseModel):
    name: MealName
    eaten_at: datetime


class MealUpdate(BaseModel):
    name: MealName | None = None
    eaten_at: datetime | None = None


class MealOut(BaseModel):
    id: int
    name: str
    eaten_at: datetime
    created_at: datetime
    items: list[MealItemOut] = []

    class Config:
        from_attributes = True