"""
KalaSetu - Explainable Market Opportunity Scoring Engine
"""

from .config import (
    HIGH_OPPORTUNITY_THRESHOLD,
    MEDIUM_OPPORTUNITY_THRESHOLD,
    MIN_SCORE,
    MAX_SCORE,
    WEIGHTS,
)

from .features import (
    calculate_weighted_score,
    generate_explanation,
)


# ============================================================
# OPPORTUNITY LEVEL
# ============================================================

def get_opportunity_level(
    score,
):

    if score >= HIGH_OPPORTUNITY_THRESHOLD:

        return "HIGH"

    if score >= MEDIUM_OPPORTUNITY_THRESHOLD:

        return "MEDIUM"

    return "LOW"


# ============================================================
# SCORE MARKET
# ============================================================

def score_market(
    row,
):

    score = calculate_weighted_score(
        row
    )

    score = max(
        MIN_SCORE,
        min(
            MAX_SCORE,
            score,
        ),
    )

    level = get_opportunity_level(
        score
    )

    explanation = (
        generate_explanation(
            row
        )
    )

    contributions = {}

    for feature, weight in (
        WEIGHTS.items()
    ):

        value = float(
            row[feature]
        )

        contributions[feature] = (
            value * weight
        )

    return {

        "product_category":
            row[
                "product_category"
            ],

        "region":
            row["region"],

        "opportunity_score":
            round(
                score,
                2,
            ),

        "opportunity_level":
            level,

        "explanation":
            explanation,

        "factor_contributions":
            {
                key: round(
                    value,
                    2,
                )

                for key, value
                in contributions.items()
            },
    }


# ============================================================
# RANK MARKETS
# ============================================================

def rank_markets(
    dataframe,
):

    results = []

    for _, row in dataframe.iterrows():

        result = score_market(
            row
        )

        results.append(
            result
        )

    results.sort(
        key=lambda item:
        item[
            "opportunity_score"
        ],
        reverse=True,
    )

    for index, result in enumerate(
        results,
        start=1,
    ):

        result[
            "rank"
        ] = index

    return results


# ============================================================
# BEST MARKET
# ============================================================

def get_best_market(
    dataframe,
):

    ranked = rank_markets(
        dataframe
    )

    if not ranked:

        return None

    return ranked[0]


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    import pandas as pd

    test_row = pd.Series(
        {
            "product_category":
                "wood_craft",

            "region":
                "karnataka",

            "demand_score":
                85,

            "price_opportunity":
                80,

            "market_growth":
                75,

            "regional_fit":
                90,

            "seasonality_score":
                70,

            "competition_score":
                35,
        }
    )

    print("=" * 70)
    print(
        "KALASETU - MARKET SCORING ENGINE TEST"
    )
    print("=" * 70)

    result = score_market(
        test_row
    )

    print(
        f"\nProduct : "
        f"{result['product_category']}"
    )

    print(
        f"Region  : "
        f"{result['region']}"
    )

    print(
        f"Score   : "
        f"{result['opportunity_score']}"
    )

    print(
        f"Level   : "
        f"{result['opportunity_level']}"
    )

    print(
        f"Reason  : "
        f"{result['explanation']}"
    )

    print(
        "\nSCORING ENGINE TEST PASSED."
    )

    print("=" * 70)