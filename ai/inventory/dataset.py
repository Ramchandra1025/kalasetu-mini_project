from pathlib import Path

import pandas as pd

from .config import DATASET_PATH


REQUIRED_COLUMNS = [
    "inventory_id",
    "product_category",
    "material",
    "region",
    "current_stock",
    "minimum_stock",
    "maximum_stock",
    "average_daily_sales",
    "recent_daily_sales",
    "historical_demand",
    "demand_growth",
    "lead_time_days",
    "unit_price",
    "days_since_last_order",
    "stockout_count",
]


def load_dataset(path=DATASET_PATH):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Inventory dataset not found: {path}"
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
        raise ValueError("Inventory dataset is empty.")

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

    return True