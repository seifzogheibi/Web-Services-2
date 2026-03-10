# Nutrition API (FastAPI)

REST API for foods, meals, and nutrition analytics.

The system separates reusable food definitions from daily consumption events. Foods act as a nutritional reference catalogue, meals represent eating occasions, and meal items record which foods were consumed in each meal and in what quantity.

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

**The frontend communicates with the REST API asynchronously using background HTTP requests. These requests are visible in browser developer tools or Swagger, rather than being exposed directly in the user interface.