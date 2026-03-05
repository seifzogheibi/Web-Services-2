from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.food import Food
from app.schemas.food import FoodCreate, FoodUpdate, FoodOut

router = APIRouter(prefix="/foods", tags=["foods"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[FoodOut])
def list_foods(db: Session = Depends(get_db)):
    return db.query(Food).all()


@router.post("/", response_model=FoodOut)
def create_food(food: FoodCreate, db: Session = Depends(get_db)):
    db_food = Food(**food.model_dump())
    db.add(db_food)
    db.commit()
    db.refresh(db_food)
    return db_food


@router.get("/{food_id}", response_model=FoodOut)
def get_food(food_id: int, db: Session = Depends(get_db)):
    food = db.query(Food).get(food_id)

    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    return food


@router.patch("/{food_id}", response_model=FoodOut)
def update_food(food_id: int, update: FoodUpdate, db: Session = Depends(get_db)):
    food = db.query(Food).get(food_id)

    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(food, key, value)

    db.commit()
    db.refresh(food)

    return food


@router.delete("/{food_id}")
def delete_food(food_id: int, db: Session = Depends(get_db)):
    food = db.query(Food).get(food_id)

    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    db.delete(food)
    db.commit()

    return {"message": "Food deleted"}