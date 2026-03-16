# Nutrition API (FastAPI + React)

Backend available at: https://nutrition-api-seif.onrender.com/docs
Frontend available at: https://nutrition-api-seif-frontend.onrender.com

A full-stack nutrition tracking application with secure user accounts, personal nutrition goals, private food libraries, meal logging, daily analytics, and external food search/import.

The system separates reusable food definitions from daily consumption events. Foods act as a nutritional reference catalogue, meals represent eating occasions, and meal items record which foods were consumed in each meal and in what quantity.

## Technology Stack
- FastAPI
- SQLAlchemy
- SQLite
- Alembic
- React
- USDA FoodData Central API
- JWT authentication
- Pytest for backend testing

## Main Features
- User registration and login
- JWT-based authentication
- Personal daily calorie and macronutrient goals
- Private user-specific food libraries
- Custom food creation, editing, and deletion
- Meal logging by date (Breakfast, Lunch, Dinner, Snack)
- Daily nutrition analytics
- Smart Goal Gap Suggestions
- USDA food search and import
- Automated backend integration tests

## Setup Instructions (Linux/Mac)
1. Clone the repository:
```bash
git clone https://github.com/seifzogheibi/Web-Services-2.git
```
### Run backend API (Swagger UI available at http://localhost:8000/docs)
```bash 
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
### Run frontend demo (available at http://localhost:5173)
```bash
cd frontend
npm install
npm run dev
```

## Documentation
Swagger UI: http://localhost:8000/docs
OpenAPI JSON: http://localhost:8000/openapi.json
API Documentation (PDF): docs/API.pdf

## Testing
Backend automated tests were implemented using pytest and FastAPI’s TestClient.

```bash
pytest -v
```