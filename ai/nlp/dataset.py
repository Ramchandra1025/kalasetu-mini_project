from pathlib import Path

import pandas as pd

from .config import DATASET_PATH


REQUIRED_COLUMNS = [
    "product_id",
    "product_category",
    "product_text",
]


def load_dataset(path: str | Path = DATASET_PATH):
    """
    Load NLP product text dataset.
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    return pd.read_csv(path)


def validate_dataset(df):
    """
    Validate required NLP dataset columns.
    """

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: "
            f"{missing_columns}"
        )

    if df.empty:
        raise ValueError(
            "Dataset is empty."
        )

    if df["product_text"].isna().any():
        raise ValueError(
            "Dataset contains missing product text."
        )

    return True


def prepare_dataset(df):
    """
    Clean product text data.
    """

    data = df.copy()

    data["product_text"] = (
        data["product_text"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    data["product_category"] = (
        data["product_category"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    data = data[
        data["product_text"].str.len() > 0
    ]

    data = data.reset_index(drop=True)

    return data


if __name__ == "__main__":

    df = load_dataset()

    validate_dataset(df)

    df = prepare_dataset(df)

    print(
        f"Dataset loaded successfully: "
        f"{len(df)} rows"
    )