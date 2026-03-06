from pydantic import BaseModel
from datetime import datetime


class FoodBase(BaseModel):
    name: str
    brand: str = ""
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    source: str = "manual"
    external_id: str | None = None


class FoodCreate(FoodBase):
    pass


class FoodUpdate(BaseModel):
    name: str | None = None
    brand: str | None = None
    calories_per_100g: float | None = None
    protein_per_100g: float | None = None
    carbs_per_100g: float | None = None
    fat_per_100g: float | None = None
    source: str | None = None


class FoodOut(FoodBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True