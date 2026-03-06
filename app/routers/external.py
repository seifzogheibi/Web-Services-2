import httpx
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.food import Food
from app.schemas.external import ExternalFoodOut, ExternalFoodImportRequest
from app.schemas.food import FoodOut

router = APIRouter(prefix="/external", tags=["external"])


@router.get("/openfoodfacts/search", response_model=list[ExternalFoodOut])
def search_openfoodfacts(query: str = Query(..., min_length=2)):
    url = "https://world.openfoodfacts.org/cgi/search.pl"

    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 10,
    }

    response = httpx.get(url, params=params, timeout=10.0)
    response.raise_for_status()
    data = response.json()

    results = []

    for product in data.get("products", []):
        nutriments = product.get("nutriments", {})

        results.append(
            ExternalFoodOut(
                external_id=str(product.get("code", "")),
                name=product.get("product_name", "") or "Unknown product",
                brand=product.get("brands", "") or "",
                calories_per_100g=nutriments.get("energy-kcal_100g"),
                protein_per_100g=nutriments.get("proteins_100g"),
                carbs_per_100g=nutriments.get("carbohydrates_100g"),
                fat_per_100g=nutriments.get("fat_100g"),
                source="openfoodfacts",
            )
        )

    return results

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/openfoodfacts/import", response_model=FoodOut, status_code=201)
def import_openfoodfacts_product(payload: ExternalFoodImportRequest, db: Session = Depends(get_db)):
    barcode = payload.barcode.strip()

    if not barcode:
        raise HTTPException(status_code=400, detail="Barcode is required")

    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"

    response = httpx.get(url, timeout=10.0)
    response.raise_for_status()
    data = response.json()

    product = data.get("product")
    if not product:
        raise HTTPException(status_code=404, detail="Product not found in OpenFoodFacts")

    nutriments = product.get("nutriments", {})

    food = Food(
        name=product.get("product_name", "") or "Unknown product",
        brand=product.get("brands", "") or "",
        calories_per_100g=float(nutriments.get("energy-kcal_100g") or 0),
        protein_per_100g=float(nutriments.get("proteins_100g") or 0),
        carbs_per_100g=float(nutriments.get("carbohydrates_100g") or 0),
        fat_per_100g=float(nutriments.get("fat_100g") or 0),
        source="openfoodfacts",
    )

    db.add(food)
    db.commit()
    db.refresh(food)

    return food
