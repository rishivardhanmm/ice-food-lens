"""Exports training_examples (+ joined prediction/correction data) as JSONL and CSV."""
import csv
import json
import os

from app.db.session import SessionLocal
from app.db.models import TrainingExample, Prediction, PredictionItem, UserCorrection, Image
from app.core.config import settings


def _build_record(db, example: TrainingExample) -> dict:
    image = db.get(Image, example.image_id)
    prediction = db.get(Prediction, example.prediction_id)
    items = db.query(PredictionItem).filter(PredictionItem.prediction_id == prediction.id).all()
    correction = db.get(UserCorrection, example.correction_id) if example.correction_id else None

    return {
        "example_id": example.id,
        "status": example.status,
        "split": example.split,
        "image_filename": image.filename if image else None,
        "model_used": prediction.model_used if prediction else None,
        "items": [
            {
                "name": it.name,
                "category": it.category,
                "quantity_value": it.quantity_value,
                "quantity_unit": it.quantity_unit,
                "calories_kcal": it.calories_kcal,
                "protein_g": it.protein_g,
                "carbs_g": it.carbs_g,
                "fat_g": it.fat_g,
                "confidence": it.confidence,
            }
            for it in items
        ],
        "correction": (
            {
                "corrected_name": correction.corrected_name,
                "corrected_quantity_value": correction.corrected_quantity_value,
                "corrected_calories_kcal": correction.corrected_calories_kcal,
                "corrected_protein_g": correction.corrected_protein_g,
                "corrected_carbs_g": correction.corrected_carbs_g,
                "corrected_fat_g": correction.corrected_fat_g,
                "notes": correction.notes,
            }
            if correction
            else None
        ),
    }


def export_dataset(fmt: str = "jsonl") -> str:
    os.makedirs(settings.export_dir, exist_ok=True)
    db = SessionLocal()
    try:
        examples = db.query(TrainingExample).all()
        records = [_build_record(db, ex) for ex in examples]

        if fmt == "jsonl":
            out_path = os.path.join(settings.export_dir, "dataset.jsonl")
            with open(out_path, "w", encoding="utf-8") as f:
                for r in records:
                    f.write(json.dumps(r) + "\n")
            return out_path

        if fmt == "csv":
            out_path = os.path.join(settings.export_dir, "dataset.csv")
            with open(out_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "example_id", "status", "split", "image_filename", "model_used",
                    "item_name", "category", "quantity_value", "calories_kcal",
                    "protein_g", "carbs_g", "fat_g", "confidence",
                    "corrected_name", "corrected_calories_kcal",
                ])
                for r in records:
                    correction = r["correction"] or {}
                    if not r["items"]:
                        writer.writerow([r["example_id"], r["status"], r["split"], r["image_filename"],
                                          r["model_used"], "", "", "", "", "", "", "", "",
                                          correction.get("corrected_name", ""),
                                          correction.get("corrected_calories_kcal", "")])
                    for item in r["items"]:
                        writer.writerow([
                            r["example_id"], r["status"], r["split"], r["image_filename"], r["model_used"],
                            item["name"], item["category"], item["quantity_value"], item["calories_kcal"],
                            item["protein_g"], item["carbs_g"], item["fat_g"], item["confidence"],
                            correction.get("corrected_name", ""),
                            correction.get("corrected_calories_kcal", ""),
                        ])
            return out_path

        raise ValueError(f"Unsupported export format: {fmt}")
    finally:
        db.close()
