"""Real-data evaluation for same-product image matching.

CSV: ml/datasets/verification/pairs.csv
Required columns: image_a,image_b,label,split
- image_a/image_b: paths relative to ml/datasets/verification/
- label: 1 = same physical product, 0 = different physical products
- split: train/validation/test; do not put images from the same product across splits.

This evaluates visual matching only. It does NOT prove artisan identity, provenance,
handmade status, or product authenticity.
"""
import json
from pathlib import Path

import pandas as pd
import torch
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from .config import DATASET_ROOT, RESULTS_DIR
from .embeddings import create_encoder, generate_embedding
from .similarity import cosine_similarity

PAIR_FILE = DATASET_ROOT / "pairs.csv"


def _metrics(labels, scores, threshold):
    predictions = [int(score >= threshold) for score in scores]
    return {
        "threshold": float(threshold),
        "accuracy": float(accuracy_score(labels, predictions)),
        "precision": float(precision_score(labels, predictions, zero_division=0)),
        "recall": float(recall_score(labels, predictions, zero_division=0)),
        "f1": float(f1_score(labels, predictions, zero_division=0)),
        "confusion_matrix": confusion_matrix(labels, predictions, labels=[0, 1]).tolist(),
        "roc_auc": float(roc_auc_score(labels, scores)) if len(set(labels)) == 2 else None,
        "average_precision": float(average_precision_score(labels, scores)) if len(set(labels)) == 2 else None,
    }


def main():
    if not PAIR_FILE.exists():
        raise FileNotFoundError(
            f"Create {PAIR_FILE} with image_a,image_b,label,split columns. "
            "Use verified same/different physical-product pairs and keep products "
            "disjoint across train/validation/test."
        )

    frame = pd.read_csv(PAIR_FILE)
    required = {"image_a", "image_b", "label", "split"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Missing pair dataset columns: {missing}")

    frame["label"] = pd.to_numeric(frame["label"], errors="coerce")
    frame = frame.dropna(subset=["image_a", "image_b", "label", "split"]).copy()
    if not frame["label"].isin([0, 1]).all():
        raise ValueError("Pair labels must be binary: 1=same product, 0=different product.")
    if not {"validation", "test"}.issubset(set(frame["split"].str.lower())):
        raise ValueError("Provide separate validation and test rows; do not tune on the test set.")

    frame["split"] = frame["split"].str.lower()
    paths = set(frame["image_a"].astype(str)) | set(frame["image_b"].astype(str))
    encoder = create_encoder()
    embeddings = {}
    for relative_path in sorted(paths):
        image_path = DATASET_ROOT / relative_path
        if not image_path.is_file():
            raise FileNotFoundError(f"Pair image not found: {image_path}")
        embeddings[relative_path] = generate_embedding(encoder, image_path)

    frame["similarity"] = frame.apply(
        lambda row: cosine_similarity(
            embeddings[str(row["image_a"])],
            embeddings[str(row["image_b"])],
        ),
        axis=1,
    )

    validation = frame[frame["split"] == "validation"]
    test = frame[frame["split"] == "test"]
    if validation["label"].nunique() != 2 or test["label"].nunique() != 2:
        raise ValueError("Both validation and test splits must contain positive and negative pairs.")

    candidates = sorted(set(validation["similarity"].round(6).tolist()))
    threshold_results = [
        _metrics(validation["label"].astype(int).tolist(),
                 validation["similarity"].tolist(), threshold)
        for threshold in candidates
    ]
    best_validation = max(threshold_results, key=lambda item: (item["f1"], item["precision"]))
    final_threshold = best_validation["threshold"]

    test_metrics = _metrics(
        test["label"].astype(int).tolist(),
        test["similarity"].tolist(),
        final_threshold,
    )
    report = {
        "task": "same physical product image matching",
        "encoder": "pretrained EfficientNet-B0 embeddings",
        "pair_count": int(len(frame)),
        "validation_pairs": int(len(validation)),
        "test_pairs": int(len(test)),
        "threshold_selected_on_validation": final_threshold,
        "validation_metrics": best_validation,
        "held_out_test_metrics": test_metrics,
        "research_valid": False,
        "limitations": [
            "The pair CSV must be genuinely labelled and products must be disjoint across splits.",
            "Image similarity is not evidence of artisan identity or product authenticity.",
            "This benchmark evaluates the current fixed pretrained encoder, not a fine-tuned model.",
            "Report performance by craft category, lighting, viewpoint, and image source when sample size permits.",
        ],
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output = RESULTS_DIR / "real_pair_evaluation.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "threshold": final_threshold,
        "held_out_test_metrics": test_metrics,
        "research_valid": False,
        "report": str(output),
    }, indent=2))


if __name__ == "__main__":
    main()
