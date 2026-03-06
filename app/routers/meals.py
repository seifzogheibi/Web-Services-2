from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.meal import Meal
from app.models.meal_item import MealItem
from app.models.food import Food
from app.schemas.meal import MealCreate, MealUpdate, MealOut
from app.schemas.meal_item import MealItemCreate, MealItemOut

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


@router.get("/{meal_id}", response_model=MealOut)
def get_meal(meal_id: int, db: Session = Depends(get_db)):
    meal = db.get(Meal, meal_id)

    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    return meal


@router.delete("/{meal_id}")
def delete_meal(meal_id: int, db: Session = Depends(get_db)):
    meal = db.get(Meal, meal_id)

    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    db.delete(meal)
    db.commit()

    return {"message": "Meal deleted"}