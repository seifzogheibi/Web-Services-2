from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    daily_calorie_goal = Column(Float, nullable=True)
    daily_protein_goal = Column(Float, nullable=True)
    daily_carbs_goal = Column(Float, nullable=True)
    daily_fat_goal = Column(Float, nullable=True)

    foods = relationship("Food", back_populates="user", cascade="all, delete-orphan")
    meals = relationship("Meal", back_populates="user", cascade="all, delete-orphan")