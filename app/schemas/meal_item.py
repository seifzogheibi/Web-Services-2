from datetime import datetime
from pydantic import BaseModel


class MealItemCreate(BaseModel):
    food_id: int
    grams: float


class MealItemOut(BaseModel):
    id: int
    meal_id: int
    food_id: int
    grams: float
    created_at: datetime

    class Config:
        from_attributes = True