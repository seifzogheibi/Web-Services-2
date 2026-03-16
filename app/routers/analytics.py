from datetime import date as date_type, datetime, time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.food import Food
from app.models.meal import Meal
from app.models.user import User
from app.schemas.analytics import DailyNutritionOut, SuggestedFoodOut

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

            total_calories += (food.calories_per_100g or 0) * factor
            total_protein += (food.protein_per_100g or 0) * factor
            total_carbs += (food.carbs_per_100g or 0) * factor
            total_fat += (food.fat_per_100g or 0) * factor

    return DailyNutritionOut(
        date=str(date),
        total_calories=round(total_calories, 2),
        total_protein=round(total_protein, 2),
        total_carbs=round(total_carbs, 2),
        total_fat=round(total_fat, 2),
    )


@router.get("/suggestions", response_model=list[SuggestedFoodOut])
def get_goal_gap_suggestions(
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

    remaining_calories = max((current_user.daily_calorie_goal or 0) - total_calories, 0)
    remaining_protein = max((current_user.daily_protein_goal or 0) - total_protein, 0)
    remaining_carbs = max((current_user.daily_carbs_goal or 0) - total_carbs, 0)
    remaining_fat = max((current_user.daily_fat_goal or 0) - total_fat, 0)

    foods = db.query(Food).filter(Food.user_id == current_user.id).all()

    suggestions = []

    for food in foods:
        calories = food.calories_per_100g or 0
        protein = food.protein_per_100g or 0
        carbs = food.carbs_per_100g or 0
        fat = food.fat_per_100g or 0

        score = 0.0

        if remaining_protein > 0:
            score += min(protein, remaining_protein) * 3

        if remaining_carbs > 0:
            score += min(carbs, remaining_carbs) * 1.5

        if remaining_fat > 0:
            score += min(fat, remaining_fat) * 1.2

        if remaining_calories > 0:
            if calories <= remaining_calories:
                score += 20
            else:
                score -= (calories - remaining_calories) * 0.1

        # Prefer protein-dense foods if protein gap is biggest
        if (
            remaining_protein >= remaining_carbs
            and remaining_protein >= remaining_fat
            and protein > 0
        ):
            score += protein * 1.5

        if score <= 0:
            continue

        reason_parts = []
        if remaining_protein > 0 and protein > 0:
            reason_parts.append(f"{round(protein, 1)}g protein")
        if remaining_carbs > 0 and carbs > 0:
            reason_parts.append(f"{round(carbs, 1)}g carbs")
        if remaining_fat > 0 and fat > 0:
            reason_parts.append(f"{round(fat, 1)}g fat")

        suggestions.append(
            SuggestedFoodOut(
                food_id=food.id,
                name=food.name,
                brand=food.brand,
                calories_per_100g=calories,
                protein_per_100g=protein,
                carbs_per_100g=carbs,
                fat_per_100g=fat,
                score=round(score, 2),
                reason=", ".join(reason_parts) if reason_parts else "Fits remaining goals",
            )
        )

    suggestions.sort(key=lambda x: x.score, reverse=True)
    return suggestions[:3]