"""
KalaSetu - Market Opportunity Intelligence
Dataset Loading and Validation
"""

import pandas as pd

from .config import (
    DATASET_FILE,
    FEATURE_COLUMNS,
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
    TARGET_COLUMN,
)


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    if not DATASET_FILE.exists():

        raise FileNotFoundError(
            f"Market dataset not found:\n"
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
# VALIDATE COLUMNS
# ============================================================

def validate_columns(
    dataframe,
):

    required_columns = (
        FEATURE_COLUMNS
        + [TARGET_COLUMN]
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing required columns:\n"
            + "\n".join(
                f"  - {column}"
                for column in missing_columns
            )
        )

    print(
        "Required columns validated."
    )


# ============================================================
# CLEAN DATA
# ============================================================

def clean_dataset(
    dataframe,
):

    dataframe = dataframe.copy()

    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

    for column in (
        NUMERIC_FEATURES
        + [TARGET_COLUMN]
    ):

        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    # --------------------------------------------------------
    # Categorical columns
    # --------------------------------------------------------

    for column in CATEGORICAL_FEATURES:

        dataframe[column] = (
            dataframe[column]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    before_count = len(
        dataframe
    )

    # --------------------------------------------------------
    # Remove missing rows
    # --------------------------------------------------------

    dataframe = dataframe.dropna(
        subset=(
            FEATURE_COLUMNS
            + [TARGET_COLUMN]
        )
    )

    # --------------------------------------------------------
    # Scores must be 0-100
    # --------------------------------------------------------

    for column in NUMERIC_FEATURES:

        dataframe = dataframe[
            dataframe[column].between(
                0,
                100,
            )
        ]

    # --------------------------------------------------------
    # Target must be 0-100
    # --------------------------------------------------------

    dataframe = dataframe[
        dataframe[TARGET_COLUMN].between(
            0,
            100,
        )
    ]

    after_count = len(
        dataframe
    )

    print(
        f"Removed invalid rows: "
        f"{before_count - after_count}"
    )

    print(
        f"Clean dataset size: "
        f"{after_count} rows"
    )

    return dataframe.reset_index(
        drop=True
    )


# ============================================================
# COMPLETE DATASET PIPELINE
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
            "Market dataset must contain "
            "at least 10 valid rows."
        )

    return dataframe


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print(
        "KALASETU - MARKET DATASET TEST"
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