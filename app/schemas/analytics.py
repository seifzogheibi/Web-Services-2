from pydantic import BaseModel


class DailyNutritionOut(BaseModel):
    date: str
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float