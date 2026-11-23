from pathlib import Path

import pandas as pd

from .config import (
    DATASET_PATH,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
)


REQUIRED_COLUMNS = (
    CATEGORICAL_FEATURES
    + NUMERICAL_FEATURES
)


def load_dataset(
    path: str | Path = DATASET_PATH,
) -> pd.DataFrame:

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    df = pd.read_csv(path)

    return df


def validate_dataset(
    df: pd.DataFrame,
) -> dict:

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    invalid_rows = int(
        df[REQUIRED_COLUMNS]
        .isnull()
        .any(axis=1)
        .sum()
    )

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_columns": missing_columns,
        "invalid_rows": invalid_rows,
        "valid": (
            len(missing_columns) == 0
            and invalid_rows == 0
        ),
    }


def prepare_dataset(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    for column in NUMERICAL_FEATURES:
        result[column] = pd.to_numeric(
            result[column],
            errors="coerce",
        )

    for column in CATEGORICAL_FEATURES:
        result[column] = (
            result[column]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    result = result.dropna(
        subset=REQUIRED_COLUMNS
    )

    return result.reset_index(drop=True)


if __name__ == "__main__":

    data = load_dataset()

    print("Dataset loaded successfully.")
    print(
        f"Rows: {len(data)}"
    )
    print(
        f"Columns: {len(data.columns)}"
    )

    validation = validate_dataset(data)

    print(
        f"Valid: {validation['valid']}"
    )
    print(
        f"Invalid rows: {validation['invalid_rows']}"
    )