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
    """Extract the main nutrition fields needed by the application.

    USDA responses can vary slightly depending on the type of record returned,
    so this helper checks multiple field names and normalises the output into
    the app's internal per-100g nutrition structure.
    """
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

        # Match the USDA energy field and store it as calories per 100g.
        if "energy" in name and (unit == "kcal" or "atwater" in name or name == "energy"):
            nutrients["calories_per_100g"] = float(value)

        # Match protein values.
        elif "protein" in name:
            nutrients["protein_per_100g"] = float(value)

        # Match carbohydrate values.
        elif "carbohydrate" in name:
            nutrients["carbs_per_100g"] = float(value)

        # Match total fat values.
        elif "total lipid (fat)" in name or name == "fat":
            nutrients["fat_per_100g"] = float(value)

    return nutrients


@router.get("/usda/search", response_model=list[ExternalFoodOut])
def search_usda_foods(
    query: str = Query(..., min_length=2),
    current_user: User = Depends(get_current_user),
):
    """Search USDA FoodData Central and return normalized external food results.

    Search results are cached by normalized query to avoid repeated external
    calls for the same term during a session. The current user dependency
    protects this endpoint so only authenticated users can perform imports
    into their private library later.
    """
    normalized_query = query.strip().lower()

    if normalized_query in search_cache:
        return search_cache[normalized_query]

    search_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {"api_key": settings.usda_api_key}
    payload = {
        "query": normalized_query,
        "pageSize": 10,
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            search_response = client.post(search_url, params=params, json=payload)
            search_response.raise_for_status()
            search_data = search_response.json()

            results = []

            """Each search hit is followed by a detail lookup so nutrition values
            can be extracted consistently before being shown in the frontend."""
            for item in search_data.get("foods", [])[:5]:
                external_id = item.get("fdcId")
                if not external_id:
                    continue

                raw_name = (item.get("description") or "").strip()
                brand = (item.get("brandOwner") or item.get("brandName") or "").strip()

                if not raw_name:
                    continue

                detail_url = f"https://api.nal.usda.gov/fdc/v1/food/{external_id}"
                detail_response = client.get(detail_url, params=params)
                detail_response.raise_for_status()
                detail_data = detail_response.json()

                nutrients = extract_usda_nutrients(detail_data.get("foodNutrients", []))

                results.append(
                    ExternalFoodOut(
                        external_id=str(external_id),
                        name=raw_name,
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

    search_cache[normalized_query] = results
    return results


@router.post("/usda/import", response_model=FoodOut, status_code=201)
def import_usda_food(
    payload: ExternalFoodImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Import a USDA food into the authenticated user's private library.

    Imported foods are stored locally so they can be reused in future meal
    logging and analytics without requiring repeated external API calls.
    """
    external_id = payload.external_id.strip()

    if not external_id:
        raise HTTPException(status_code=400, detail="External ID is required")

    """Avoid importing duplicate USDA records into the same user's library."""
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