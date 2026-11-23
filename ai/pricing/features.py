"""
KalaSetu - Fair Pricing AI
Feature Engineering

Creates meaningful derived features for price prediction.

The raw dataset contains:
    size_cm
    production_hours
    material_cost
    labor_cost
    demand_score
    complexity_score
    craft_category
    material
    region

This module creates additional economic/product features.
"""

import numpy as np
import pandas as pd

from .config import (
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
    TARGET_COLUMN,
)


# ============================================================
# NUMERIC SAFETY
# ============================================================

def ensure_numeric(dataframe):
    """
    Convert numerical columns to numeric values.
    Invalid values become NaN.
    """

    dataframe = dataframe.copy()

    for column in NUMERIC_FEATURES:

        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    return dataframe


# ============================================================
# COST FEATURES
# ============================================================

def add_cost_features(dataframe):
    """
    Create production-cost related features.
    """

    dataframe = dataframe.copy()

    # Total direct production cost
    dataframe["total_cost"] = (
        dataframe["material_cost"]
        + dataframe["labor_cost"]
    )

    # Labor cost per production hour
    dataframe["labor_cost_per_hour"] = (
        dataframe["labor_cost"]
        / dataframe["production_hours"].replace(
            0,
            np.nan,
        )
    )

    # Material cost per square/size unit
    dataframe["material_cost_per_size"] = (
        dataframe["material_cost"]
        / dataframe["size_cm"].replace(
            0,
            np.nan,
        )
    )

    return dataframe


# ============================================================
# PRODUCTION FEATURES
# ============================================================

def add_production_features(dataframe):
    """
    Create production efficiency and complexity features.
    """

    dataframe = dataframe.copy()

    # Production time relative to product size
    dataframe["hours_per_size"] = (
        dataframe["production_hours"]
        / dataframe["size_cm"].replace(
            0,
            np.nan,
        )
    )

    # Combined production complexity
    dataframe["production_complexity"] = (
        dataframe["complexity_score"]
        * dataframe["production_hours"]
    )

    return dataframe


# ============================================================
# DEMAND FEATURES
# ============================================================

def add_demand_features(dataframe):
    """
    Create demand-related features.
    """

    dataframe = dataframe.copy()

    # Normalize demand to 0-1
    dataframe["demand_normalized"] = (
        dataframe["demand_score"]
        / 100.0
    )

    # Interaction between demand and complexity
    dataframe["demand_complexity"] = (
        dataframe["demand_score"]
        * dataframe["complexity_score"]
        / 100.0
    )

    return dataframe


# ============================================================
# SIZE FEATURES
# ============================================================

def add_size_features(dataframe):
    """
    Create size-related features.
    """

    dataframe = dataframe.copy()

    # Log transform reduces extreme size effects
    dataframe["log_size"] = np.log1p(
        dataframe["size_cm"]
    )

    return dataframe


# ============================================================
# PRICE BASELINE FEATURES
# ============================================================

def add_cost_ratio_features(dataframe):
    """
    Create relationships between production costs.
    """

    dataframe = dataframe.copy()

    dataframe["labor_material_ratio"] = (
        dataframe["labor_cost"]
        / dataframe["material_cost"].replace(
            0,
            np.nan,
        )
    )

    dataframe["labor_cost_ratio"] = (
        dataframe["labor_cost"]
        / dataframe["total_cost"].replace(
            0,
            np.nan,
        )
    )

    dataframe["material_cost_ratio"] = (
        dataframe["material_cost"]
        / dataframe["total_cost"].replace(
            0,
            np.nan,
        )
    )

    return dataframe


# ============================================================
# COMPLETE FEATURE ENGINEERING
# ============================================================

def engineer_features(dataframe):
    """
    Apply all feature-engineering transformations.
    """

    dataframe = dataframe.copy()

    dataframe = ensure_numeric(
        dataframe
    )

    dataframe = add_cost_features(
        dataframe
    )

    dataframe = add_production_features(
        dataframe
    )

    dataframe = add_demand_features(
        dataframe
    )

    dataframe = add_size_features(
        dataframe
    )

    dataframe = add_cost_ratio_features(
        dataframe
    )

    # Replace infinite values generated by divisions
    dataframe = dataframe.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    # Fill derived numeric missing values
    derived_numeric_columns = [
        "total_cost",
        "labor_cost_per_hour",
        "material_cost_per_size",
        "hours_per_size",
        "production_complexity",
        "demand_normalized",
        "demand_complexity",
        "log_size",
        "labor_material_ratio",
        "labor_cost_ratio",
        "material_cost_ratio",
    ]

    for column in derived_numeric_columns:

        if column in dataframe.columns:

            dataframe[column] = dataframe[
                column
            ].fillna(0.0)

    return dataframe


# ============================================================
# GET ENGINEERED NUMERIC FEATURES
# ============================================================

def get_engineered_numeric_features():
    """
    Return names of all numeric features after engineering.
    """

    engineered_features = [
        "size_cm",
        "production_hours",
        "material_cost",
        "labor_cost",
        "demand_score",
        "complexity_score",
        "total_cost",
        "labor_cost_per_hour",
        "material_cost_per_size",
        "hours_per_size",
        "production_complexity",
        "demand_normalized",
        "demand_complexity",
        "log_size",
        "labor_material_ratio",
        "labor_cost_ratio",
        "material_cost_ratio",
    ]

    return engineered_features


# ============================================================
# FEATURE SUMMARY
# ============================================================

def get_feature_summary(dataframe):
    """
    Return a summary of the engineered feature set.
    """

    numeric_features = (
        get_engineered_numeric_features()
    )

    categorical_features = [
        column
        for column in CATEGORICAL_FEATURES
        if column in dataframe.columns
    ]

    return {
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "target": TARGET_COLUMN,
        "total_numeric_features": len(
            numeric_features
        ),
        "total_categorical_features": len(
            categorical_features
        ),
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    from .dataset import load_dataset, validate_columns, clean_dataset

    print("=" * 60)
    print("KALASETU - FAIR PRICING FEATURE ENGINEERING")
    print("=" * 60)

    try:

        # Load dataset
        dataframe = load_dataset()

        # Validate
        validate_columns(
            dataframe
        )

        # Clean
        dataframe = clean_dataset(
            dataframe
        )

        # Engineer
        engineered = engineer_features(
            dataframe
        )

        print(
            f"\nOriginal columns : "
            f"{len(dataframe.columns)}"
        )

        print(
            f"Engineered columns : "
            f"{len(engineered.columns)}"
        )

        print("\nEngineered Numeric Features:")

        for feature in get_engineered_numeric_features():

            print(
                f"  - {feature}"
            )

        summary = get_feature_summary(
            engineered
        )

        print("\nFeature Summary:")

        print(
            f"  Numeric Features     : "
            f"{summary['total_numeric_features']}"
        )

        print(
            f"  Categorical Features : "
            f"{summary['total_categorical_features']}"
        )

        print(
            f"  Target               : "
            f"{summary['target']}"
        )

        print("\n" + "=" * 60)
        print("FEATURE ENGINEERING TEST PASSED")
        print("=" * 60)

    except Exception as error:

        print("\n" + "=" * 60)
        print("FEATURE ENGINEERING TEST FAILED")
        print("=" * 60)

        print(
            f"\nError: {error}"
        )