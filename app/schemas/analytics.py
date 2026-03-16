from pydantic import BaseModel


class DailyNutritionOut(BaseModel):
    date: str
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float


class SuggestedFoodOut(BaseModel):
    food_id: int
    name: str
    brand: str | None = None
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    score: float
    reason: str