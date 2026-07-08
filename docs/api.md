# FoodLens AI — API Reference

Base URL (local dev): `http://localhost:8000`

## POST /api/analyze-food
`multipart/form-data`

| Field | Type | Required | Notes |
|---|---|---|---|
| image | file | yes | The food photo |
| train | bool | no | If true, saves the example as a `pending_review` training candidate |
| source | string | no | e.g. `ui`, `api`, `postman` |
| user_id | string | no | Caller identity |
| notes | string | no | Extra context passed into the OpenAI prompt |
| use_internal_model | bool | no | If true, tries the internal model first |
| fallback_to_openai | bool | no | If internal confidence is low, fall back to OpenAI |

Response: see `AnalyzeFoodResponse` shape in the README / `app/schemas/food.py`.

## POST /api/corrections
JSON body referencing a `prediction_item_id` returned by `/api/analyze-food`.
Marks the related `training_example` as `reviewed`.

## POST /api/dataset/import-directory
Server-side directory scan (local/admin mode only). Returns a `job_id` and image count.

## POST /api/dataset/process-batch
Runs (or pauses/resumes) OpenAI analysis over a previously imported batch job.

## POST /api/dataset/export
Body: `{ "format": "jsonl" | "csv" }`. Writes to `backend/storage/exports/`.

## POST /api/train/start
Splits `reviewed` training examples into train/validation/test, runs the (placeholder)
training pipeline, and creates a `ModelVersion`.

## GET /api/train/status/{training_run_id}
## GET /api/models
## POST /api/models/promote?model_version_id=...
Promotes a model version to active only if its metrics beat the current active version.

## GET /api/evaluation/summary
Aggregate stats for the Evaluation Dashboard.
