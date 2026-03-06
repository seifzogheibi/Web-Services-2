from datetime import datetime
from pydantic import BaseModel, Field


class MealItemCreate(BaseModel):
    food_id: int
    grams: float = Field(..., gt=0) # ensure grams is greater than 0


class MealItemOut(BaseModel):
    id: int
    meal_id: int
    food_id: int
    grams: float
    created_at: datetime

    class Config:
        from_attributes = True