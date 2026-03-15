from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.food import Food
from app.models.user import User
from app.schemas.food import FoodCreate, FoodOut, FoodUpdate

router = APIRouter(prefix="/foods", tags=["foods"])


@router.get("/", response_model=list[FoodOut])
def list_foods(
    search: str | None = Query(default=None, description="Search foods by name"),
    brand: str | None = Query(default=None, description="Filter by brand"),
    source: str | None = Query(default=None, description="Filter by data source"),
    min_protein: float | None = Query(default=None, description="Minimum protein per 100g"),
    max_calories: float | None = Query(default=None, description="Maximum calories per 100g"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Food).filter(Food.user_id == current_user.id)

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
def create_food(
    food: FoodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_food = Food(**food.model_dump(), user_id=current_user.id)
    db.add(db_food)
    db.commit()
    db.refresh(db_food)
    return db_food


@router.get("/{food_id}", response_model=FoodOut)
def get_food(
    food_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    food = (
        db.query(Food)
        .filter(Food.id == food_id, Food.user_id == current_user.id)
        .first()
    )

    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    return food


@router.patch("/{food_id}", response_model=FoodOut)
def update_food(
    food_id: int,
    update: FoodUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    food = (
        db.query(Food)
        .filter(Food.id == food_id, Food.user_id == current_user.id)
        .first()
    )

    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(food, key, value)

    db.commit()
    db.refresh(food)
    return food


@router.delete("/{food_id}")
def delete_food(
    food_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    food = (
        db.query(Food)
        .filter(Food.id == food_id, Food.user_id == current_user.id)
        .first()
    )

    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    db.delete(food)
    db.commit()

    return {"message": "Food deleted"}