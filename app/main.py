from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import foods, meals, analytics, external, authentication
from dotenv import load_dotenv

load_dotenv()

"""Main FastAPI application entry point.

This file creates the API instance, registers all route groups, exposes a
basic health-check endpoint, and enables CORS so the React frontend can
communicate with the backend in both local and deployed environments.
"""

app = FastAPI(
    title="Nutrition API",
    version="1.0.0",
    description="REST API for foods, meals, and nutrition analytics.",
)


@app.get("/health")
def health_check():
    return {"status": "okay"}


app.include_router(foods.router)
app.include_router(meals.router)
app.include_router(analytics.router)
app.include_router(external.router)
app.include_router(authentication.router)

"""CORS is enabled for the local Vite frontend and the deployed Render
frontend so authenticated browser requests can be made safely."""
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://nutrition-api-seif-frontend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)