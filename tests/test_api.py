import os
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.base import Base
from app.core.dependencies import get_db

TEST_DB_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DB_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module():
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test.db"):
        os.remove("test.db")


def register_user(email: str, password: str):
    return client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )


def login_user(email: str, password: str):
    return client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login():
    register_res = register_user("test1@example.com", "password123")
    assert register_res.status_code == 200

    login_res = login_user("test1@example.com", "password123")
    assert login_res.status_code == 200

    token = login_res.json()["access_token"]
    assert token is not None


def test_auth_me():
    register_user("test2@example.com", "password123")
    login_res = login_user("test2@example.com", "password123")
    token = login_res.json()["access_token"]

    me_res = client.get("/auth/me", headers=auth_headers(token))
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "test2@example.com"


def test_food_is_user_specific():
    register_user("usera@example.com", "password123")
    token_a = login_user("usera@example.com", "password123").json()["access_token"]

    register_user("userb@example.com", "password123")
    token_b = login_user("userb@example.com", "password123").json()["access_token"]

    create_food_res = client.post(
        "/foods/",
        headers=auth_headers(token_a) | {"Content-Type": "application/json"},
        json={
            "name": "Chicken Breast",
            "brand": "Test Brand",
            "calories_per_100g": 165,
            "protein_per_100g": 31,
            "carbs_per_100g": 0,
            "fat_per_100g": 3.6,
            "source": "manual",
        },
    )
    assert create_food_res.status_code == 201

    foods_a = client.get("/foods/", headers=auth_headers(token_a))
    foods_b = client.get("/foods/", headers=auth_headers(token_b))

    assert foods_a.status_code == 200
    assert foods_b.status_code == 200

    assert len(foods_a.json()) == 1
    assert len(foods_b.json()) == 0


def test_daily_analytics():
    register_user("analytics@example.com", "password123")
    token = login_user("analytics@example.com", "password123").json()["access_token"]

    food_res = client.post(
        "/foods/",
        headers=auth_headers(token) | {"Content-Type": "application/json"},
        json={
            "name": "Rice",
            "brand": "Test",
            "calories_per_100g": 130,
            "protein_per_100g": 2.5,
            "carbs_per_100g": 28,
            "fat_per_100g": 0.3,
            "source": "manual",
        },
    )
    assert food_res.status_code == 201
    food_id = food_res.json()["id"]

    meal_res = client.post(
        "/meals/",
        headers=auth_headers(token) | {"Content-Type": "application/json"},
        json={
            "name": "Lunch",
            "eaten_at": "2026-03-16T12:00:00",
        },
    )
    assert meal_res.status_code == 201
    meal_id = meal_res.json()["id"]

    item_res = client.post(
        f"/meals/{meal_id}/items",
        headers=auth_headers(token) | {"Content-Type": "application/json"},
        json={
            "food_id": food_id,
            "grams": 200,
        },
    )
    assert item_res.status_code == 201

    analytics_res = client.get(
        "/analytics/daily?date=2026-03-16",
        headers=auth_headers(token),
    )
    assert analytics_res.status_code == 200

    data = analytics_res.json()
    assert round(data["total_calories"], 1) == 260.0
    assert round(data["total_protein"], 1) == 5.0
    assert round(data["total_carbs"], 1) == 56.0
    assert round(data["total_fat"], 1) == 0.6


def test_goal_gap_suggestions():
    register_user("suggest@example.com", "password123")
    token = login_user("suggest@example.com", "password123").json()["access_token"]

    update_goals = client.put(
        "/auth/goals",
        headers=auth_headers(token) | {"Content-Type": "application/json"},
        json={
            "daily_calorie_goal": 2000,
            "daily_protein_goal": 150,
            "daily_carbs_goal": 250,
            "daily_fat_goal": 70,
        },
    )
    assert update_goals.status_code == 200

    food_res = client.post(
        "/foods/",
        headers=auth_headers(token) | {"Content-Type": "application/json"},
        json={
            "name": "Chicken Breast",
            "brand": "Test Brand",
            "calories_per_100g": 165,
            "protein_per_100g": 31,
            "carbs_per_100g": 0,
            "fat_per_100g": 3.6,
            "source": "manual",
        },
    )
    assert food_res.status_code == 201

    suggestions_res = client.get(
        "/analytics/suggestions?date=2026-03-16",
        headers=auth_headers(token),
    )
    assert suggestions_res.status_code == 200

    data = suggestions_res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "Chicken Breast"

def test_auth_me_requires_token():
    res = client.get("/auth/me")
    assert res.status_code in [401, 403]

def test_analytics_are_user_specific():
    register_user("a1@example.com", "password123")
    token_a = login_user("a1@example.com", "password123").json()["access_token"]

    register_user("b1@example.com", "password123")
    token_b = login_user("b1@example.com", "password123").json()["access_token"]

    food_res = client.post(
        "/foods/",
        headers=auth_headers(token_a) | {"Content-Type": "application/json"},
        json={
            "name": "Rice",
            "brand": "Test",
            "calories_per_100g": 130,
            "protein_per_100g": 2.5,
            "carbs_per_100g": 28,
            "fat_per_100g": 0.3,
            "source": "manual",
        },
    )
    food_id = food_res.json()["id"]

    meal_res = client.post(
        "/meals/",
        headers=auth_headers(token_a) | {"Content-Type": "application/json"},
        json={"name": "Lunch", "eaten_at": "2026-03-16T12:00:00"},
    )
    meal_id = meal_res.json()["id"]

    client.post(
        f"/meals/{meal_id}/items",
        headers=auth_headers(token_a) | {"Content-Type": "application/json"},
        json={"food_id": food_id, "grams": 200},
    )

    analytics_a = client.get(
        "/analytics/daily?date=2026-03-16",
        headers=auth_headers(token_a),
    )
    analytics_b = client.get(
        "/analytics/daily?date=2026-03-16",
        headers=auth_headers(token_b),
    )

    assert analytics_a.status_code == 200
    assert analytics_b.status_code == 200

    assert analytics_a.json()["total_calories"] > 0
    assert analytics_b.json()["total_calories"] == 0
