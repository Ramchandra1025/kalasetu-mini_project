from pathlib import Path

import pandas as pd

from .config import (
    DATASET_FILE,
    TEST_IMAGE_DIR,
)


REQUIRED_COLUMNS = [
    "image_id",
    "image_path",
    "expected_text",
    "category",
]


def load_dataset(path=DATASET_FILE):
    """
    Load OCR dataset.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    df = pd.read_csv(path)

    validate_dataset(df)

    return df


def validate_dataset(df):
    """
    Validate required dataset columns.
    """
    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing dataset columns: {missing}"
        )

    if df.empty:
        raise ValueError(
            "OCR dataset is empty."
        )

    return True


def prepare_dataset(df):
    """
    Clean OCR dataset.
    """
    df = df.copy()

    for column in [
        "image_id",
        "image_path",
        "expected_text",
        "category",
    ]:
        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    df = df[df["image_path"] != ""]
    df = df[df["expected_text"] != ""]

    return df.reset_index(drop=True)


def resolve_image_path(image_path):
    """
    Resolve dataset-relative image paths.
    """
    path = Path(image_path)

    if path.is_absolute():
        return path

    return TEST_IMAGE_DIR / path