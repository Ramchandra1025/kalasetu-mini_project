import numpy as np
import pandas as pd


CATEGORICAL_COLUMNS = [
    "product_category",
    "material",
    "region",
]

NUMERIC_COLUMNS = [
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


def create_inventory_features(df):
    data = df.copy()

    # -----------------------------------------------------
    # BASIC DEMAND FEATURES
    # -----------------------------------------------------

    data["sales_momentum"] = (
        data["recent_daily_sales"]
        - data["average_daily_sales"]
    )

    data["sales_ratio"] = (
        data["recent_daily_sales"]
        / data["average_daily_sales"].replace(0, 1)
    )

    data["positive_demand_growth"] = (
        data["demand_growth"] > 0
    ).astype(int)

    # -----------------------------------------------------
    # STOCK COVERAGE
    # -----------------------------------------------------

    data["stock_coverage_days"] = (
        data["current_stock"]
        / data["recent_daily_sales"].replace(0, 0.1)
    )

    # -----------------------------------------------------
    # STOCK RATIO
    # -----------------------------------------------------

    data["minimum_stock_ratio"] = (
        data["current_stock"]
        / data["minimum_stock"].replace(0, 1)
    )

    data["maximum_stock_ratio"] = (
        data["current_stock"]
        / data["maximum_stock"].replace(0, 1)
    )

    # -----------------------------------------------------
    # LEAD TIME DEMAND
    # -----------------------------------------------------

    data["lead_time_demand"] = (
        data["recent_daily_sales"]
        * data["lead_time_days"]
    )

    # -----------------------------------------------------
    # SAFETY STOCK
    # -----------------------------------------------------

    data["safety_stock"] = (
        data["recent_daily_sales"] * 3
    )

    # -----------------------------------------------------
    # REORDER POINT
    # -----------------------------------------------------

    data["reorder_point"] = (
        data["lead_time_demand"]
        + data["safety_stock"]
    )

    # -----------------------------------------------------
    # INVENTORY GAP
    # -----------------------------------------------------

    data["inventory_gap"] = (
        data["reorder_point"]
        - data["current_stock"]
    )

    # -----------------------------------------------------
    # DEMAND PRESSURE
    # -----------------------------------------------------

    data["demand_pressure"] = (
        data["recent_daily_sales"]
        + data["historical_demand"] * 0.01
    )

    # -----------------------------------------------------
    # STOCKOUT PRESSURE
    # -----------------------------------------------------

    data["stockout_pressure"] = (
        data["stockout_count"]
        + data["days_since_last_order"] * 0.05
    )

    # Replace invalid values

    data = data.replace(
        [np.inf, -np.inf],
        np.nan
    )

    data = data.fillna(0)

    return data


def get_feature_columns():
    return (
        CATEGORICAL_COLUMNS
        + NUMERIC_COLUMNS
        + [
            "sales_momentum",
            "sales_ratio",
            "positive_demand_growth",
            "stock_coverage_days",
            "minimum_stock_ratio",
            "maximum_stock_ratio",
            "lead_time_demand",
            "safety_stock",
            "reorder_point",
            "inventory_gap",
            "demand_pressure",
            "stockout_pressure",
        ]
    )


def encode_features(df):
    features = create_inventory_features(df)

    categorical = pd.get_dummies(
        features[CATEGORICAL_COLUMNS],
        prefix=CATEGORICAL_COLUMNS,
        dtype=int,
    )

    numeric_columns = [
        column
        for column in get_feature_columns()
        if column not in CATEGORICAL_COLUMNS
    ]

    numeric = features[numeric_columns].copy()

    result = pd.concat(
        [categorical, numeric],
        axis=1,
    )

    return result