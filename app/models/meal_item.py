from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

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