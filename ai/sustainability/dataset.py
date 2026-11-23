from pathlib import Path

import pandas as pd

from .config import DATASET_PATH


REQUIRED_COLUMNS = [
    "product_id",
    "product_category",
    "material",
    "material_weight_kg",
    "production_energy_kwh",
    "waste_kg",
    "packaging_type",
    "transport_distance_km",
    "recyclability",
    "local_sourcing",
]


def load_dataset(path=DATASET_PATH):

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Sustainability dataset not found: {path}"
        )

    df = pd.read_csv(path)

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    if df.empty:
        raise ValueError(
            "Sustainability dataset is empty."
        )

    return df


def validate_dataset(df):

    if df.empty:
        raise ValueError(
            "Dataset is empty."
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

    numeric_columns = [
        "material_weight_kg",
        "production_energy_kwh",
        "waste_kg",
        "transport_distance_km",
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

    return True