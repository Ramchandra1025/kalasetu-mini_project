"""
KalaSetu - Buyer Matching & Recommendation AI
Dataset Pipeline
"""

import pandas as pd

from .config import (
    DATASET_FILE,
    INPUT_COLUMNS,
    TARGET_COLUMN,
)


# ============================================================
# LOAD
# ============================================================

def load_dataset():

    if not DATASET_FILE.exists():

        raise FileNotFoundError(
            f"Recommendation dataset not found:\n"
            f"{DATASET_FILE}"
        )

    dataframe = pd.read_csv(
        DATASET_FILE
    )

    print(
        f"Dataset loaded: "
        f"{len(dataframe)} rows"
    )

    return dataframe


# ============================================================
# VALIDATE
# ============================================================

def validate_columns(
    dataframe,
):

    required = (
        INPUT_COLUMNS
        + [TARGET_COLUMN]
    )

    missing = [
        column

        for column in required

        if column not in dataframe.columns
    ]

    if missing:

        raise ValueError(
            "Missing required columns:\n"
            + "\n".join(
                f"  - {column}"
                for column in missing
            )
        )

    print(
        "Required columns validated."
    )


# ============================================================
# CLEAN
# ============================================================

def clean_dataset(
    dataframe,
):

    dataframe = dataframe.copy()

    categorical_columns = [

        "buyer_id",
        "buyer_region",
        "preferred_category",
        "preferred_material",
        "previous_category",
        "previous_material",
        "product_category",
        "product_material",
        "product_region",
    ]

    numeric_columns = [

        "min_budget",
        "max_budget",
        "product_price",
        "product_demand_score",
        TARGET_COLUMN,
    ]

    # --------------------------------------------------------
    # Categorical normalization
    # --------------------------------------------------------

    for column in categorical_columns:

        dataframe[column] = (
            dataframe[column]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    # --------------------------------------------------------
    # Numeric conversion
    # --------------------------------------------------------

    for column in numeric_columns:

        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    before = len(
        dataframe
    )

    dataframe = dataframe.dropna(
        subset=(
            INPUT_COLUMNS
            + [TARGET_COLUMN]
        )
    )

    # --------------------------------------------------------
    # Budget validation
    # --------------------------------------------------------

    dataframe = dataframe[
        dataframe["min_budget"] >= 0
    ]

    dataframe = dataframe[
        dataframe["max_budget"]
        >= dataframe["min_budget"]
    ]

    dataframe = dataframe[
        dataframe["product_price"] >= 0
    ]

    # --------------------------------------------------------
    # Score validation
    # --------------------------------------------------------

    dataframe = dataframe[
        dataframe["product_demand_score"]
        .between(0, 100)
    ]

    dataframe = dataframe[
        dataframe[TARGET_COLUMN]
        .between(0, 100)
    ]

    after = len(
        dataframe
    )

    print(
        f"Removed invalid rows: "
        f"{before - after}"
    )

    print(
        f"Clean dataset size: "
        f"{after} rows"
    )

    return dataframe.reset_index(
        drop=True
    )


# ============================================================
# PIPELINE
# ============================================================

def create_dataset():

    dataframe = load_dataset()

    validate_columns(
        dataframe
    )

    dataframe = clean_dataset(
        dataframe
    )

    if len(dataframe) < 10:

        raise ValueError(
            "Recommendation dataset must "
            "contain at least 10 valid rows."
        )

    return dataframe


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)

    print(
        "KALASETU - RECOMMENDATION DATASET TEST"
    )

    print("=" * 70)

    dataframe = create_dataset()

    print(
        "\nDataset shape:"
    )

    print(
        dataframe.shape
    )

    print(
        "\nColumns:"
    )

    for column in dataframe.columns:

        print(
            f"  - {column}"
        )

    print(
        "\nDATASET PIPELINE TEST PASSED."
    )

    print("=" * 70)