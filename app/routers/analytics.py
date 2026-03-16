from datetime import date as date_type, datetime, time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.meal import Meal
from app.models.user import User
from app.schemas.analytics import DailyNutritionOut

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/daily", response_model=DailyNutritionOut)
def get_daily_nutrition(
    date: date_type,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_of_day = datetime.combine(date, time.min)
    end_of_day = datetime.combine(date, time.max)

    meals = (
        db.query(Meal)
        .filter(
            Meal.user_id == current_user.id,
            Meal.eaten_at >= start_of_day,
            Meal.eaten_at <= end_of_day,
        )
        .all()
    )

    total_calories = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0

    for meal in meals:
        for item in meal.items:
            food = item.food
            factor = item.grams / 100.0

            total_calories += food.calories_per_100g * factor
            total_protein += food.protein_per_100g * factor
            total_carbs += food.carbs_per_100g * factor
            total_fat += food.fat_per_100g * factor

    return DailyNutritionOut(
        date=str(date),
        total_calories=round(total_calories, 2),
        total_protein=round(total_protein, 2),
        total_carbs=round(total_carbs, 2),
        total_fat=round(total_fat, 2),
    )