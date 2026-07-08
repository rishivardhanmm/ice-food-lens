"""Evaluation utilities for internal model versions and OpenAI comparison.

Computes the metrics shown on the Evaluation Dashboard:
  - food identification accuracy
  - quantity estimation error
  - calorie / protein / carbs / fat MAE
  - confidence calibration
  - accuracy by category / cuisine
"""
from typing import List


def evaluate_holdout(test_examples: List) -> dict:
    """PLACEHOLDER: with no trained model yet, returns nominal/empty metrics
    so the dashboard and promotion logic have a well-formed shape to consume."""
    if not test_examples:
        return {
            "n_examples": 0,
            "food_identification_accuracy": None,
            "quantity_mae_g": None,
            "calorie_mae": None,
            "protein_mae": None,
            "carbs_mae": None,
            "fat_mae": None,
            "confidence_calibration_error": None,
        }
    # TODO: once predictions vs. corrected ground truth are joined, compute
    # real MAE/accuracy here.
    return {
        "n_examples": len(test_examples),
        "food_identification_accuracy": None,
        "quantity_mae_g": None,
        "calorie_mae": None,
        "protein_mae": None,
        "carbs_mae": None,
        "fat_mae": None,
        "confidence_calibration_error": None,
    }


def compare_models_by_category(db) -> List[dict]:
    """TODO: group predictions by PredictionItem.category and compare
    internal vs openai model_used against user_corrections."""
    return []
