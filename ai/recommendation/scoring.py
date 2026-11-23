"""
KalaSetu - Hybrid Buyer Matching Engine
Scoring and Ranking
"""

from .config import (
    HIGH_MATCH_THRESHOLD,
    MEDIUM_MATCH_THRESHOLD,
    WEIGHTS,
)

from .features import (
    calculate_matching_features,
    calculate_weighted_score,
)


# ============================================================
# MATCH LEVEL
# ============================================================

def get_match_level(
    score,
):

    if score >= HIGH_MATCH_THRESHOLD:

        return "HIGH"

    if score >= MEDIUM_MATCH_THRESHOLD:

        return "MEDIUM"

    return "LOW"


# ============================================================
# EXPLANATION
# ============================================================

def generate_explanation(
    features,
):

    reasons = []

    if features[
        "category_match"
    ] >= 100:

        reasons.append(
            "preferred category matches"
        )

    if features[
        "material_match"
    ] >= 100:

        reasons.append(
            "preferred material matches"
        )

    if features[
        "budget_match"
    ] >= 90:

        reasons.append(
            "product fits buyer budget"
        )

    elif features[
        "budget_match"
    ] >= 70:

        reasons.append(
            "product is close to buyer budget"
        )

    if features[
        "location_match"
    ] >= 100:

        reasons.append(
            "same region"
        )

    if features[
        "history_match"
    ] >= 80:

        reasons.append(
            "similar to previous purchases"
        )

    if features[
        "demand_relevance"
    ] >= 75:

        reasons.append(
            "high-demand product"
        )

    if not reasons:

        reasons.append(
            "partial preference compatibility"
        )

    return "; ".join(
        reasons
    )


# ============================================================
# SCORE BUYER-PRODUCT PAIR
# ============================================================

def score_buyer_product(
    row,
):

    features = (
        calculate_matching_features(
            row
        )
    )

    score = calculate_weighted_score(
        features
    )

    result = {

        "buyer_id":
            row["buyer_id"],

        "product_category":
            row[
                "product_category"
            ],

        "product_material":
            row[
                "product_material"
            ],

        "product_price":
            float(
                row["product_price"]
            ),

        "product_region":
            row[
                "product_region"
            ],

        "match_score":
            round(
                score,
                2,
            ),

        "match_level":
            get_match_level(
                score
            ),

        "explanation":
            generate_explanation(
                features
            ),

        "factor_contributions":
            {
                feature:
                    round(
                        features[
                            feature
                        ] * weight,
                        2,
                    )

                for feature, weight
                in WEIGHTS.items()
            },
    }

    return result


# ============================================================
# RANK PRODUCTS FOR BUYER
# ============================================================

def rank_products_for_buyer(
    dataframe,
    buyer_id,
):

    buyer_dataframe = dataframe[
        dataframe["buyer_id"]
        == buyer_id
    ]

    if buyer_dataframe.empty:

        return []

    results = []

    for _, row in (
        buyer_dataframe.iterrows()
    ):

        results.append(
            score_buyer_product(
                row
            )
        )

    results.sort(
        key=lambda item:
        item["match_score"],
        reverse=True,
    )

    for rank, result in enumerate(
        results,
        start=1,
    ):

        result[
            "rank"
        ] = rank

    return results


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    import pandas as pd

    print("=" * 70)

    print(
        "KALASETU - BUYER MATCHING ENGINE TEST"
    )

    print("=" * 70)

    test_row = pd.Series(
        {

            "buyer_id":
                "buyer_001",

            "buyer_region":
                "karnataka",

            "preferred_category":
                "wood_craft",

            "preferred_material":
                "wood",

            "min_budget":
                2000,

            "max_budget":
                5000,

            "previous_category":
                "wood_craft",

            "previous_material":
                "wood",

            "product_category":
                "wood_craft",

            "product_material":
                "wood",

            "product_price":
                3200,

            "product_region":
                "karnataka",

            "product_demand_score":
                82,
        }
    )

    result = score_buyer_product(
        test_row
    )

    print(
        f"\nBuyer        : "
        f"{result['buyer_id']}"
    )

    print(
        f"Product      : "
        f"{result['product_category']}"
    )

    print(
        f"Match Score  : "
        f"{result['match_score']}"
    )

    print(
        f"Match Level  : "
        f"{result['match_level']}"
    )

    print(
        f"Explanation  : "
        f"{result['explanation']}"
    )

    print(
        "\nFactor Contributions:"
    )

    for key, value in (
        result[
            "factor_contributions"
        ].items()
    ):

        print(
            f"  {key:<22}: "
            f"{value:.2f}"
        )

    print(
        "\nBUYER MATCHING ENGINE TEST PASSED."
    )

    print("=" * 70)