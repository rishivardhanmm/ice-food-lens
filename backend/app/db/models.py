import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text
)
from sqlalchemy.orm import relationship

from app.db.session import Base


def gen_uuid():
    return str(uuid.uuid4())


class Image(Base):
    __tablename__ = "images"

    id = Column(String, primary_key=True, default=gen_uuid)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    content_type = Column(String, nullable=True)
    source = Column(String, nullable=True)  # ui | api | batch
    uploaded_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    predictions = relationship("Prediction", back_populates="image")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, default=gen_uuid)
    image_id = Column(String, ForeignKey("images.id"), nullable=False)
    request_id = Column(String, default=gen_uuid)
    model_used = Column(String, nullable=False)  # openai | internal | internal_with_openai_fallback
    train_requested = Column(Boolean, default=False)
    status = Column(String, default="success")
    totals = Column(JSON, nullable=True)
    accuracy_warnings = Column(JSON, nullable=True)
    improvement_questions = Column(JSON, nullable=True)
    raw_response = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    image = relationship("Image", back_populates="predictions")
    items = relationship("PredictionItem", back_populates="prediction")


class PredictionItem(Base):
    __tablename__ = "prediction_items"

    id = Column(String, primary_key=True, default=gen_uuid)
    prediction_id = Column(String, ForeignKey("predictions.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    quantity_value = Column(Float, nullable=True)
    quantity_unit = Column(String, nullable=True)
    calories_kcal = Column(Float, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    fibre_g = Column(Float, nullable=True)
    sugar_g = Column(Float, nullable=True)
    micronutrients = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=True)
    reasoning_summary = Column(Text, nullable=True)
    assumptions = Column(JSON, nullable=True)

    prediction = relationship("Prediction", back_populates="items")


class UserCorrection(Base):
    __tablename__ = "user_corrections"

    id = Column(String, primary_key=True, default=gen_uuid)
    prediction_item_id = Column(String, ForeignKey("prediction_items.id"), nullable=False)
    corrected_name = Column(String, nullable=True)
    corrected_quantity_value = Column(Float, nullable=True)
    corrected_quantity_unit = Column(String, nullable=True)
    corrected_calories_kcal = Column(Float, nullable=True)
    corrected_protein_g = Column(Float, nullable=True)
    corrected_carbs_g = Column(Float, nullable=True)
    corrected_fat_g = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    corrected_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TrainingExample(Base):
    __tablename__ = "training_examples"

    id = Column(String, primary_key=True, default=gen_uuid)
    image_id = Column(String, ForeignKey("images.id"), nullable=False)
    prediction_id = Column(String, ForeignKey("predictions.id"), nullable=False)
    correction_id = Column(String, ForeignKey("user_corrections.id"), nullable=True)
    status = Column(String, default="pending_review")  # pending_review | reviewed | rejected | used
    split = Column(String, nullable=True)  # train | validation | test
    created_at = Column(DateTime, default=datetime.utcnow)


class TrainingRun(Base):
    __tablename__ = "training_runs"

    id = Column(String, primary_key=True, default=gen_uuid)
    status = Column(String, default="queued")  # queued | running | completed | failed
    train_count = Column(Integer, default=0)
    validation_count = Column(Integer, default=0)
    test_count = Column(Integer, default=0)
    metrics = Column(JSON, nullable=True)
    resulting_model_version_id = Column(String, ForeignKey("model_versions.id"), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(String, primary_key=True, default=gen_uuid)
    version_label = Column(String, nullable=False)
    training_run_id = Column(String, ForeignKey("training_runs.id"), nullable=True)
    metrics = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=False)
    artifact_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ApiLog(Base):
    __tablename__ = "api_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=True)
    request_id = Column(String, nullable=True)
    duration_ms = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
