from datetime import datetime
from pydantic import BaseModel


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

    class Config:
        from_attributes = True