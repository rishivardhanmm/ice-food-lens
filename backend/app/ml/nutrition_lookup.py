"""Food composition lookup table used by the internal model pipeline.

This is a small seed table for demo purposes. In production this would be
backed by a proper food composition database (e.g. USDA FoodData Central).
Values are per 100g/100ml.
"""
from typing import Optional, TypedDict


class NutritionRecord(TypedDict):
    category: str
    calories_kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fibre_g: float
    sugar_g: float
    sodium_mg: float


NUTRITION_TABLE: dict[str, NutritionRecord] = {
    "white_rice": {"category": "grain", "calories_kcal": 130, "protein_g": 2.7, "carbs_g": 28,
                    "fat_g": 0.3, "fibre_g": 0.4, "sugar_g": 0.1, "sodium_mg": 1},
    "grilled_chicken": {"category": "protein", "calories_kcal": 165, "protein_g": 31, "carbs_g": 0,
                          "fat_g": 3.6, "fibre_g": 0, "sugar_g": 0, "sodium_mg": 74},
    "broccoli": {"category": "vegetable", "calories_kcal": 34, "protein_g": 2.8, "carbs_g": 7,
                  "fat_g": 0.4, "fibre_g": 2.6, "sugar_g": 1.7, "sodium_mg": 33},
    "apple": {"category": "fruit", "calories_kcal": 52, "protein_g": 0.3, "carbs_g": 14,
               "fat_g": 0.2, "fibre_g": 2.4, "sugar_g": 10.4, "sodium_mg": 1},
}


def lookup(food_key: str) -> Optional[NutritionRecord]:
    return NUTRITION_TABLE.get(food_key)


def scale_to_quantity(record: NutritionRecord, grams: float) -> dict:
    factor = grams / 100.0
    return {k: (v * factor if isinstance(v, (int, float)) and k != "category" else v)
            for k, v in record.items()}
