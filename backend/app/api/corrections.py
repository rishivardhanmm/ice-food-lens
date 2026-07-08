from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import PredictionItem, UserCorrection, TrainingExample
from app.schemas.food import CorrectionIn

router = APIRouter()


@router.post("/api/corrections")
def submit_correction(payload: CorrectionIn, db: Session = Depends(get_db)):
    item = db.get(PredictionItem, payload.prediction_item_id)
    if not item:
        raise HTTPException(status_code=404, detail="prediction_item not found")

    correction = UserCorrection(
        prediction_item_id=item.id,
        corrected_name=payload.corrected_name,
        corrected_quantity_value=payload.corrected_quantity_value,
        corrected_quantity_unit=payload.corrected_quantity_unit,
        corrected_calories_kcal=payload.corrected_calories_kcal,
        corrected_protein_g=payload.corrected_protein_g,
        corrected_carbs_g=payload.corrected_carbs_g,
        corrected_fat_g=payload.corrected_fat_g,
        notes=payload.notes,
        corrected_by=payload.corrected_by,
    )
    db.add(correction)
    db.commit()
    db.refresh(correction)

    # Link to any pending training_example for this item's prediction, mark reviewed.
    training_example = (
        db.query(TrainingExample)
        .filter(TrainingExample.prediction_id == item.prediction_id)
        .first()
    )
    if training_example:
        training_example.correction_id = correction.id
        training_example.status = "reviewed"
        db.commit()

    return {"status": "saved", "correction_id": correction.id}
