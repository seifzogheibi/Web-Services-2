from pydantic import BaseModel


class ExternalFoodOut(BaseModel):
    external_id: str
    name: str
    brand: str
    calories_per_100g: float | None = None
    protein_per_100g: float | None = None
    carbs_per_100g: float | None = None
    fat_per_100g: float | None = None
    source: str = "openfoodfacts"