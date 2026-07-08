from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import TrainingRun, ModelVersion
from app.ml import train as train_module

router = APIRouter()


@router.post("/api/train/start")
def start_training(db: Session = Depends(get_db)):
    try:
        run_id = train_module.run_training()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"training_run_id": run_id, "status": "completed"}


@router.get("/api/train/status/{training_run_id}")
def training_status(training_run_id: str, db: Session = Depends(get_db)):
    run = db.get(TrainingRun, training_run_id)
    if not run:
        raise HTTPException(status_code=404, detail="training run not found")
    return {
        "id": run.id,
        "status": run.status,
        "train_count": run.train_count,
        "validation_count": run.validation_count,
        "test_count": run.test_count,
        "metrics": run.metrics,
        "resulting_model_version_id": run.resulting_model_version_id,
        "error_message": run.error_message,
    }


@router.get("/api/models")
def list_models(db: Session = Depends(get_db)):
    versions = db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).all()
    return [
        {
            "id": v.id,
            "version_label": v.version_label,
            "is_active": v.is_active,
            "metrics": v.metrics,
            "created_at": v.created_at.isoformat(),
        }
        for v in versions
    ]


@router.post("/api/models/promote")
def promote_model(model_version_id: str, db: Session = Depends(get_db)):
    promoted = train_module.promote_if_better(model_version_id)
    return {"promoted": promoted}
