# Nutrition API (FastAPI)

REST API for foods, meals, and nutrition analytics.

## Run locally
```bash 
source venv/bin/activate
uvicorn app.main:app --reload

## Docs
Swagger UI: /docs
OpenAPI JSON: /openapi.json


**An initial Django prototype was explored but replaced with FastAPI to improve API-first design, asynchronous request handling, and automatic OpenAPI documentation generation.