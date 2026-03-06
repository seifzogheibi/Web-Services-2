from fastapi import FastAPI
from app.routers import foods, meals, analytics

app = FastAPI(
    title="Nutrition API",
    version="1.0.0",
    description="REST API for foods, meals, and nutrition analytics.",
)

@app.get("/test")
def test():
    return {"status": "okay"}

app.include_router(foods.router)
app.include_router(meals.router)
app.include_router(analytics.router)