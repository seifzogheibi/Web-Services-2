# Nutrition API (FastAPI)

REST API for foods, meals, and nutrition analytics.

The system separates reusable food definitions from daily consumption events. Foods act as a nutritional reference catalogue, meals represent eating occasions, and meal items record which foods were consumed in each meal and in what quantity.

## Technology Stack
- FastAPI
- SQLAlchemy
- SQLite
- Alembic
- React frontend
- OpenFoodFacts external dataset

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

## Project Overview

Main features:
- Food CRUD operations
- Meal logging by date
- Daily nutrition analytics
- Food diary frontend
- OpenFoodFacts search and import
- Local food library editing and deletion


Notes:
**An initial Django prototype was explored but replaced with FastAPI to improve API-first design, asynchronous request handling, and automatic OpenAPI documentation generation.

**During development, SQLite was used for simplicity and portability. Because SQLite has limitations around altering constraints in existing tables, duplicate prevention for imported foods was handled at the application layer by checking external_id before insertion.

**The frontend communicates with the REST API asynchronously using background HTTP requests. These requests are visible in browser developer tools or Swagger, rather than being exposed directly in the user interface.