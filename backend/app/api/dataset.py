import os
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Image, Prediction, PredictionItem, TrainingExample
from app.ml import dataset_export
from app.services import openai_service, storage

router = APIRouter()

# In-memory batch job registry (MVP). A real system would persist this.
BATCH_JOBS: dict[str, dict] = {}


class ImportDirectoryIn(BaseModel):
    directory_path: str
    extensions: list[str] = [".jpg", ".jpeg", ".png", ".webp"]


@router.post("/api/dataset/import-directory")
def import_directory(payload: ImportDirectoryIn):
    """Server-side directory scan — local/admin mode only."""
    if not os.path.isdir(payload.directory_path):
        raise HTTPException(status_code=400, detail="Directory not found.")

    files = [
        os.path.join(payload.directory_path, f)
        for f in os.listdir(payload.directory_path)
        if os.path.splitext(f)[1].lower() in payload.extensions
    ]

    job_id = str(uuid.uuid4())
    BATCH_JOBS[job_id] = {
        "status": "pending",
        "files": files,
        "total": len(files),
        "processed": 0,
        "failed": 0,
        "skipped": 0,
        "estimated_cost_usd": round(len(files) * 0.01, 2),  # rough per-image estimate
    }
    return {"job_id": job_id, "total_images": len(files), "estimated_cost_usd": BATCH_JOBS[job_id]["estimated_cost_usd"]}


class ProcessBatchIn(BaseModel):
    job_id: str
    action: str = "start"  # start | pause | resume


@router.post("/api/dataset/process-batch")
def process_batch(payload: ProcessBatchIn, db: Session = Depends(get_db)):
    job = BATCH_JOBS.get(payload.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")

    if payload.action == "pause":
        job["status"] = "paused"
        return {"job_id": payload.job_id, **job}

    if payload.action in ("start", "resume"):
        job["status"] = "running"
        remaining = job["files"][job["processed"]:]
        for filepath in remaining:
            if job["status"] != "running":
                break
            try:
                with open(filepath, "rb") as f:
                    file_bytes = f.read()
                saved = storage.save_upload(file_bytes, os.path.basename(filepath))

                db_image = Image(
                    filename=os.path.basename(filepath),
                    filepath=saved["filepath"],
                    width=saved["width"],
                    height=saved["height"],
                    source="batch",
                )
                db.add(db_image)
                db.commit()
                db.refresh(db_image)

                result = openai_service.analyze_image(saved["filepath"])
                items = result.get("items", [])

                prediction = Prediction(
                    image_id=db_image.id,
                    model_used="openai",
                    train_requested=True,
                    status="success",
                    accuracy_warnings=result.get("accuracy_warnings", []),
                    improvement_questions=result.get("improvement_questions", []),
                    raw_response={"items": items},
                )
                db.add(prediction)
                db.commit()
                db.refresh(prediction)

                for item in items:
                    macros = item.get("macros", {})
                    qty = item.get("estimated_quantity", {})
                    db.add(PredictionItem(
                        prediction_id=prediction.id,
                        name=item.get("name", "unknown"),
                        category=item.get("category"),
                        quantity_value=qty.get("value"),
                        quantity_unit=qty.get("unit"),
                        calories_kcal=item.get("calories_kcal"),
                        protein_g=macros.get("protein_g"),
                        carbs_g=macros.get("carbs_g"),
                        fat_g=macros.get("fat_g"),
                        fibre_g=macros.get("fibre_g"),
                        sugar_g=macros.get("sugar_g"),
                        micronutrients=item.get("micronutrients", {}),
                        confidence=item.get("confidence"),
                        reasoning_summary=item.get("reasoning_summary"),
                        assumptions=item.get("assumptions", []),
                    ))
                db.commit()

                db.add(TrainingExample(image_id=db_image.id, prediction_id=prediction.id, status="pending_review"))
                db.commit()

                job["processed"] += 1
            except Exception:
                job["failed"] += 1
                job["processed"] += 1

        if job["processed"] >= job["total"]:
            job["status"] = "completed"

    return {"job_id": payload.job_id, **job}


@router.get("/api/dataset/batch-status/{job_id}")
def batch_status(job_id: str):
    job = BATCH_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return {"job_id": job_id, **job}


class ExportIn(BaseModel):
    format: str = "jsonl"  # jsonl | csv


@router.post("/api/dataset/export")
def export_dataset(payload: ExportIn):
    path = dataset_export.export_dataset(payload.format)
    return {"status": "exported", "path": path}
