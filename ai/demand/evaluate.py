"""
KalaSetu - Demand Prediction AI
Evaluation Pipeline
"""

import json

import numpy as np

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from .dataset import create_datasets

from .model import (
    load_model,
    predict_demand,
)

from .config import (
    EVALUATION_DIR,
    RESULTS_DIR,
)


# ============================================================
# MAPE
# ============================================================

def calculate_mape(
    actual,
    predicted,
):

    actual = np.asarray(
        actual,
        dtype=float,
    )

    predicted = np.asarray(
        predicted,
        dtype=float,
    )

    denominator = np.where(
        actual == 0,
        1,
        actual,
    )

    percentage_error = (
        np.abs(
            (actual - predicted)
            / denominator
        )
        * 100
    )

    return float(
        np.mean(
            percentage_error
        )
    )


# ============================================================
# EVALUATION
# ============================================================

def main():

    print("=" * 70)
    print("KALASETU - DEMAND PREDICTION EVALUATION")
    print("=" * 70)

    datasets = create_datasets()

    X_test = datasets["X_test"]
    y_test = datasets["y_test"]

    model = load_model()

    predictions = predict_demand(
        model,
        X_test,
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions,
        )
    )

    r2 = r2_score(
        y_test,
        predictions,
    )

    mape = calculate_mape(
        y_test,
        predictions,
    )

    print(
        f"\nTest samples: {len(y_test)}"
    )

    print(
        f"MAE  : {mae:.2f}"
    )

    print(
        f"RMSE : {rmse:.2f}"
    )

    print(
        f"R²   : {r2:.4f}"
    )

    print(
        f"MAPE : {mape:.2f}%"
    )

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    print(
        "\nTest Predictions:"
    )

    for index, (
        actual,
        predicted,
    ) in enumerate(
        zip(
            y_test,
            predictions,
        ),
        start=1,
    ):

        error = abs(
            actual - predicted
        )

        print(
            f"Sample {index} "
            f"Actual {actual:.2f} "
            f"Predicted {predicted:.2f} "
            f"Error {error:.2f}"
        )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    results = {

        "test_samples":
            len(y_test),

        "mae":
            float(mae),

        "rmse":
            float(rmse),

        "r2":
            float(r2),

        "mape":
            float(mape),

        "data_type":
            "synthetic_pipeline_testing_data",

        "research_valid":
            False,

        "reason":
            (
                "Current demand dataset is "
                "synthetic pipeline-testing data."
            ),
    }

    evaluation_file = (
        EVALUATION_DIR
        / "evaluation_results.json"
    )

    result_file = (
        RESULTS_DIR
        / "evaluation_results.json"
    )

    for output_file in [
        evaluation_file,
        result_file,
    ]:

        with open(
            output_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                results,
                file,
                indent=4,
            )

    print(
        "\nEvaluation results saved."
    )

    print(
        "\nResearch status:"
    )

    print(
        "Research-valid result: NO"
    )

    print(
        "Reason: Current demand dataset "
        "is synthetic pipeline-testing data."
    )

    print(
        "\nEVALUATION TEST PASSED."
    )

    print("=" * 70)


if __name__ == "__main__":
    main()