import httpx
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.food import Food
from app.models.user import User
from app.schemas.external import ExternalFoodOut, ExternalFoodImportRequest
from app.schemas.food import FoodOut

router = APIRouter(prefix="/external", tags=["external"])
search_cache = {}

from app.core.config import settings

if not settings.usda_api_key:
    raise RuntimeError("USDA_API_KEY is not set")


def extract_usda_nutrients(food_nutrients: list[dict]) -> dict:
    nutrients = {
        "calories_per_100g": None,
        "protein_per_100g": None,
        "carbs_per_100g": None,
        "fat_per_100g": None,
    }

    for nutrient in food_nutrients or []:
        nutrient_info = nutrient.get("nutrient", {})

        name = (
            nutrient_info.get("name")
            or nutrient.get("nutrientName")
            or ""
        ).lower()

        unit = (
            nutrient_info.get("unitName")
            or nutrient.get("unitName")
            or ""
        ).lower()

        value = nutrient.get("amount")
        if value is None:
            value = nutrient.get("value")

        if value is None:
            continue

        # Calories
        if "energy" in name and (unit == "kcal" or "atwater" in name or name == "energy"):
            nutrients["calories_per_100g"] = float(value)

        # Protein
        elif "protein" in name:
            nutrients["protein_per_100g"] = float(value)

        # Carbs
        elif "carbohydrate" in name:
            nutrients["carbs_per_100g"] = float(value)

        # Fat
        elif "total lipid (fat)" in name or name == "fat":
            nutrients["fat_per_100g"] = float(value)

    return nutrients

def score_usda_result(item: dict, query: str) -> int:
    description = (item.get("description") or "").lower()
    brand = (item.get("brandOwner") or item.get("brandName") or "").lower()
    query_words = query.split()

    score = 0

    if description == query:
        score += 120

    if query in description:
        score += 60

    if all(word in description for word in query_words):
        score += 35

    if description.startswith(query):
        score += 20

    if brand:
        score += 10

    # Penalise poor match types for general consumer searches
    penalties = [
        "powder",
        "mix",
        "dry",
        "concentrate",
        "flour",
        "meal replacement powder",
    ]

    for term in penalties:
        if term in description and term not in query:
            score -= 25

    return score


@router.get("/usda/search", response_model=list[ExternalFoodOut])
def search_usda_foods(
    query: str = Query(..., min_length=2),
    max_calories: float | None = Query(None),
    min_protein: float | None = Query(None),
    current_user: User = Depends(get_current_user),
):
    normalized_query = query.strip().lower()

    cache_key = f"{normalized_query}|max_calories={max_calories}|min_protein={min_protein}"

    if cache_key in search_cache:
        return search_cache[cache_key]

    search_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {"api_key": settings.usda_api_key}
    payload = {
        "query": normalized_query,
        "pageSize": 5,
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            search_response = client.post(search_url, params=params, json=payload)
            search_response.raise_for_status()
            search_data = search_response.json()

            results = []

            foods = search_data.get("foods", [])
            foods = sorted(
                foods,
                key=lambda item: score_usda_result(item, normalized_query),
                reverse=True,
            )
            for item in foods[:5]:
                external_id = item.get("fdcId")
                if not external_id:
                    continue

                raw_name = (item.get("description") or "").strip()
                brand = (item.get("brandOwner") or item.get("brandName") or "").strip()

                if not raw_name:
                    continue

                bad_terms = ["nfs", "ready-to-drink", "light,", "nutritional drink or shake"]
                if any(term in raw_name.lower() for term in bad_terms) and not brand:
                    continue

                display_name = raw_name.split(",")[0].strip()

                if not display_name:
                    continue

                detail_url = f"https://api.nal.usda.gov/fdc/v1/food/{external_id}"
                detail_response = client.get(detail_url, params=params)
                detail_response.raise_for_status()
                detail_data = detail_response.json()

                nutrients = extract_usda_nutrients(detail_data.get("foodNutrients", []))

                calories = nutrients["calories_per_100g"]
                if (
                    calories is not None
                    and any(word in normalized_query for word in ["shake", "drink", "juice", "cola", "soda"])
                    and calories > 400
                ):
                    continue

                results.append(
                    ExternalFoodOut(
                        external_id=str(external_id),
                        name=display_name,
                        brand=brand,
                        calories_per_100g=nutrients["calories_per_100g"],
                        protein_per_100g=nutrients["protein_per_100g"],
                        carbs_per_100g=nutrients["carbs_per_100g"],
                        fat_per_100g=nutrients["fat_per_100g"],
                        source="usda",
                    )
                )

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"USDA API error: {e.response.status_code} - {e.response.text}",
        )
    except httpx.ReadTimeout:
        raise HTTPException(
            status_code=504,
            detail="USDA food search timed out. Please try again.",
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=502,
            detail=f"USDA connection error: {str(e)}",
        )
    
    if max_calories is not None:
        results = [
            food for food in results
            if food.calories_per_100g is not None and food.calories_per_100g <= max_calories
        ]

    if min_protein is not None:
        results = [
            food for food in results
            if food.protein_per_100g is not None and food.protein_per_100g >= min_protein
        ]

    search_cache[cache_key] = results
    return results


@router.post("/usda/import", response_model=FoodOut, status_code=201)
def import_usda_food(
    payload: ExternalFoodImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    external_id = payload.external_id.strip()

    if not external_id:
        raise HTTPException(status_code=400, detail="External ID is required")

    existing_food = (
        db.query(Food)
        .filter(Food.external_id == external_id, Food.user_id == current_user.id)
        .first()
    )
    if existing_food:
        return existing_food

    url = f"https://api.nal.usda.gov/fdc/v1/food/{external_id}"
    params = {"api_key": settings.usda_api_key}

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"USDA API error: {e.response.status_code} - {e.response.text}",
        )
    except httpx.ReadTimeout:
        raise HTTPException(
            status_code=504,
            detail="USDA food import timed out. Please try again.",
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=502,
            detail=f"USDA connection error: {str(e)}",
        )

    nutrients = extract_usda_nutrients(data.get("foodNutrients", []))

    raw_name = (data.get("description") or "").strip()
    display_name = raw_name.split(",")[0].strip()
    brand = (data.get("brandOwner") or data.get("brandName") or "").strip()

    if not display_name:
        raise HTTPException(status_code=404, detail="Product name not available")

    food = Food(
        name=display_name,
        brand=brand,
        calories_per_100g=float(nutrients["calories_per_100g"] or 0),
        protein_per_100g=float(nutrients["protein_per_100g"] or 0),
        carbs_per_100g=float(nutrients["carbs_per_100g"] or 0),
        fat_per_100g=float(nutrients["fat_per_100g"] or 0),
        source="usda",
        external_id=external_id,
        user_id=current_user.id,
    )

    db.add(food)
    db.commit()
    db.refresh(food)
    return food