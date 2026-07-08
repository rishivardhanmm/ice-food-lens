"""Training entrypoint for the internal model.

PLACEHOLDER pipeline:
  1. Pull TrainingExample rows with status='reviewed' (i.e. corrected/confirmed
     ground truth only — never train on unreviewed OpenAI output).
  2. Split into train/validation/test (e.g. 70/15/15).
  3. Train a classifier (left as TODO — needs a real feature extractor).
  4. Evaluate on the test split (see evaluate.py).
  5. Save a ModelVersion row; only `promote_if_better` flips is_active.

Run: python -m app.ml.train
"""
import random
from datetime import datetime

from app.db.session import SessionLocal
from app.db.models import TrainingExample, TrainingRun, ModelVersion
from app.ml import evaluate

SPLIT_RATIOS = {"train": 0.7, "validation": 0.15, "test": 0.15}


def split_examples(examples: list) -> dict:
    shuffled = examples[:]
    random.shuffle(shuffled)
    n = len(shuffled)
    n_train = int(n * SPLIT_RATIOS["train"])
    n_val = int(n * SPLIT_RATIOS["validation"])
    return {
        "train": shuffled[:n_train],
        "validation": shuffled[n_train:n_train + n_val],
        "test": shuffled[n_train + n_val:],
    }


def run_training():
    db = SessionLocal()
    run = TrainingRun(status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        examples = db.query(TrainingExample).filter(TrainingExample.status == "reviewed").all()
        splits = split_examples(examples)

        for split_name, items in splits.items():
            for ex in items:
                ex.split = split_name
        db.commit()

        run.train_count = len(splits["train"])
        run.validation_count = len(splits["validation"])
        run.test_count = len(splits["test"])

        # TODO: real feature extraction + model fit goes here.
        metrics = evaluate.evaluate_holdout(splits["test"])

        version = ModelVersion(
            version_label=f"v-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            training_run_id=run.id,
            metrics=metrics,
            is_active=False,
        )
        db.add(version)
        db.commit()
        db.refresh(version)

        run.resulting_model_version_id = version.id
        run.status = "completed"
        run.completed_at = datetime.utcnow()
        run.metrics = metrics
        db.commit()
        return run.id
    except Exception as e:
        run.status = "failed"
        run.error_message = str(e)
        db.commit()
        raise
    finally:
        db.close()


def promote_if_better(new_version_id: str):
    db = SessionLocal()
    try:
        new_version = db.get(ModelVersion, new_version_id)
        active = db.query(ModelVersion).filter(ModelVersion.is_active == True).first()  # noqa: E712

        new_score = (new_version.metrics or {}).get("calorie_mae", float("inf"))
        active_score = (active.metrics or {}).get("calorie_mae", float("inf")) if active else float("inf")

        if new_score < active_score:
            if active:
                active.is_active = False
            new_version.is_active = True
            db.commit()
            return True
        return False
    finally:
        db.close()


if __name__ == "__main__":
    run_id = run_training()
    print(f"Training run completed: {run_id}")
