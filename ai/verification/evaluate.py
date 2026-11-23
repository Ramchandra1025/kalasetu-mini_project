from pathlib import Path
from typing import Dict, List

import json
import torch
import torch.nn.functional as F

from .config import (
    DEVICE,
    VERIFICATION_THRESHOLD,
    RESULTS_DIR,
)


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(
    embedding_a: torch.Tensor,
    embedding_b: torch.Tensor,
) -> float:

    embedding_a = embedding_a.flatten()
    embedding_b = embedding_b.flatten()

    embedding_a = F.normalize(
        embedding_a,
        p=2,
        dim=0,
    )

    embedding_b = F.normalize(
        embedding_b,
        p=2,
        dim=0,
    )

    return float(
        torch.dot(
            embedding_a,
            embedding_b,
        ).item()
    )


# ============================================================
# BINARY VERIFICATION
# ============================================================

def verify_pair(
    query_embedding: torch.Tensor,
    reference_embedding: torch.Tensor,
    threshold: float = VERIFICATION_THRESHOLD,
) -> Dict:

    similarity = cosine_similarity(
        query_embedding,
        reference_embedding,
    )

    prediction = (
        1
        if similarity >= threshold
        else 0
    )

    return {
        "similarity": similarity,
        "prediction": prediction,
        "status": (
            "MATCH_CANDIDATE"
            if prediction == 1
            else "NO_CONFIDENT_MATCH"
        ),
    }


# ============================================================
# CLASSIFICATION METRICS
# ============================================================

def calculate_metrics(
    y_true: List[int],
    y_pred: List[int],
) -> Dict:

    if len(y_true) != len(y_pred):
        raise ValueError(
            "y_true and y_pred must have "
            "the same length."
        )

    if not y_true:
        raise ValueError(
            "Evaluation data is empty."
        )

    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0

    for actual, predicted in zip(
        y_true,
        y_pred,
    ):

        if actual == 1 and predicted == 1:
            true_positive += 1

        elif actual == 0 and predicted == 0:
            true_negative += 1

        elif actual == 0 and predicted == 1:
            false_positive += 1

        elif actual == 1 and predicted == 0:
            false_negative += 1

    total = len(y_true)

    accuracy = (
        (true_positive + true_negative)
        / total
    )

    precision_denominator = (
        true_positive + false_positive
    )

    recall_denominator = (
        true_positive + false_negative
    )

    precision = (
        true_positive
        / precision_denominator
        if precision_denominator > 0
        else 0.0
    )

    recall = (
        true_positive
        / recall_denominator
        if recall_denominator > 0
        else 0.0
    )

    f1_denominator = (
        precision + recall
    )

    f1 = (
        2 * precision * recall
        / f1_denominator
        if f1_denominator > 0
        else 0.0
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "true_positive": true_positive,
        "true_negative": true_negative,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "total_samples": total,
    }


# ============================================================
# THRESHOLD EVALUATION
# ============================================================

def evaluate_thresholds(
    similarities: List[float],
    labels: List[int],
    thresholds: List[float],
) -> List[Dict]:

    if len(similarities) != len(labels):
        raise ValueError(
            "Similarities and labels must have "
            "the same length."
        )

    if not similarities:
        raise ValueError(
            "Similarity list is empty."
        )

    results = []

    for threshold in thresholds:

        predictions = [
            1
            if similarity >= threshold
            else 0
            for similarity in similarities
        ]

        metrics = calculate_metrics(
            labels,
            predictions,
        )

        metrics["threshold"] = threshold

        results.append(
            metrics
        )

    return results


# ============================================================
# FIND BEST THRESHOLD
# ============================================================

def find_best_threshold(
    threshold_results: List[Dict],
) -> Dict:

    if not threshold_results:
        raise ValueError(
            "Threshold results are empty."
        )

    best = max(
        threshold_results,
        key=lambda result: (
            result["f1_score"],
            result["accuracy"],
        ),
    )

    return best


# ============================================================
# SAVE EVALUATION RESULTS
# ============================================================

def save_results(
    results: Dict,
    filename: str = "evaluation_results.json",
):

    output_path = (
        Path(RESULTS_DIR)
        / filename
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=4,
        )

    return output_path


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("KALASETU - CRAFT VERIFICATION EVALUATION")
    print("=" * 60)

    print(
        f"Device               : {DEVICE}"
    )

    print(
        f"Default threshold    : "
        f"{VERIFICATION_THRESHOLD}"
    )

    # --------------------------------------------------------
    # Synthetic evaluation data.
    #
    # This is ONLY a software test.
    # It is NOT a research result.
    # --------------------------------------------------------

    similarities = [
        0.91,
        0.87,
        0.82,
        0.79,
        0.41,
        0.35,
        0.29,
        0.22,
    ]

    labels = [
        1,
        1,
        1,
        1,
        0,
        0,
        0,
        0,
    ]

    # --------------------------------------------------------
    # Test default threshold.
    # --------------------------------------------------------

    predictions = [
        1
        if similarity >= VERIFICATION_THRESHOLD
        else 0
        for similarity in similarities
    ]

    metrics = calculate_metrics(
        labels,
        predictions,
    )

    print("\nDefault Threshold Evaluation")

    print(
        f"  Accuracy  : "
        f"{metrics['accuracy']:.4f}"
    )

    print(
        f"  Precision : "
        f"{metrics['precision']:.4f}"
    )

    print(
        f"  Recall    : "
        f"{metrics['recall']:.4f}"
    )

    print(
        f"  F1 Score  : "
        f"{metrics['f1_score']:.4f}"
    )

    # --------------------------------------------------------
    # Threshold comparison.
    # --------------------------------------------------------

    thresholds = [
        0.50,
        0.55,
        0.60,
        0.65,
        0.70,
        0.75,
        0.80,
        0.85,
        0.90,
    ]

    threshold_results = evaluate_thresholds(
        similarities,
        labels,
        thresholds,
    )

    best_threshold = find_best_threshold(
        threshold_results
    )

    print("\nBest Threshold")

    print(
        f"  Threshold : "
        f"{best_threshold['threshold']:.2f}"
    )

    print(
        f"  Accuracy  : "
        f"{best_threshold['accuracy']:.4f}"
    )

    print(
        f"  Precision : "
        f"{best_threshold['precision']:.4f}"
    )

    print(
        f"  Recall    : "
        f"{best_threshold['recall']:.4f}"
    )

    print(
        f"  F1 Score  : "
        f"{best_threshold['f1_score']:.4f}"
    )

    # --------------------------------------------------------
    # Save software-test result.
    # --------------------------------------------------------

    result_data = {
        "test_type": "synthetic_pipeline_test",
        "research_valid": False,
        "default_threshold": VERIFICATION_THRESHOLD,
        "default_metrics": metrics,
        "threshold_results": threshold_results,
        "best_threshold": best_threshold,
    }

    output_path = save_results(
        result_data,
        "evaluation_test.json",
    )

    print(
        f"\nTest results saved to:"
    )

    print(
        f"  {output_path}"
    )

    print(
        "\nEvaluation engine test PASSED."
    )