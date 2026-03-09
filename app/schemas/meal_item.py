from datetime import datetime
from pydantic import BaseModel, Field


class MealItemFoodOut(BaseModel):
    id: int
    name: str
    brand: str
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    source: str
    external_id: str | None = None

    class Config:
        from_attributes = True


class MealItemCreate(BaseModel):
    food_id: int
    grams: float = Field(..., gt=0)


class MealItemOut(BaseModel):
    id: int
    meal_id: int
    food_id: int
    grams: float
    created_at: datetime
    food: MealItemFoodOut | None = None

    class Config:
        from_attributes = True