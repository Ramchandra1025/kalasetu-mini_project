"""
KalaSetu - Buyer Matching & Recommendation AI
Feature Engineering
"""

import pandas as pd

from .config import WEIGHTS


# ============================================================
# CATEGORY MATCH
# ============================================================

def category_match(
    buyer_category,
    product_category,
):

    if (
        buyer_category.lower()
        == product_category.lower()
    ):

        return 100.0

    return 0.0


# ============================================================
# MATERIAL MATCH
# ============================================================

def material_match(
    buyer_material,
    product_material,
):

    if (
        buyer_material.lower()
        == product_material.lower()
    ):

        return 100.0

    return 0.0


# ============================================================
# BUDGET MATCH
# ============================================================

def budget_match(
    minimum_budget,
    maximum_budget,
    product_price,
):

    if (
        minimum_budget
        <= product_price
        <= maximum_budget
    ):

        return 100.0

    # Product slightly above budget

    if product_price > maximum_budget:

        difference = (
            product_price
            - maximum_budget
        )

        percentage = (
            difference
            / max(
                maximum_budget,
                1,
            )
        ) * 100

        return max(
            0.0,
            100.0 - percentage,
        )

    # Product below budget

    difference = (
        minimum_budget
        - product_price
    )

    percentage = (
        difference
        / max(
            minimum_budget,
            1,
        )
    ) * 100

    return max(
        0.0,
        100.0 - percentage,
    )


# ============================================================
# LOCATION MATCH
# ============================================================

def location_match(
    buyer_region,
    product_region,
):

    if (
        buyer_region.lower()
        == product_region.lower()
    ):

        return 100.0

    return 50.0


# ============================================================
# HISTORY MATCH
# ============================================================

def history_match(
    previous_category,
    previous_material,
    product_category,
    product_material,
):

    category_score = category_match(
        previous_category,
        product_category,
    )

    material_score = material_match(
        previous_material,
        product_material,
    )

    return (
        category_score * 0.6
        +
        material_score * 0.4
    )


# ============================================================
# PRODUCT FIT
# ============================================================

def product_fit(
    demand_score,
):

    return max(
        0.0,
        min(
            100.0,
            float(demand_score),
        ),
    )


# ============================================================
# CALCULATE FEATURES
# ============================================================

def calculate_matching_features(
    row,
):

    features = {

        "category_match":
            category_match(
                row[
                    "preferred_category"
                ],
                row[
                    "product_category"
                ],
            ),

        "material_match":
            material_match(
                row[
                    "preferred_material"
                ],
                row[
                    "product_material"
                ],
            ),

        "budget_match":
            budget_match(
                row[
                    "min_budget"
                ],
                row[
                    "max_budget"
                ],
                row[
                    "product_price"
                ],
            ),

        "location_match":
            location_match(
                row[
                    "buyer_region"
                ],
                row[
                    "product_region"
                ],
            ),

        "history_match":
            history_match(
                row[
                    "previous_category"
                ],
                row[
                    "previous_material"
                ],
                row[
                    "product_category"
                ],
                row[
                    "product_material"
                ],
            ),

        "demand_relevance":
            product_fit(
                row[
                    "product_demand_score"
                ],
            ),

        "product_fit":
            product_fit(
                row[
                    "product_demand_score"
                ],
            ),
    }

    return features


# ============================================================
# WEIGHTED SCORE
# ============================================================

def calculate_weighted_score(
    features,
):

    score = 0.0

    for feature, weight in (
        WEIGHTS.items()
    ):

        score += (
            features[feature]
            * weight
        )

    return max(
        0.0,
        min(
            100.0,
            score,
        ),
    )


# ============================================================
# DATAFRAME FEATURE ENGINEERING
# ============================================================

def engineer_features(
    dataframe,
):

    dataframe = dataframe.copy()

    feature_rows = []

    for _, row in dataframe.iterrows():

        features = (
            calculate_matching_features(
                row
            )
        )

        features[
            "match_score"
        ] = calculate_weighted_score(
            features
        )

        feature_rows.append(
            features
        )

    feature_dataframe = pd.DataFrame(
        feature_rows
    )

    return pd.concat(
        [
            dataframe.reset_index(
                drop=True
            ),
            feature_dataframe,
        ],
        axis=1,
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
        "KALASETU - RECOMMENDATION FEATURE TEST"
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
        "\nRECOMMENDATION FEATURE TEST PASSED."
    )

    print("=" * 70)