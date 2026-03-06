# Nutrition API (FastAPI)

REST API for foods, meals, and nutrition analytics.

## Run locally
```bash 
source venv/bin/activate
uvicorn app.main:app --reload
```

## Docs
Swagger UI: /docs
OpenAPI JSON: /openapi.json


Notes:
**An initial Django prototype was explored but replaced with FastAPI to improve API-first design, asynchronous request handling, and automatic OpenAPI documentation generation.

**During development, SQLite was used for simplicity and portability. Because SQLite has limitations around altering constraints in existing tables, duplicate prevention for imported foods was handled at the application layer by checking external_id before insertion.