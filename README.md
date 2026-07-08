# FoodLens AI

AI-assisted food nutrition estimation from a photo: detected food items, estimated
quantity, calories, macros, micronutrients, confidence scores, assumptions, and warnings.

> **Disclaimer:** This is an AI estimate and should not be used as medical advice. For
> clinical nutrition, diabetes management, eating disorder care, or medical conditions,
> consult a qualified professional.

## Modes

1. **Web UI** — `frontend/` (Next.js + TypeScript + Tailwind): upload, results, corrections,
   Dataset Builder, Evaluation Dashboard.
2. **REST API** — `backend/` (FastAPI): `POST /api/analyze-food` for Postman/curl demos.
   See [docs/api.md](docs/api.md) and [postman/FoodLens.postman_collection.json](postman/FoodLens.postman_collection.json).
3. **Training / dataset preparation** — directory batch processing, JSONL/CSV dataset export,
   and an internal-model pipeline scaffold under `backend/app/ml/`.

## Architecture

```
frontend/        Next.js app (upload, dataset builder, evaluation dashboard)
backend/
  app/api/       FastAPI route modules (analyze, corrections, dataset, training, evaluation)
  app/services/  OpenAI vision integration, file storage
  app/ml/        Internal model pipeline placeholders (preprocess, model, lookup, train, evaluate, export)
  app/db/        SQLAlchemy models + session
  app/schemas/   Pydantic request/response schemas
  storage/       uploads/ and exports/ (gitignored in practice)
postman/         Postman collection
docs/            API reference
sample_test_images/  Drop test photos here for batch demos
```

## Database schema (SQLite for MVP, swap `DATABASE_URL` for Postgres)

`images`, `predictions`, `prediction_items`, `user_corrections`, `training_examples`,
`training_runs`, `model_versions`, `api_logs` — see `backend/app/db/models.py`.

## Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
cp .env.example .env            # then set OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```

Tables are created automatically on startup (`Base.metadata.create_all`). For schema
changes in a real deployment, introduce Alembic migrations.

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Visit `http://localhost:3000`.

## Quick demo (curl)

```bash
curl -X POST http://localhost:8000/api/analyze-food \
  -F "image=@sample_test_images/meal1.jpg" \
  -F "train=true" \
  -F "source=curl" \
  -F "use_internal_model=false" \
  -F "fallback_to_openai=true"
```

Then submit a correction using a `prediction_item_id` from the response:

```bash
curl -X POST http://localhost:8000/api/corrections \
  -H "Content-Type: application/json" \
  -d '{
    "prediction_item_id": "REPLACE_ME",
    "corrected_name": "grilled chicken breast",
    "corrected_quantity_value": 150,
    "corrected_calories_kcal": 250,
    "corrected_protein_g": 46
  }'
```

## Training flow

1. UI/API calls with `train=true` save image + OpenAI prediction as `training_examples`
   with `status=pending_review`.
2. A human reviews/corrects via the correction form → `POST /api/corrections` marks the
   example `reviewed`. Only reviewed examples are eligible for training.
3. `POST /api/train/start` splits reviewed examples 70/15/15 into train/validation/test,
   runs `app/ml/train.py` (placeholder — wire in a real classifier), and records a
   `ModelVersion` with evaluation metrics.
4. `POST /api/models/promote` only flips the active model if the new version's metrics
   beat the current active version (lower calorie MAE).

## Internal model status

There is **no trained internal model yet** — `app/ml/internal_model.py` is an explicit
low-confidence placeholder so the `use_internal_model` / `fallback_to_openai` branching in
`POST /api/analyze-food` can be exercised end-to-end. The pipeline scaffold (preprocess →
detect/classify → portion estimate → nutrition lookup → calibration → confidence) is in
`backend/app/ml/`.

## Dataset export format (JSONL)

Each line is one training example:

```json
{"example_id": "...", "status": "reviewed", "split": "train", "image_filename": "meal1.jpg",
 "model_used": "openai", "items": [{"name": "...", "category": "...", "quantity_value": 150,
 "calories_kcal": 250, "protein_g": 46, "carbs_g": 0, "fat_g": 5, "confidence": 0.7}],
 "correction": {"corrected_name": "...", "corrected_calories_kcal": 250, "...": "..."}}
```

## Notes

- This is an MVP scaffold meant to run locally end-to-end, not a production system.
- Swap SQLite for Postgres by changing `DATABASE_URL` in `backend/.env`.
- Folder upload in the Dataset Builder uses the non-standard `webkitdirectory` attribute
  (browser mode); server-side directory scanning is for local/admin use only, since browsers
  cannot read arbitrary local paths.
