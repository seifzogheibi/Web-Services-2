import httpx
from fastapi import APIRouter, Query

from app.schemas.external import ExternalFoodOut

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