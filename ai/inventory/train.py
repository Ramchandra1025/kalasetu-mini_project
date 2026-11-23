"""Train inventory stockout-risk model only on an observed future-outcome label.

Expected target column: stockout_within_7d (0/1), recorded after the feature snapshot.
The current 30-row CSV has no such target and is synthetic; training is intentionally blocked.
"""
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

from .config import DATASET_PATH, RESEARCH_EXPERIMENT_DIR, RANDOM_SEED
from .dataset import load_dataset
from .features import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS

TARGET = "stockout_within_7d"


def _make_pipeline():
    try:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=True)
    except TypeError:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse=True)

    preprocessing = ColumnTransformer(
        transformers=[
            ("numeric", SimpleImputer(strategy="median"), NUMERIC_COLUMNS),
            ("categorical", Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", encoder),
            ]), CATEGORICAL_COLUMNS),
        ],
        remainder="drop",
    )
    classifier = XGBClassifier(
        n_estimators=250,
        max_depth=3,
        learning_rate=0.04,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_lambda=2.0,
        eval_metric="logloss",
        random_state=RANDOM_SEED,
        n_jobs=1,
    )
    return Pipeline([("preprocessing", preprocessing), ("classifier", classifier)])


def main():
    frame = load_dataset(DATASET_PATH)
    if TARGET not in frame.columns:
        raise ValueError(
            f"Training blocked: dataset has no '{TARGET}' outcome column. "
            "Collect a dated inventory snapshot, then record whether that item "
            "stocked out during the following 7 days. Do not derive this label "
            "from current_stock or stock_coverage_days."
        )

    required = CATEGORICAL_COLUMNS + NUMERIC_COLUMNS + [TARGET]
    missing = [c for c in required if c not in frame.columns]
    if missing:
        raise ValueError(f"Missing training columns: {missing}")

    frame = frame[required].copy()
    for column in NUMERIC_COLUMNS + [TARGET]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame[TARGET] = frame[TARGET].astype("Int64")
    frame = frame.dropna(subset=required)
    frame = frame[frame[TARGET].isin([0, 1])]
    if frame[TARGET].nunique() != 2 or frame[TARGET].value_counts().min() < 2:
        raise ValueError("Need at least two examples of each outcome class for a stratified holdout.")

    X = frame[CATEGORICAL_COLUMNS + NUMERIC_COLUMNS]
    y = frame[TARGET].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_SEED, stratify=y
    )

    model = _make_pipeline()
    model.fit(X_train, y_train)
    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    metrics = {
        "test_rows": int(len(y_test)),
        "positive_rate": float(y_test.mean()),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, predictions)),
        "average_precision": float(average_precision_score(y_test, probabilities)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)) if y_test.nunique() == 2 else None,
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
        "classification_report": classification_report(y_test, predictions, output_dict=True, zero_division=0),
    }

    RESEARCH_EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "task": "predict stockout within next 7 days",
        "target": TARGET,
        "features": CATEGORICAL_COLUMNS + NUMERIC_COLUMNS,
        "algorithm": "XGBoost Classifier with train-fitted preprocessing",
        "split": "stratified random holdout; replace with chronological split when snapshot_date is available",
        "train_rows": int(len(y_train)),
        "test_rows": int(len(y_test)),
        "metrics": metrics,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "research_valid": False,
        "limitations": [
            "Do not use synthetic data for research claims.",
            "A single random holdout is preliminary, not external validation.",
            "For production research, use dated snapshots and chronological or grouped temporal evaluation.",
            "Calibrate the operating threshold using validation data and report false-negative cost.",
        ],
    }
    path = RESEARCH_EXPERIMENT_DIR / "evaluation_report.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(path), "metrics": metrics, "research_valid": False}, indent=2))


if __name__ == "__main__":
    main()
