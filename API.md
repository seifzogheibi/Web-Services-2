# Nutrition Tracker API Documentation

This API follows REST architectural principles. Resources such as foods, meals,
and meal items are represented as endpoints that support standard HTTP methods
(GET, POST, PATCH, DELETE).

Responses are returned in JSON format and HTTP status codes are used to
indicate request success or failure.

The API is implemented using FastAPI with SQLAlchemy for database interaction.

## Overview

The Nutrition Tracker API is a RESTful web service that allows users to manage foods, log meals, analyse nutritional intake, and import nutritional information from external open food datasets.

The API is implemented using FastAPI and returns responses in JSON format.

The system supports:
- Food library management (CRUD operations)
- Meal logging and diary tracking
- Nutritional analytics
- Integration with external food datasets (OpenFoodFacts)

Interactive documentation is automatically generated using Swagger UI and is available at:

http://127.0.0.1:8000/docs


--------------------------------------------------

BASE URL

http://127.0.0.1:8000

All endpoints described below are relative to this base URL.


--------------------------------------------------

AUTHENTICATION

Authentication is not implemented for this coursework prototype.

All endpoints are publicly accessible.


--------------------------------------------------

HEALTH ENDPOINT

GET /health

Description:
Checks whether the API server is running.

Example Request:
GET /health

Example Response:

{
  "status": "ok"
}

Status Codes:
200 - Server running successfully


--------------------------------------------------

FOODS

Foods represent individual food items stored in the local food library.

Each food contains nutritional values per 100g.

Fields:
- name
- brand
- calories_per_100g
- protein_per_100g
- carbs_per_100g
- fat_per_100g
- source (manual or openfoodfacts)
- external_id (optional identifier for imported foods)


--------------------------------------------------

GET /foods/

Description:
Returns all foods stored in the database.

Example Request:
GET /foods/

Optional Query Parameters:
- search : search foods by name
- brand : filter by brand
- source : filter by data source
- min_protein : minimum protein value
- max_calories : maximum calories
- offset : number of items to skip (pagination)
- limit : maximum number of items returned (pagination)

Example Response:

[
  {
    "id": 1,
    "name": "Chicken Breast",
    "brand": "General",
    "calories_per_100g": 165,
    "protein_per_100g": 31,
    "carbs_per_100g": 0,
    "fat_per_100g": 3.6,
    "source": "manual",
    "external_id": null
  }
]

Status Codes:
200 - Success


--------------------------------------------------

POST /foods/

Description:
Creates a new food entry in the database.

Request Body:

{
  "name": "Chicken Breast",
  "brand": "General",
  "calories_per_100g": 165,
  "protein_per_100g": 31,
  "carbs_per_100g": 0,
  "fat_per_100g": 3.6,
  "source": "manual"
}

Response:
Returns the created food object.

Status Codes:
201 - Food created successfully
422 - Validation error


--------------------------------------------------

GET /foods/{food_id}

Description:
Returns a specific food.

Example Request:
GET /foods/1

Example Response:

{
  "id": 1,
  "name": "Chicken Breast",
  "brand": "General",
  "calories_per_100g": 165,
  "protein_per_100g": 31,
  "carbs_per_100g": 0,
  "fat_per_100g": 3.6,
  "source": "manual",
  "external_id": null
}

Status Codes:
200 - Success
404 - Food not found


--------------------------------------------------

PATCH /foods/{food_id}

Description:
Updates an existing food.

Example Request:
PATCH /foods/1

Request Body Example:

{
  "brand": "Tesco"
}

Response:
Returns the updated food object.


--------------------------------------------------

DELETE /foods/{food_id}

Description:
Deletes a food from the database.

Example Request:
DELETE /foods/1

Example Response:

{
  "message": "Food deleted"
}

Status Codes:
200 - Food deleted
404 - Food not found


--------------------------------------------------

MEALS

Meals represent eating events in the food diary.

Allowed meal types:
- Breakfast
- Lunch
- Dinner
- Snack

Meals contain one or more meal items representing foods consumed.


--------------------------------------------------

GET /meals/

Description:
Returns all meals stored in the system.

Example Request:
GET /meals/


--------------------------------------------------

POST /meals/

Description:
Creates a new meal.

Request Body:

{
  "name": "Lunch",
  "eaten_at": "2026-03-09T13:00:00"
}

Response:
Returns the created meal object.


--------------------------------------------------

GET /meals/{meal_id}

Description:
Returns a specific meal including all food items.

Example Request:
GET /meals/4


--------------------------------------------------

PATCH /meals/{meal_id}

Description:
Updates a meal.


--------------------------------------------------

DELETE /meals/{meal_id}

Description:
Deletes a meal and all associated meal items.


--------------------------------------------------

MEAL ITEMS

Meal items represent foods consumed in a meal.

Each item contains:
- food_id
- grams consumed


--------------------------------------------------

POST /meals/{meal_id}/items

Description:
Adds a food to a meal.

Example Request:
POST /meals/4/items

Request Body:

{
  "food_id": 4,
  "grams": 200
}

Response:
Returns the created meal item.


--------------------------------------------------

MEALS BY DATE

GET /meals/by-date

Description:
Returns all meals for a specific date.

Example Request:
GET /meals/by-date?date=2026-03-09

Example Response:

[
  {
    "id": 2,
    "name": "Lunch",
    "eaten_at": "2026-03-09T13:00:00",
    "items": [
      {
        "food_id": 4,
        "grams": 200
      }
    ]
  }
]


--------------------------------------------------

ANALYTICS

Analytics endpoints compute nutritional summaries.


--------------------------------------------------

GET /analytics/daily

Description:
Returns the total nutritional intake for a given date.

Example Request:
GET /analytics/daily?date=2026-03-09

Example Response:

{
  "total_calories": 650,
  "total_protein": 52,
  "total_carbs": 30,
  "total_fat": 20
}


--------------------------------------------------

GET /meals/{meal_id}/nutrition

Description:
Returns the nutritional breakdown of a specific meal.


--------------------------------------------------

EXTERNAL DATA INTEGRATION

The API integrates with the OpenFoodFacts dataset.

This allows users to search external food products and import them into the local food library.


--------------------------------------------------

GET /external/openfoodfacts/search

Description:
Searches for foods in the OpenFoodFacts API.

Example Request:
GET /external/openfoodfacts/search?query=pepsi

Example Response:

[
  {
    "external_id": "5449000000996",
    "name": "Pepsi Max",
    "brand": "Pepsi",
    "calories_per_100g": 0
  }
]


--------------------------------------------------

POST /external/openfoodfacts/import

Description:
Imports a product from OpenFoodFacts into the local food database.

Request Body:

{
  "barcode": "5449000000996"
}

Response:
Returns the created food object stored in the local database.


--------------------------------------------------

ERROR HANDLING

The API uses standard HTTP response codes.

200 - Successful request  
201 - Resource created  
404 - Resource not found  
422 - Validation error  
500 - Internal server error  


--------------------------------------------------

SWAGGER DOCUMENTATION

Interactive API documentation is automatically generated by FastAPI and is available at:

http://127.0.0.1:8000/docs

Swagger UI allows developers to:
- Explore endpoints
- Test API requests
- View request and response schemas
- Inspect returned data