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

@router.get("/openfoodfacts/search", response_model=list[ExternalFoodOut])
def search_openfoodfacts(
    query: str = Query(..., min_length=2),
    current_user: User = Depends(get_current_user),
):
    normalized_query = query.strip().lower()

    if normalized_query in search_cache:
        return search_cache[normalized_query]

    url = "https://world.openfoodfacts.org/cgi/search.pl"

    params = {
        "search_terms": normalized_query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 5,
        "fields": "code,product_name,brands,nutriments",
    }

    try:
        with httpx.Client(timeout=18.0, follow_redirects=True) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.ReadTimeout:
        raise HTTPException(
            status_code=504,
            detail="External food search timed out. Please try again."
        )
    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="External food service is currently unavailable."
        )

    results = []

    for product in data.get("products", [])[:5]:
        nutriments = product.get("nutriments", {})
        code = product.get("code")

        if not code:
            continue

        results.append(
            ExternalFoodOut(
                external_id=str(code),
                name=product.get("product_name") or "Unknown product",
                brand=product.get("brands") or "",
                calories_per_100g=nutriments.get("energy-kcal_100g"),
                protein_per_100g=nutriments.get("proteins_100g"),
                carbs_per_100g=nutriments.get("carbohydrates_100g"),
                fat_per_100g=nutriments.get("fat_100g"),
                source="openfoodfacts",
            )
        )

    search_cache[normalized_query] = results
    return results


@router.post("/openfoodfacts/import", response_model=FoodOut, status_code=201)
def import_openfoodfacts_product(
    payload: ExternalFoodImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    barcode = payload.barcode.strip()

    if not barcode:
        raise HTTPException(status_code=400, detail="Barcode is required")

    existing_food = (
        db.query(Food)
        .filter(Food.external_id == barcode, Food.user_id == current_user.id)
        .first()
    )
    if existing_food:
        return existing_food

    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"

    try:
        with httpx.Client(timeout=18.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()
    except httpx.ReadTimeout:
        raise HTTPException(
            status_code=504,
            detail="External food import timed out. Please try again."
        )
    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="External food service is currently unavailable."
        )

    product = data.get("product")
    if not product:
        raise HTTPException(status_code=404, detail="Product not found in OpenFoodFacts")

    nutriments = product.get("nutriments", {})

    food = Food(
        name=product.get("product_name") or "Unknown product",
        brand=product.get("brands") or "",
        calories_per_100g=float(nutriments.get("energy-kcal_100g") or 0),
        protein_per_100g=float(nutriments.get("proteins_100g") or 0),
        carbs_per_100g=float(nutriments.get("carbohydrates_100g") or 0),
        fat_per_100g=float(nutriments.get("fat_100g") or 0),
        source="openfoodfacts",
        external_id=barcode,
        user_id=current_user.id,
    )

    db.add(food)
    db.commit()
    db.refresh(food)

    return food