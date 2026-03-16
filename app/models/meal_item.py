"""
This module defines the `MealItem` model, which represents an association between a meal and a food item
in the database. Each `MealItem` instance specifies the quantity of a food item (in grams) included in a meal.

Classes:
    MealItem: A SQLAlchemy model representing a meal item, which links a meal to a food item.

Attributes:
    id (int): The primary key of the meal item.
    meal_id (int): Foreign key referencing the associated meal.
    food_id (int): Foreign key referencing the associated food item.
    grams (float): The quantity of the food item in grams.
    created_at (datetime): The timestamp when the meal item was created.

Relationships:
    meal: A relationship to the `Meal` model, representing the meal this item belongs to.
    food: A relationship to the `Food` model, representing the food item included in the meal.
"""

from sqlalchemy import ForeignKey, DateTime, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base


class MealItem(Base):
    __tablename__ = "meal_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    meal_id: Mapped[int] = mapped_column(ForeignKey("meals.id", ondelete="CASCADE"), nullable=False)
    food_id: Mapped[int] = mapped_column(ForeignKey("foods.id", ondelete="CASCADE"), nullable=False)

    grams: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    meal = relationship("Meal", back_populates="items")
    food = relationship("Food", back_populates="meal_items")