"""
KalaSetu - Fair Pricing AI
Model Evaluation

Metrics:
    MAE
    RMSE
    R2
    MAPE

IMPORTANT:
    Current pricing dataset is synthetic.
    Evaluation results are pipeline-testing results only.
    They must NOT be presented as research findings.
"""

import json
from datetime import datetime

import numpy as np
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from .dataset import create_datasets
from .model import load_model, predict_price

from .config import (
    EVALUATION_DIR,
    RESULTS_DIR,
)


# ============================================================
# MAPE
# ============================================================

def calculate_mape(y_true, y_pred):
    """
    Calculate Mean Absolute Percentage Error.

    Zero actual values are ignored to avoid division by zero.
    """

    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)

    mask = y_true != 0

    if not np.any(mask):
        return 0.0

    percentage_error = (
        np.abs(
            (y_true[mask] - y_pred[mask])
            / y_true[mask]
        )
        * 100
    )

    return float(np.mean(percentage_error))


# ============================================================
# CALCULATE METRICS
# ============================================================

def calculate_metrics(y_true, y_pred):
    """
    Calculate regression evaluation metrics.
    """

    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)

    mae = mean_absolute_error(
        y_true,
        y_pred,
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_true,
            y_pred,
        )
    )

    r2 = r2_score(
        y_true,
        y_pred,
    )

    mape = calculate_mape(
        y_true,
        y_pred,
    )

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
        "mape": float(mape),
    }


# ============================================================
# SAVE EVALUATION
# ============================================================

def save_evaluation(
    metrics,
    y_true,
    y_pred,
):
    """
    Save evaluation results as JSON.
    """

    evaluation = {
        "model": "XGBRegressor",
        "task": "fair_price_regression",

        "metrics": metrics,

        "predictions": [
            {
                "actual_price": float(actual),
                "predicted_price": float(predicted),
                "absolute_error": float(
                    abs(actual - predicted)
                ),
            }
            for actual, predicted
            in zip(y_true, y_pred)
        ],

        "data_type": "synthetic_pipeline_testing_data",

        "research_valid": False,

        "warning": (
            "These evaluation results are based on "
            "synthetic pipeline-testing data and must "
            "not be presented as research findings."
        ),

        "created_at": datetime.now().isoformat(),
    }

    evaluation_file = (
        EVALUATION_DIR
        / "evaluation_results.json"
    )

    with open(
        evaluation_file,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            evaluation,
            file,
            indent=4,
        )

    # Also save a compact result copy
    result_file = (
        RESULTS_DIR
        / "evaluation_results.json"
    )

    with open(
        result_file,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            evaluation,
            file,
            indent=4,
        )

    print("\nEvaluation results saved:")

    print(
        f"  {evaluation_file}"
    )

    print(
        f"  {result_file}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("KALASETU - FAIR PRICING AI EVALUATION")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Prepare dataset
    # --------------------------------------------------------

    print("\n[1/4] Preparing test dataset...")

    datasets = create_datasets()

    X_test = datasets["X_test"]
    y_test = datasets["y_test"]

    print(
        f"Test samples available: {len(X_test)}"
    )

    # --------------------------------------------------------
    # 2. Load trained model
    # --------------------------------------------------------

    print("\n[2/4] Loading trained model...")

    model = load_model()

    print("Pricing model loaded successfully.")

    # --------------------------------------------------------
    # 3. Generate predictions
    # --------------------------------------------------------

    print("\n[3/4] Generating test predictions...")

    predictions = predict_price(
        model,
        X_test,
    )

    print(
        f"Predictions generated: {len(predictions)}"
    )

    # --------------------------------------------------------
    # 4. Calculate metrics
    # --------------------------------------------------------

    print("\n[4/4] Calculating evaluation metrics...")

    metrics = calculate_metrics(
        y_test,
        predictions,
    )

    print("\n" + "=" * 70)
    print("EVALUATION RESULTS")
    print("=" * 70)

    print(
        f"\nMAE  : ₹{metrics['mae']:.2f}"
    )

    print(
        f"RMSE : ₹{metrics['rmse']:.2f}"
    )

    print(
        f"R²   : {metrics['r2']:.4f}"
    )

    print(
        f"MAPE : {metrics['mape']:.2f}%"
    )

    # --------------------------------------------------------
    # Prediction table
    # --------------------------------------------------------

    print("\nTest Predictions:")

    for index, (actual, predicted) in enumerate(
        zip(y_test, predictions)
    ):

        error = abs(
            float(actual)
            - float(predicted)
        )

        print(
            f"  Sample {index + 1}: "
            f"Actual = ₹{float(actual):.2f} | "
            f"Predicted = ₹{float(predicted):.2f} | "
            f"Error = ₹{error:.2f}"
        )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_evaluation(
        metrics,
        y_test,
        predictions,
    )

    print("\n" + "=" * 70)
    print("EVALUATION PIPELINE COMPLETED")
    print("=" * 70)

    print("\nResearch status:")
    print("  Research-valid result: NO")

    print(
        "\nReason:"
        "\n  Current pricing dataset is synthetic "
        "pipeline-testing data."
    )

    print("\nEVALUATION TEST PASSED.")


if __name__ == "__main__":
    main()