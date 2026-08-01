"""
Dataset Management + Model Retraining service (Module 14).

Previously /api/admin/model/retrain did nothing at all — it returned a
hardcoded "successfully triggered in background" message with a fake
version string and fake metrics, without touching the model file, without
persisting anything to model_registry, and without any dataset to retrain
on in the first place (Module 14's "Dataset Management" sub-feature didn't
exist as any endpoint). This module makes both real:

  - Admins can upload a real labeled CSV (once a college/placement-cell
    dataset exists) via /api/admin/dataset/upload. Until then, the system
    transparently falls back to the same synthetic dataset generator the
    initial model was trained on (see app/ml/train_placement_model.py for
    why that's disclosed as synthetic, not real, data).
  - /api/admin/model/retrain actually re-runs the same 4-model comparison
    (Random Forest / SVM / MLP / XGBoost) against whichever dataset is
    currently active, overwrites the .joblib + feature_order.json + metrics
    files, hot-reloads the in-memory model so predictions immediately use
    the new one, and persists a real ModelRegistry row with the real
    resulting metrics — not fabricated numbers.
"""
import os
import io
import datetime
from typing import Dict, Any

import pandas as pd

from app.ml.train_placement_model import (
    FEATURE_ORDER, generate_synthetic_dataset, train_and_compare, MODEL_DIR,
)
from app.services.prediction_service import reload_model

REQUIRED_COLUMNS = FEATURE_ORDER + ["placed"]
DATASET_DIR = os.path.join(MODEL_DIR, "..", "datasets")
os.makedirs(DATASET_DIR, exist_ok=True)
UPLOADED_DATASET_PATH = os.path.join(DATASET_DIR, "uploaded_dataset.csv")

MIN_ROWS_FOR_TRAINING = 50  # below this, a train/test split is too small to trust


def _load_active_dataset() -> Dict[str, Any]:
    if os.path.exists(UPLOADED_DATASET_PATH):
        df = pd.read_csv(UPLOADED_DATASET_PATH)
        return {"df": df, "source": "uploaded"}
    df = generate_synthetic_dataset()
    return {"df": df, "source": "synthetic"}


def get_dataset_info() -> Dict[str, Any]:
    active = _load_active_dataset()
    df = active["df"]
    info = {
        "source": active["source"],
        "row_count": len(df),
        "columns": list(df.columns),
        "positive_class_ratio": round(float(df["placed"].mean()), 4) if "placed" in df.columns else None,
    }
    if active["source"] == "uploaded":
        info["uploaded_at"] = datetime.datetime.fromtimestamp(
            os.path.getmtime(UPLOADED_DATASET_PATH)
        ).isoformat()
    return info


def validate_and_save_dataset(file_bytes: bytes) -> Dict[str, Any]:
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
    except Exception as e:
        raise ValueError(f"Could not parse file as CSV: {e}")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Dataset is missing required columns: {missing}. "
            f"Required columns are: {REQUIRED_COLUMNS}"
        )

    if len(df) < MIN_ROWS_FOR_TRAINING:
        raise ValueError(
            f"Dataset has only {len(df)} rows; at least {MIN_ROWS_FOR_TRAINING} "
            f"are needed for a meaningful train/test split."
        )

    if not set(df["placed"].unique()).issubset({0, 1}):
        raise ValueError('The "placed" label column must contain only 0 or 1.')

    df[REQUIRED_COLUMNS].to_csv(UPLOADED_DATASET_PATH, index=False)
    return get_dataset_info()


def retrain_model() -> Dict[str, Any]:
    active = _load_active_dataset()
    df = active["df"]

    results, xgb_model = train_and_compare(df)  # writes .joblib + feature_order.json + metrics.json
    reload_model()  # next prediction call picks up the freshly-written model, no restart needed

    version = f"v-{datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-XGBoost"
    return {
        "model_name": "PlacementXGBoostClassifier",
        "new_version": version,
        "dataset_source": active["source"],
        "dataset_rows": len(df),
        "metrics": results,  # real accuracy/roc_auc/f1 for all 4 compared models
    }