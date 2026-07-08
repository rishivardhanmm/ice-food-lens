"""Internal food-recognition model.

PLACEHOLDER: there is no trained internal model yet. `predict()` returns a
low-confidence stub result so the API's `use_internal_model` /
`fallback_to_openai` branching can be exercised end-to-end before a real
model exists. Once `app/ml/train.py` produces a promoted ModelVersion, this
module should load those weights and run the real pipeline:

    preprocess -> detect/segment -> classify -> portion estimate
    -> nutrition_lookup -> calibrate with user_corrections -> confidence score
"""
from app.ml import nutrition_lookup

INTERNAL_MODEL_LOADED = False
LOW_CONFIDENCE_THRESHOLD = 0.45


def predict(filepath: str) -> dict:
    """Returns the same item shape the API layer expects, with low confidence
    so callers know to fall back to OpenAI."""
    return {
        "items": [
            {
                "name": "unknown_food",
                "category": "unknown",
                "estimated_quantity": {"value": 100, "unit": "g"},
                "calories_kcal": 0,
                "macros": {"protein_g": 0, "carbs_g": 0, "fat_g": 0, "fibre_g": 0, "sugar_g": 0},
                "micronutrients": {},
                "confidence": 0.1,
                "reasoning_summary": "Internal model is a placeholder and has not been trained.",
                "assumptions": ["Internal model not yet trained on real data."],
            }
        ],
        "overall_confidence": 0.1,
    }


def is_low_confidence(result: dict) -> bool:
    return result.get("overall_confidence", 0) < LOW_CONFIDENCE_THRESHOLD
