import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Image, Prediction, PredictionItem, TrainingExample
from app.ml import internal_model
from app.services import openai_service, storage

router = APIRouter()

DISCLAIMER = (
    "This is an AI estimate and should not be used as medical advice. "
    "For clinical nutrition, diabetes management, eating disorder care, or "
    "medical conditions, consult a qualified professional."
)


def _totals_from_items(items: list[dict]) -> dict:
    totals = {"calories_kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "fibre_g": 0, "sugar_g": 0}
    for item in items:
        macros = item.get("macros", {})
        totals["calories_kcal"] += item.get("calories_kcal", 0) or 0
        totals["protein_g"] += macros.get("protein_g", 0) or 0
        totals["carbs_g"] += macros.get("carbs_g", 0) or 0
        totals["fat_g"] += macros.get("fat_g", 0) or 0
        totals["fibre_g"] += macros.get("fibre_g", 0) or 0
        totals["sugar_g"] += macros.get("sugar_g", 0) or 0
    return {k: round(v, 2) for k, v in totals.items()}


@router.post("/api/analyze-food")
async def analyze_food(
    image: UploadFile = File(...),
    train: bool = Form(False),
    source: str | None = Form(None),
    user_id: str | None = Form(None),
    notes: str | None = Form(None),
    use_internal_model: bool = Form(False),
    fallback_to_openai: bool = Form(True),
    db: Session = Depends(get_db),
):
    request_id = str(uuid.uuid4())

    file_bytes = await image.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty image upload.")

    saved = storage.save_upload(file_bytes, image.filename or "upload.jpg")

    db_image = Image(
        filename=image.filename or saved["stored_name"],
        filepath=saved["filepath"],
        width=saved["width"],
        height=saved["height"],
        content_type=image.content_type,
        source=source or "api",
        uploaded_by=user_id,
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    model_used = "openai"
    accuracy_warnings: list[str] = []
    improvement_questions: list[str] = []
    items: list[dict] = []

    if use_internal_model:
        internal_result = internal_model.predict(saved["filepath"])
        if internal_model.is_low_confidence(internal_result) and fallback_to_openai:
            try:
                openai_result = openai_service.analyze_image(saved["filepath"], notes or "")
                items = openai_result.get("items", [])
                accuracy_warnings = openai_result.get("accuracy_warnings", [])
                improvement_questions = openai_result.get("improvement_questions", [])
                model_used = "internal_with_openai_fallback"
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"OpenAI analysis failed: {e}")
        else:
            items = internal_result["items"]
            model_used = "internal"
            accuracy_warnings.append("Internal model is not yet trained; treat results as a placeholder.")
    else:
        try:
            openai_result = openai_service.analyze_image(saved["filepath"], notes or "")
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"OpenAI analysis failed: {e}")
        items = openai_result.get("items", [])
        accuracy_warnings = openai_result.get("accuracy_warnings", [])
        improvement_questions = openai_result.get("improvement_questions", [])
        model_used = "openai"

    accuracy_warnings.append(DISCLAIMER)
    totals = _totals_from_items(items)

    prediction = Prediction(
        image_id=db_image.id,
        request_id=request_id,
        model_used=model_used,
        train_requested=train,
        status="success",
        totals=totals,
        accuracy_warnings=accuracy_warnings,
        improvement_questions=improvement_questions,
        raw_response={"items": items},
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    item_rows = []
    for item in items:
        macros = item.get("macros", {})
        qty = item.get("estimated_quantity", {})
        row = PredictionItem(
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
        )
        db.add(row)
        item_rows.append(row)
    db.commit()

    if train:
        training_example = TrainingExample(
            image_id=db_image.id,
            prediction_id=prediction.id,
            status="pending_review",
        )
        db.add(training_example)
        db.commit()

    return {
        "request_id": request_id,
        "model_used": model_used,
        "train": train,
        "status": "success",
        "image_metadata": {
            "filename": db_image.filename,
            "width": db_image.width or 0,
            "height": db_image.height or 0,
        },
        "items": items,
        "totals": totals,
        "accuracy_warnings": accuracy_warnings,
        "improvement_questions": improvement_questions,
        "prediction_id": prediction.id,
        "prediction_item_ids": [row.id for row in item_rows],
    }
