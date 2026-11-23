import json
from pathlib import Path

import pandas as pd

from .dataset import (
    load_dataset,
    prepare_dataset,
)

from .features import (
    build_feature_matrix,
)

from .model import (
    AnomalyDetector,
)

from .config import (
    MODEL_PATH,
    RESEARCH_EVALUATION_DIR,
    RESEARCH_VALID,
)


def classify_risk(
    score: float,
) -> str:

    if score >= 75:
        return "HIGH RISK"

    if score >= 50:
        return "SUSPICIOUS"

    return "NORMAL"


def evaluate():

    print("=" * 60)
    print("KALASETU - ANOMALY DETECTION EVALUATION")
    print("=" * 60)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    df = load_dataset()

    df = prepare_dataset(df)

    # --------------------------------------------------------
    # Features
    # --------------------------------------------------------

    X = build_feature_matrix(df)

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    detector = AnomalyDetector.load(
        MODEL_PATH
    )

    predictions = detector.predict(X)

    scores = detector.anomaly_score(X)

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    results = df.copy()

    results["anomaly_prediction"] = (
        predictions
    )

    results["risk_score"] = scores.round(2)

    results["risk_level"] = [
        classify_risk(score)
        for score in scores
    ]

    results["detected_anomaly"] = (
        predictions == -1
    )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    total = len(results)

    anomaly_count = int(
        results["detected_anomaly"].sum()
    )

    normal_count = (
        total - anomaly_count
    )

    high_risk = int(
        (
            results["risk_level"]
            == "HIGH RISK"
        ).sum()
    )

    suspicious = int(
        (
            results["risk_level"]
            == "SUSPICIOUS"
        ).sum()
    )

    normal = int(
        (
            results["risk_level"]
            == "NORMAL"
        ).sum()
    )

    summary = {

        "total_samples": total,

        "anomalies_detected": anomaly_count,

        "normal_samples": normal_count,

        "high_risk": high_risk,

        "suspicious": suspicious,

        "normal": normal,

        "average_risk_score": float(
            scores.mean()
        ),

        "research_valid": RESEARCH_VALID,

        "dataset_type": "synthetic",
    }

    # --------------------------------------------------------
    # Save evaluation
    # --------------------------------------------------------

    output_dir = Path(
        RESEARCH_EVALUATION_DIR
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_path = (
        output_dir
        / "evaluation_summary.json"
    )

    results_path = (
        output_dir
        / "evaluation_results.csv"
    )

    with open(
        summary_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=4,
        )

    results.to_csv(
        results_path,
        index=False,
    )

    # --------------------------------------------------------
    # Print
    # --------------------------------------------------------

    print(
        f"Total samples: {total}"
    )

    print(
        f"Anomalies detected: {anomaly_count}"
    )

    print(
        f"Normal samples: {normal_count}"
    )

    print(
        f"High risk: {high_risk}"
    )

    print(
        f"Suspicious: {suspicious}"
    )

    print(
        f"Normal: {normal}"
    )

    print(
        f"Average risk score: "
        f"{scores.mean():.2f}"
    )

    print(
        f"Research valid: "
        f"{RESEARCH_VALID}"
    )

    print()
    print(
        "Top anomaly samples:"
    )

    print(
        results.sort_values(
            "risk_score",
            ascending=False,
        )[
            [
                "activity_id",
                "activity_type",
                "risk_score",
                "risk_level",
            ]
        ].head(5).to_string(
            index=False
        )
    )

    print()
    print(
        f"Evaluation saved to:\n"
        f"{output_dir}"
    )

    print("=" * 60)

    return results


if __name__ == "__main__":
    evaluate()