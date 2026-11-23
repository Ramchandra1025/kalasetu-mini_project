"""Train an Isolation Forest using only the normal training partition.

The small bundled dataset is synthetic. The labelled holdout metrics below are
diagnostics only and must not be presented as real-world fraud detection results.
"""
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split

from .dataset import load_dataset, prepare_dataset, validate_dataset
from .features import build_feature_matrix
from .model import AnomalyDetector
from .config import (
    MODEL_PATH, RESEARCH_EXPERIMENT_DIR, MODEL_NAME, MODEL_VERSION,
    DATASET_TYPE, RESEARCH_VALID, RANDOM_SEED,
)


def _align_to_training_columns(frame, columns):
    return frame.reindex(columns=columns, fill_value=0.0)


def train():
    df = load_dataset()
    validation = validate_dataset(df)
    if not validation["valid"]:
        raise ValueError(f"Invalid anomaly dataset: {validation}")

    df = prepare_dataset(df)
    if "is_anomaly" not in df.columns:
        raise ValueError("Anomaly dataset must contain the is_anomaly label.")
    labels = df["is_anomaly"].astype(int)
    if not set(labels.unique()).issubset({0, 1}):
        raise ValueError("is_anomaly must contain only 0 (normal) and 1 (anomaly).")
    if labels.nunique() < 2:
        raise ValueError("Both normal and anomaly labels are required for holdout evaluation.")

    train_idx, test_idx = train_test_split(
        np.arange(len(df)), test_size=0.25, random_state=RANDOM_SEED,
        stratify=labels,
    )
    train_df = df.iloc[train_idx].copy()
    test_df = df.iloc[test_idx].copy()
    y_train = labels.iloc[train_idx].to_numpy()
    y_test = labels.iloc[test_idx].to_numpy()

    # Isolation Forest is unsupervised: fit its reference distribution only
    # on labelled-normal training observations, never on known anomalies.
    X_train_all = build_feature_matrix(train_df)
    normal_mask = y_train == 0
    X_normal = X_train_all.loc[normal_mask].copy()
    if len(X_normal) < 5:
        raise ValueError("At least five normal training observations are required.")

    detector = AnomalyDetector()
    detector.fit(X_normal)

    X_test = _align_to_training_columns(
        build_feature_matrix(test_df), detector.feature_columns
    )
    predictions = detector.predict(X_test)
    predicted_anomaly = (predictions == -1).astype(int)
    scores = detector.anomaly_score(X_test)

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, predicted_anomaly, average="binary", zero_division=0
    )
    try:
        average_precision = float(average_precision_score(y_test, scores))
    except ValueError:
        average_precision = None

    detector.save(MODEL_PATH)

    metadata = {
        "model_name": MODEL_NAME,
        "model_version": "1.1.0",
        "algorithm": "Isolation Forest (fit on normal training rows only)",
        "dataset_type": DATASET_TYPE,
        "research_valid": False,
        "total_rows": len(df),
        "train_rows": len(train_idx),
        "test_rows": len(test_idx),
        "normal_rows_used_for_fit": int(normal_mask.sum()),
        "test_metrics": {
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "average_precision": average_precision,
            "confusion_matrix_labels_0_normal_1_anomaly": confusion_matrix(
                y_test, predicted_anomaly, labels=[0, 1]
            ).tolist(),
        },
        "classification_report": classification_report(
            y_test, predicted_anomaly, output_dict=True, zero_division=0
        ),
        "warning": (
            "Synthetic 30-row dataset. Holdout metrics are pipeline diagnostics "
            "only; validate on temporally separated, real transaction outcomes."
        ),
        "model_path": str(MODEL_PATH),
    }
    output_dir = Path(RESEARCH_EXPERIMENT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "training_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print(json.dumps(metadata["test_metrics"], indent=2))
    print("Research valid: NO (synthetic dataset).")
    return detector


if __name__ == "__main__":
    train()
