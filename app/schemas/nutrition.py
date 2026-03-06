from pydantic import BaseModel


class MealNutritionOut(BaseModel):
    meal_id: int
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float