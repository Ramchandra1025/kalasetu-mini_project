from pathlib import Path

import pandas as pd

from .config import DATASET_PATH


REQUIRED_COLUMNS = [
    "order_id",
    "artisan_id",
    "buyer_region",
    "latitude",
    "longitude",
    "package_weight",
    "priority",
    "delivery_status",
]


def load_dataset(path=DATASET_PATH):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Logistics dataset not found: {path}"
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
        raise ValueError("Logistics dataset is empty.")

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

    if df["latitude"].isnull().any():
        raise ValueError("Latitude contains missing values.")

    if df["longitude"].isnull().any():
        raise ValueError("Longitude contains missing values.")

    if (df["package_weight"] <= 0).any():
        raise ValueError(
            "Package weight must be greater than zero."
        )

    return True