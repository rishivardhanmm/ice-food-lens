from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Prediction, PredictionItem, TrainingExample

router = APIRouter()


@router.get("/api/evaluation/summary")
def evaluation_summary(db: Session = Depends(get_db)):
    total_predictions = db.query(func.count(Prediction.id)).scalar() or 0
    by_model = dict(
        db.query(Prediction.model_used, func.count(Prediction.id))
        .group_by(Prediction.model_used)
        .all()
    )
    avg_confidence = db.query(func.avg(PredictionItem.confidence)).scalar()
    by_category = dict(
        db.query(PredictionItem.category, func.avg(PredictionItem.confidence))
        .group_by(PredictionItem.category)
        .all()
    )
    pending_review = (
        db.query(func.count(TrainingExample.id))
        .filter(TrainingExample.status == "pending_review")
        .scalar()
        or 0
    )
    reviewed = (
        db.query(func.count(TrainingExample.id))
        .filter(TrainingExample.status == "reviewed")
        .scalar()
        or 0
    )

    return {
        "total_predictions": total_predictions,
        "predictions_by_model": by_model,
        "avg_confidence": round(avg_confidence, 3) if avg_confidence else None,
        "avg_confidence_by_category": {k: round(v, 3) for k, v in by_category.items() if k},
        "training_examples_pending_review": pending_review,
        "training_examples_reviewed": reviewed,
        # Real quantity/calorie/MAE numbers require corrected ground truth —
        # see app/ml/evaluate.py once enough reviewed examples exist.
        "note": "MAE/accuracy metrics populate once training_examples have user_corrections.",
    }
