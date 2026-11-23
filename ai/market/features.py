"""
KalaSetu - Market Opportunity Intelligence
Feature Engineering
"""

import pandas as pd

from .config import (
    NUMERIC_FEATURES,
    WEIGHTS,
)


# ============================================================
# NORMALIZE SCORE
# ============================================================

def normalize_score(
    value,
    minimum=0.0,
    maximum=100.0,
):

    if maximum == minimum:

        return 0.0

    score = (
        (value - minimum)
        / (maximum - minimum)
    ) * 100.0

    return max(
        0.0,
        min(
            100.0,
            score,
        ),
    )


# ============================================================
# CALCULATE WEIGHTED SCORE
# ============================================================

def calculate_weighted_score(
    row,
):

    score = 0.0

    for feature, weight in WEIGHTS.items():

        value = float(
            row[feature]
        )

        score += (
            value * weight
        )

    return max(
        0.0,
        min(
            100.0,
            score,
        ),
    )


# ============================================================
# ENGINEER MARKET FEATURES
# ============================================================

def engineer_features(
    dataframe,
):

    dataframe = dataframe.copy()

    # --------------------------------------------------------
    # Weighted opportunity score
    # --------------------------------------------------------

    dataframe[
        "opportunity_score"
    ] = dataframe.apply(
        calculate_weighted_score,
        axis=1,
    )

    # --------------------------------------------------------
    # Demand-price balance
    # --------------------------------------------------------

    dataframe[
        "demand_price_balance"
    ] = (
        dataframe["demand_score"]
        * dataframe["price_opportunity"]
    ) / 100.0

    # --------------------------------------------------------
    # Market momentum
    # --------------------------------------------------------

    dataframe[
        "market_momentum"
    ] = (
        dataframe["market_growth"]
        * dataframe["demand_score"]
    ) / 100.0

    # --------------------------------------------------------
    # Market attractiveness
    # --------------------------------------------------------

    dataframe[
        "market_attractiveness"
    ] = (
        dataframe[
            "opportunity_score"
        ]
        * 0.7
        +
        dataframe[
            "demand_price_balance"
        ]
        * 0.2
        +
        dataframe[
            "market_momentum"
        ]
        * 0.1
    )

    # --------------------------------------------------------
    # Clamp scores
    # --------------------------------------------------------

    dataframe[
        "opportunity_score"
    ] = dataframe[
        "opportunity_score"
    ].clip(
        0,
        100,
    )

    dataframe[
        "market_attractiveness"
    ] = dataframe[
        "market_attractiveness"
    ].clip(
        0,
        100,
    )

    return dataframe


# ============================================================
# EXPLANATION
# ============================================================

def generate_explanation(
    row,
):

    factors = []

    if row["demand_score"] >= 75:

        factors.append(
            "strong predicted demand"
        )

    elif row["demand_score"] >= 50:

        factors.append(
            "moderate predicted demand"
        )

    else:

        factors.append(
            "low predicted demand"
        )

    if row["price_opportunity"] >= 75:

        factors.append(
            "strong price opportunity"
        )

    elif row["price_opportunity"] >= 50:

        factors.append(
            "moderate price opportunity"
        )

    else:

        factors.append(
            "limited price opportunity"
        )

    if row["market_growth"] >= 75:

        factors.append(
            "strong market growth"
        )

    elif row["market_growth"] >= 50:

        factors.append(
            "positive market growth"
        )

    if row["regional_fit"] >= 75:

        factors.append(
            "strong regional product fit"
        )

    if row["seasonality_score"] >= 75:

        factors.append(
            "favorable seasonal conditions"
        )

    if row["competition_score"] >= 75:

        factors.append(
            "high competitive pressure"
        )

    elif row["competition_score"] <= 40:

        factors.append(
            "relatively low competitive pressure"
        )

    return "; ".join(
        factors
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    from .dataset import (
        create_dataset,
    )

    print("=" * 70)
    print(
        "KALASETU - MARKET FEATURE ENGINEERING TEST"
    )
    print("=" * 70)

    dataframe = create_dataset()

    engineered = engineer_features(
        dataframe
    )

    print(
        f"\nOriginal columns : "
        f"{len(dataframe.columns)}"
    )

    print(
        f"Engineered columns : "
        f"{len(engineered.columns)}"
    )

    print(
        "\nGenerated features:"
    )

    for column in engineered.columns:

        if column not in dataframe.columns:

            print(
                f"  - {column}"
            )

    print(
        "\nFEATURE ENGINEERING TEST PASSED."
    )

    print("=" * 70)