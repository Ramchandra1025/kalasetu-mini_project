"""Leakage-safe dataset loading, cleaning, feature engineering and splitting."""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from .config import (
    DATASET_FILE, NUMERIC_FEATURES, CATEGORICAL_FEATURES,
    TARGET_COLUMN, TRAIN_RATIO, VALIDATION_RATIO, TEST_RATIO,
    RANDOM_SEED, MODEL_FEATURES,
)
from .features import engineer_features

REQUIRED_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET_COLUMN]


def load_dataset():
    if not DATASET_FILE.exists():
        raise FileNotFoundError(f"Pricing dataset not found: {DATASET_FILE}")
    return pd.read_csv(DATASET_FILE)


def validate_columns(dataframe):
    missing = [column for column in REQUIRED_COLUMNS if column not in dataframe.columns]
    if missing:
        raise ValueError("Missing required pricing columns: " + ", ".join(missing))


def clean_dataset(dataframe):
    """Clean records without learning any statistics from validation/test rows."""
    dataframe = dataframe.copy().dropna(how="all")

    for column in NUMERIC_FEATURES + [TARGET_COLUMN]:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")

    for column in CATEGORICAL_FEATURES:
        dataframe[column] = (
            dataframe[column].astype("string").str.strip().str.lower()
            .replace({"": pd.NA, "nan": pd.NA, "none": pd.NA})
        )

    dataframe = dataframe.dropna(subset=REQUIRED_COLUMNS)
    dataframe = dataframe[
        (dataframe["size_cm"] > 0)
        & (dataframe["production_hours"] > 0)
        & (dataframe["material_cost"] >= 0)
        & (dataframe["labor_cost"] >= 0)
        & dataframe["demand_score"].between(0, 100)
        & dataframe["complexity_score"].between(0, 100)
        & (dataframe[TARGET_COLUMN] > 0)
    ].copy()

    dataframe[NUMERIC_FEATURES + [TARGET_COLUMN]] = (
        dataframe[NUMERIC_FEATURES + [TARGET_COLUMN]].replace([np.inf, -np.inf], np.nan)
    )
    dataframe = dataframe.dropna(subset=REQUIRED_COLUMNS).reset_index(drop=True)
    return dataframe


def split_dataframe(dataframe):
    """Split raw rows first; preprocessing/model fitting happens after this point."""
    if len(dataframe) < 10:
        raise ValueError(
            f"Only {len(dataframe)} valid rows remain. At least 10 are required "
            "for a pipeline smoke test; substantially more are needed for research."
        )

    date_column = next((name for name in ("quote_date", "created_at", "date") if name in dataframe.columns), None)
    if date_column:
        ordered = dataframe.copy()
        ordered[date_column] = pd.to_datetime(ordered[date_column], errors="coerce")
        ordered = ordered.dropna(subset=[date_column]).sort_values(date_column).reset_index(drop=True)
        if ordered[date_column].nunique() < 3:
            raise ValueError("At least three distinct dates are required for chronological pricing evaluation.")
        train_end = int(len(ordered) * TRAIN_RATIO)
        validation_end = int(len(ordered) * (TRAIN_RATIO + VALIDATION_RATIO))
        if train_end < 1 or validation_end <= train_end or validation_end >= len(ordered):
            raise ValueError("Not enough dated quote rows for chronological train/validation/test partitions.")
        train_df = ordered.iloc[:train_end].copy()
        validation_df = ordered.iloc[train_end:validation_end].copy()
        test_df = ordered.iloc[validation_end:].copy()
    else:
        # Legacy synthetic-data fallback only; final pricing research needs dated quotes.
        train_df, temporary_df = train_test_split(
            dataframe, test_size=VALIDATION_RATIO + TEST_RATIO,
            random_state=RANDOM_SEED,
        )
        test_fraction = TEST_RATIO / (VALIDATION_RATIO + TEST_RATIO)
        validation_df, test_df = train_test_split(
            temporary_df, test_size=test_fraction, random_state=RANDOM_SEED,
        )
    return (
        train_df.reset_index(drop=True),
        validation_df.reset_index(drop=True),
        test_df.reset_index(drop=True),
    )


def _model_frame(frame):
    engineered = engineer_features(frame)
    # Select in a fixed, explicit order; never include the target in model inputs.
    return engineered[MODEL_FEATURES].copy()


def create_datasets():
    dataframe = load_dataset()
    validate_columns(dataframe)
    dataframe = clean_dataset(dataframe)
    train_df, validation_df, test_df = split_dataframe(dataframe)

    X_train = _model_frame(train_df)
    X_validation = _model_frame(validation_df)
    X_test = _model_frame(test_df)

    return {
        "X_train": X_train,
        "X_validation": X_validation,
        "X_test": X_test,
        "y_train": train_df[TARGET_COLUMN].astype(float).to_numpy(),
        "y_validation": validation_df[TARGET_COLUMN].astype(float).to_numpy(),
        "y_test": test_df[TARGET_COLUMN].astype(float).to_numpy(),
        "train_dataframe": train_df,
        "validation_dataframe": validation_df,
        "test_dataframe": test_df,
        "dataframe": dataframe,
        "feature_names": MODEL_FEATURES,
        "data_type": "synthetic_pipeline_testing_data",
        "research_valid": False,
    }


if __name__ == "__main__":
    data = create_datasets()
    print("Pricing dataset pipeline check")
    for key in ("X_train", "X_validation", "X_test"):
        print(f"{key}: {data[key].shape}")
    print("Feature preprocessing is performed inside each model pipeline.")
    print("Research-valid: False (current CSV is synthetic test data).")
