"""
KalaSetu - Demand Prediction AI
Feature Engineering
"""

import numpy as np
import pandas as pd


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def engineer_features(dataframe):

    dataframe = dataframe.copy()

    # --------------------------------------------------------
    # Demand momentum
    # --------------------------------------------------------

    dataframe["demand_momentum"] = (
        dataframe["historical_demand"]
        - dataframe["previous_demand"]
    )

    # --------------------------------------------------------
    # Demand ratio
    # --------------------------------------------------------

    dataframe["demand_ratio"] = (
        dataframe["historical_demand"]
        /
        dataframe["previous_demand"]
        .replace(0, 1)
    )

    # --------------------------------------------------------
    # Price-adjusted demand
    # --------------------------------------------------------

    dataframe["demand_per_price"] = (
        dataframe["historical_demand"]
        /
        dataframe["price"]
        .replace(0, 1)
    )

    # --------------------------------------------------------
    # Price impact proxy
    # --------------------------------------------------------

    dataframe["price_demand_interaction"] = (
        dataframe["price"]
        * dataframe["historical_demand"]
    )

    # --------------------------------------------------------
    # Growth direction
    # --------------------------------------------------------

    dataframe["growth_positive"] = (
        dataframe["demand_growth"] > 0
    ).astype(int)

    # --------------------------------------------------------
    # Month cyclic features
    # --------------------------------------------------------

    dataframe["month_sin"] = np.sin(
        2 * np.pi * dataframe["month"] / 12
    )

    dataframe["month_cos"] = np.cos(
        2 * np.pi * dataframe["month"] / 12
    )

    # --------------------------------------------------------
    # Clean infinite values
    # --------------------------------------------------------

    dataframe = dataframe.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    dataframe = dataframe.fillna(0)

    return dataframe


# ============================================================
# FEATURE SUMMARY
# ============================================================

def get_feature_summary(dataframe):

    engineered = engineer_features(
        dataframe
    )

    summary = {
        "original_columns": len(
            dataframe.columns
        ),
        "engineered_columns": len(
            engineered.columns
        ),
        "new_features": [
            column
            for column in engineered.columns
            if column not in dataframe.columns
        ],
    }

    return summary


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    from .dataset import load_dataset

    print("=" * 70)
    print("KALASETU - DEMAND FEATURE ENGINEERING TEST")
    print("=" * 70)

    dataframe = load_dataset()

    print(
        f"Original columns : "
        f"{len(dataframe.columns)}"
    )

    engineered = engineer_features(
        dataframe
    )

    print(
        f"Engineered columns : "
        f"{len(engineered.columns)}"
    )

    print("\nNew features:")

    for column in engineered.columns:

        if column not in dataframe.columns:

            print(
                f"  - {column}"
            )

    print(
        "\nFEATURE ENGINEERING TEST PASSED."
    )

    print("=" * 70)