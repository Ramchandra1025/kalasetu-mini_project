from pathlib import Path
import pandas as pd

from .config import DATASET_PATH


REQUIRED_COLUMNS = [
    "waste_id",
    "craft_category",
    "material",
    "waste_quantity_kg",
    "condition_score",
    "reuse_compatibility",
    "demand_score",
    "processing_effort",
    "disposal_cost",
    "expected_reuse_value",
]


def load_dataset(path: str | Path = DATASET_PATH) -> pd.DataFrame:

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Waste dataset not found: {path}"
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

    return df


def validate_dataset(df: pd.DataFrame) -> dict:

    result = {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values": int(
            df.isnull().sum().sum()
        ),
        "duplicate_rows": int(
            df.duplicated().sum()
        ),
        "invalid_quantity": int(
            (df["waste_quantity_kg"] <= 0).sum()
        ),
        "invalid_condition": int(
            (
                (df["condition_score"] < 0)
                | (df["condition_score"] > 100)
            ).sum()
        ),
        "invalid_compatibility": int(
            (
                (df["reuse_compatibility"] < 0)
                | (df["reuse_compatibility"] > 100)
            ).sum()
        ),
        "invalid_demand": int(
            (
                (df["demand_score"] < 0)
                | (df["demand_score"] > 100)
            ).sum()
        ),
        "invalid_processing": int(
            (
                (df["processing_effort"] < 0)
                | (df["processing_effort"] > 100)
            ).sum()
        ),
    }

    result["valid"] = all(
        value == 0
        for key, value in result.items()
        if key not in {"rows", "columns"}
    )

    return result