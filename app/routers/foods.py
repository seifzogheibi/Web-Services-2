from fastapi import APIRouter, Depends, HTTPException, status, Query
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
def list_foods(
    db: Session = Depends(get_db),
    search: str | None = Query(default=None, description="Search foods by name"),
    brand: str | None = Query(default=None, description="Filter by brand"),
    source: str | None = Query(default=None, description="Filter by data source"),
    min_protein: float | None = Query(default=None, description="Minimum protein per 100g"),
    max_calories: float | None = Query(default=None, description="Maximum calories per 100g"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    query = db.query(Food)

    if search:
        query = query.filter(Food.name.ilike(f"%{search}%"))

    if brand:
        query = query.filter(Food.brand.ilike(f"%{brand}%"))

    if source:
        query = query.filter(Food.source == source)

    if min_protein is not None:
        query = query.filter(Food.protein_per_100g >= min_protein)

    if max_calories is not None:
        query = query.filter(Food.calories_per_100g <= max_calories)

    return query.offset(offset).limit(limit).all()


@router.post("/", response_model=FoodOut, status_code=status.HTTP_201_CREATED)
def create_food(food: FoodCreate, db: Session = Depends(get_db)):
    db_food = Food(**food.model_dump())
    db.add(db_food)
    db.commit()
    db.refresh(db_food)
    return db_food


@router.get("/{food_id}", response_model=FoodOut)
def get_food(food_id: int, db: Session = Depends(get_db)):
    food = db.get(Food, food_id)

    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    return food


@router.patch("/{food_id}", response_model=FoodOut)
def update_food(food_id: int, update: FoodUpdate, db: Session = Depends(get_db)):
    food = db.get(Food, food_id)

    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(food, key, value)

    db.commit()
    db.refresh(food)

    return food


@router.delete("/{food_id}")
def delete_food(food_id: int, db: Session = Depends(get_db)):
    food = db.get(Food, food_id)

    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    db.delete(food)
    db.commit()

    return {"message": "Food deleted"}