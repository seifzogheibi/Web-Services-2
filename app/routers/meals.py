from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from datetime import date as date_type, datetime, time

from app.db.session import SessionLocal
from app.models.meal import Meal
from app.models.meal_item import MealItem
from app.models.food import Food
from app.schemas.meal import MealCreate, MealUpdate, MealOut
from app.schemas.meal_item import MealItemCreate, MealItemOut
from app.schemas.nutrition import MealNutritionOut

router = APIRouter(prefix="/meals", tags=["meals"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=MealOut, status_code=status.HTTP_201_CREATED)
def create_meal(meal: MealCreate, db: Session = Depends(get_db)):
    db_meal = Meal(**meal.model_dump())
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal

@router.patch("/{meal_id}", response_model=MealOut)
def update_meal(meal_id: int, update: MealUpdate, db: Session = Depends(get_db)):
    meal = db.get(Meal, meal_id)

    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(meal, key, value)

    db.commit()
    db.refresh(meal)

    return meal

@router.post("/{meal_id}/items", response_model=MealItemOut, status_code=status.HTTP_201_CREATED)
def add_food_to_meal(meal_id: int, item: MealItemCreate, db: Session = Depends(get_db)):
    meal = db.get(Meal, meal_id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    food = db.get(Food, item.food_id)
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
def list_meals(db: Session = Depends(get_db)):
    return db.query(Meal).all()

@router.get("/by-date", response_model=list[MealOut])
def get_meals_by_date(date: date_type, db: Session = Depends(get_db)):
    start_of_day = datetime.combine(date, time.min)
    end_of_day = datetime.combine(date, time.max)

    meals = (
        db.query(Meal)
        .options(selectinload(Meal.items).selectinload(MealItem.food))
        .filter(Meal.eaten_at >= start_of_day, Meal.eaten_at <= end_of_day)
        .order_by(Meal.eaten_at.asc())
        .all()
    )

    return meals


@router.get("/{meal_id}", response_model=MealOut)
def get_meal(meal_id: int, db: Session = Depends(get_db)):
    meal = db.get(Meal, meal_id)

    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    return meal

@router.get("/{meal_id}/nutrition", response_model=MealNutritionOut)
def get_meal_nutrition(meal_id: int, db: Session = Depends(get_db)):
    meal = db.get(Meal, meal_id)

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
def delete_meal(meal_id: int, db: Session = Depends(get_db)):
    meal = db.get(Meal, meal_id)

    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    db.delete(meal)
    db.commit()

    return {"message": "Meal deleted"}

@router.patch("/items/{item_id}", response_model=MealItemOut)
def update_meal_item(item_id: int, update: MealItemCreate, db: Session = Depends(get_db)):
    item = db.get(MealItem, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Meal item not found")

    food = db.get(Food, update.food_id)
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    item.food_id = update.food_id
    item.grams = update.grams

    db.commit()
    db.refresh(item)
    return item


@router.delete("/items/{item_id}")
def delete_meal_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(MealItem, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Meal item not found")

    db.delete(item)
    db.commit()

    return {"message": "Meal item deleted"}