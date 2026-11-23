from pathlib import Path

import pandas as pd

from .config import DATASET_PATH


REQUIRED_COLUMNS = [
    "product_id",
    "product_name",
    "artisan_id",
    "artisan_name",
    "craft_category",
    "material",
    "origin_state",
    "origin_district",
    "production_method",
    "material_source",
    "sustainability_score",
    "carbon_impact_kg_co2e",
]


def load_dataset(path=DATASET_PATH):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"DPP dataset not found: {path}"
        )

    df = pd.read_csv(path)

    if df.empty:
        raise ValueError(
            "DPP dataset is empty."
        )

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    return df


def validate_dataset(df):
    if df.empty:
        raise ValueError("Dataset is empty.")

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    numeric_columns = [
        "sustainability_score",
        "carbon_impact_kg_co2e",
    ]

    for column in numeric_columns:
        if df[column].isnull().any():
            raise ValueError(
                f"{column} contains missing values."
            )

        if (df[column] < 0).any():
            raise ValueError(
                f"{column} cannot contain negative values."
            )

    if ((df["sustainability_score"] < 0) |
        (df["sustainability_score"] > 100)).any():
        raise ValueError(
            "Sustainability score must be between 0 and 100."
        )

    return True