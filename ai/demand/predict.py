"""
KalaSetu - Demand Prediction AI
Prediction / Inference

The current model is trained on synthetic
pipeline-testing data.
"""

import argparse
import json

import numpy as np
import pandas as pd

from .config import (
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
    MIN_PREDICTED_DEMAND,
    ROUND_DEMAND_TO,
)

from .model import (
    load_model,
    load_encoder,
    predict_demand,
)


# ============================================================
# PREPARE INPUT
# ============================================================

def prepare_input(
    product_data,
    encoder,
):

    required_fields = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
    )

    missing_fields = [
        field
        for field in required_fields
        if field not in product_data
    ]

    if missing_fields:

        raise ValueError(
            "Missing required fields:\n"
            + "\n".join(
                f"  - {field}"
                for field in missing_fields
            )
        )

    # --------------------------------------------------------
    # Numeric features
    # --------------------------------------------------------

    numeric_values = []

    for feature in NUMERIC_FEATURES:

        try:

            value = float(
                product_data[feature]
            )

        except (
            TypeError,
            ValueError,
        ):

            raise ValueError(
                f"Invalid numeric value "
                f"for '{feature}'."
            )

        numeric_values.append(
            value
        )

    numeric_array = np.asarray(
        numeric_values,
        dtype=np.float32,
    ).reshape(1, -1)

    # --------------------------------------------------------
    # Categorical features
    # --------------------------------------------------------

    categorical_data = pd.DataFrame(
        [
            {
                feature:
                    str(
                        product_data[
                            feature
                        ]
                    )
                    .strip()
                    .lower()

                for feature
                in CATEGORICAL_FEATURES
            }
        ]
    )

    encoded_categories = (
        encoder.transform(
            categorical_data
        )
    )

    encoded_array = np.asarray(
        encoded_categories,
        dtype=np.float32,
    )

    # --------------------------------------------------------
    # Final feature vector
    # --------------------------------------------------------

    features = np.concatenate(
        [
            numeric_array,
            encoded_array,
        ],
        axis=1,
    )

    return features


# ============================================================
# PREDICT DEMAND
# ============================================================

def predict_future_demand(
    product_data,
):

    model = load_model()

    encoder = load_encoder()

    features = prepare_input(
        product_data,
        encoder,
    )

    prediction = predict_demand(
        model,
        features,
    )

    predicted_demand = float(
        prediction[0]
    )

    predicted_demand = max(
        predicted_demand,
        MIN_PREDICTED_DEMAND,
    )

    if ROUND_DEMAND_TO > 0:

        predicted_demand = (
            round(
                predicted_demand
                / ROUND_DEMAND_TO
            )
            * ROUND_DEMAND_TO
        )

    return {

        "predicted_demand":
            float(predicted_demand),

        "unit":
            "demand_index",

        "model":
            "XGBRegressor",

        "data_type":
            "synthetic_pipeline_testing_data",

        "research_valid":
            False,

        "warning":
            (
                "This prediction is generated "
                "by a prototype model trained "
                "on synthetic pipeline-testing data."
            ),
    }


# ============================================================
# CLI
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "KalaSetu Demand Prediction AI"
        )
    )

    parser.add_argument(
        "--product-category",
        required=True,
    )

    parser.add_argument(
        "--region",
        required=True,
    )

    parser.add_argument(
        "--month",
        required=True,
        type=float,
    )

    parser.add_argument(
        "--season",
        required=True,
    )

    parser.add_argument(
        "--historical-demand",
        required=True,
        type=float,
    )

    parser.add_argument(
        "--previous-demand",
        required=True,
        type=float,
    )

    parser.add_argument(
        "--price",
        required=True,
        type=float,
    )

    parser.add_argument(
        "--demand-growth",
        required=True,
        type=float,
    )

    args = parser.parse_args()

    product_data = {

        "product_category":
            args.product_category,

        "region":
            args.region,

        "month":
            args.month,

        "season":
            args.season,

        "historical_demand":
            args.historical_demand,

        "previous_demand":
            args.previous_demand,

        "price":
            args.price,

        "demand_growth":
            args.demand_growth,
    }

    print("=" * 70)
    print("KALASETU - DEMAND PREDICTION AI")
    print("=" * 70)

    print("\nProduct Input:")

    for key, value in (
        product_data.items()
    ):

        print(
            f"  {key:<22}: {value}"
        )

    print(
        "\nRunning prediction..."
    )

    result = predict_future_demand(
        product_data
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "PREDICTION RESULT"
    )

    print(
        "=" * 70
    )

    print(
        f"\nPredicted Demand: "
        f"{result['predicted_demand']:.0f}"
    )

    print(
        f"Unit            : "
        f"{result['unit']}"
    )

    print(
        f"Model           : "
        f"{result['model']}"
    )

    print(
        f"Research Valid  : "
        f"{result['research_valid']}"
    )

    print(
        f"\nWarning:\n"
        f"{result['warning']}"
    )

    print(
        "\nJSON Result:"
    )

    print(
        json.dumps(
            result,
            indent=4,
        )
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "PREDICTION TEST PASSED"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()