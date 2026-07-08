from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import Base, engine
from app.db import models  # noqa: F401 (ensures models are registered before create_all)
from app.api import analyze, corrections, dataset, training, evaluation

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FoodLens AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, tags=["analyze"])
app.include_router(corrections.router, tags=["corrections"])
app.include_router(dataset.router, tags=["dataset"])
app.include_router(training.router, tags=["training"])
app.include_router(evaluation.router, tags=["evaluation"])


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.app_env}
