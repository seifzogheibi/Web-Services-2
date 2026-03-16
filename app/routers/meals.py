from datetime import date as date_type, datetime, time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.core.dependencies import get_db, get_current_user
from app.models.food import Food
from app.models.meal import Meal
from app.models.meal_item import MealItem
from app.models.user import User
from app.schemas.meal import MealCreate, MealOut, MealUpdate
from app.schemas.meal_item import MealItemCreate, MealItemOut
from app.schemas.nutrition import MealNutritionOut

router = APIRouter(prefix="/meals", tags=["meals"])


@router.post("/", response_model=MealOut, status_code=status.HTTP_201_CREATED)
def create_meal(
    meal: MealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a meal record owned by the authenticated user."""
    db_meal = Meal(**meal.model_dump(), user_id=current_user.id)
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal


@router.patch("/{meal_id}", response_model=MealOut)
def update_meal(
    meal_id: int,
    update: MealUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a user-owned meal by ID."""
    meal = (
        db.query(Meal)
        .filter(Meal.id == meal_id, Meal.user_id == current_user.id)
        .first()
    )

    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(meal, key, value)

    db.commit()
    db.refresh(meal)
    return meal


@router.post("/{meal_id}/items", response_model=MealItemOut, status_code=status.HTTP_201_CREATED)
def add_food_to_meal(
    meal_id: int,
    item: MealItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Attach a food item to a meal using the MealItem junction table.

    Both the meal and the selected food must belong to the authenticated user
    so cross-user access and invalid analytics are prevented.
    """
    meal = (
        db.query(Meal)
        .filter(Meal.id == meal_id, Meal.user_id == current_user.id)
        .first()
    )
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    food = (
        db.query(Food)
        .filter(Food.id == item.food_id, Food.user_id == current_user.id)
        .first()
    )
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    db_item = MealItem(
        meal_id=meal_id,
        food_id=item.food_id,
        grams=item.grams,
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/", response_model=list[MealOut])
def list_meals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all meals owned by the current user.

    Related meal items and foods are eagerly loaded so the frontend can render
    full diary data without repeated follow-up queries.
    """
    meals = (
        db.query(Meal)
        .options(selectinload(Meal.items).selectinload(MealItem.food))
        .filter(Meal.user_id == current_user.id)
        .order_by(Meal.eaten_at.asc())
        .all()
    )
    return meals


@router.get("/by-date", response_model=list[MealOut])
def get_meals_by_date(
    date: date_type,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return only the meals logged by the current user on a selected date."""
    start_of_day = datetime.combine(date, time.min)
    end_of_day = datetime.combine(date, time.max)

    meals = (
        db.query(Meal)
        .options(selectinload(Meal.items).selectinload(MealItem.food))
        .filter(
            Meal.user_id == current_user.id,
            Meal.eaten_at >= start_of_day,
            Meal.eaten_at <= end_of_day,
        )
        .order_by(Meal.eaten_at.asc())
        .all()
    )

    return meals


@router.get("/{meal_id}", response_model=MealOut)
def get_meal(
    meal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a single meal with its related foods for the current user."""
    meal = (
        db.query(Meal)
        .options(selectinload(Meal.items).selectinload(MealItem.food))
        .filter(Meal.id == meal_id, Meal.user_id == current_user.id)
        .first()
    )

    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    return meal


@router.get("/{meal_id}/nutrition", response_model=MealNutritionOut)
def get_meal_nutrition(
    meal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calculate total nutrition for one user-owned meal.

    Nutritional values are stored per 100g on Food, so each MealItem is scaled
    using grams / 100 before totals are aggregated.
    """
    meal = (
        db.query(Meal)
        .options(selectinload(Meal.items).selectinload(MealItem.food))
        .filter(Meal.id == meal_id, Meal.user_id == current_user.id)
        .first()
    )

    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    total_calories = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0

    for item in meal.items:
        food = item.food
        factor = item.grams / 100.0

        total_calories += food.calories_per_100g * factor
        total_protein += food.protein_per_100g * factor
        total_carbs += food.carbs_per_100g * factor
        total_fat += food.fat_per_100g * factor

    return MealNutritionOut(
        meal_id=meal.id,
        total_calories=round(total_calories, 2),
        total_protein=round(total_protein, 2),
        total_carbs=round(total_carbs, 2),
        total_fat=round(total_fat, 2),
    )


@router.delete("/{meal_id}")
def delete_meal(
    meal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a meal only if it belongs to the authenticated user."""
    meal = (
        db.query(Meal)
        .filter(Meal.id == meal_id, Meal.user_id == current_user.id)
        .first()
    )

    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    db.delete(meal)
    db.commit()

    return {"message": "Meal deleted"}


@router.patch("/items/{item_id}", response_model=MealItemOut)
def update_meal_item(
    item_id: int,
    update: MealItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a meal item only if the parent meal belongs to the current user."""
    item = (
        db.query(MealItem)
        .join(Meal, MealItem.meal_id == Meal.id)
        .filter(MealItem.id == item_id, Meal.user_id == current_user.id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Meal item not found")

    food = (
        db.query(Food)
        .filter(Food.id == update.food_id, Food.user_id == current_user.id)
        .first()
    )
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    item.food_id = update.food_id
    item.grams = update.grams

    db.commit()
    db.refresh(item)
    return item


@router.delete("/items/{item_id}")
def delete_meal_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a meal item only if it is linked to a user-owned meal."""
    item = (
        db.query(MealItem)
        .join(Meal, MealItem.meal_id == Meal.id)
        .filter(MealItem.id == item_id, Meal.user_id == current_user.id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Meal item not found")

    db.delete(item)
    db.commit()

    return {"message": "Meal item deleted"}