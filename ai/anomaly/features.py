import pandas as pd

from .config import (
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
)


def create_features(
    df: pd.DataFrame,
) -> pd.DataFrame:

    data = df.copy()

    # --------------------------------------------------------
    # Order frequency
    # --------------------------------------------------------

    data["order_frequency"] = (
        data["orders_last_7_days"] / 7.0
    )

    # --------------------------------------------------------
    # Cancellation risk
    # --------------------------------------------------------

    data["cancellation_risk"] = (
        data["cancellation_rate"] / 100.0
    )

    # --------------------------------------------------------
    # Price anomaly
    # --------------------------------------------------------

    data["price_anomaly"] = (
        data["price_deviation"].abs()
    )

    # --------------------------------------------------------
    # Quantity anomaly
    # --------------------------------------------------------

    data["quantity_anomaly"] = (
        data["quantity_deviation"].abs()
    )

    # --------------------------------------------------------
    # Transaction amount anomaly
    # --------------------------------------------------------

    data["amount_anomaly"] = (
        data["amount_deviation"].abs()
    )

    # --------------------------------------------------------
    # Account activity intensity
    # --------------------------------------------------------

    data["activity_intensity"] = (
        data["orders_last_30_days"]
        / (data["account_age_days"] + 1)
    )

    # --------------------------------------------------------
    # Repetition signal
    # --------------------------------------------------------

    data["repetition_signal"] = (
        data["repeated_buyer_count"]
        + data["repeated_artisan_count"]
    )

    # --------------------------------------------------------
    # High-risk composite signal
    # --------------------------------------------------------

    data["behavioral_risk_signal"] = (
        data["price_anomaly"] * 0.20
        + data["quantity_anomaly"] * 0.20
        + data["amount_anomaly"] * 0.20
        + data["cancellation_risk"] * 20.0
        + data["activity_intensity"] * 20.0
        + data["repetition_signal"] * 0.50
    )

    return data


def encode_features(
    df: pd.DataFrame,
) -> pd.DataFrame:

    data = df.copy()

    categorical_encoded = pd.get_dummies(
        data[CATEGORICAL_FEATURES],
        prefix=CATEGORICAL_FEATURES,
        dtype=float,
    )

    numerical_columns = [
        column
        for column in data.columns
        if column not in CATEGORICAL_FEATURES
        and column != "activity_id"
        and column != "is_anomaly"
    ]

    numerical_data = data[
        numerical_columns
    ].astype(float)

    result = pd.concat(
        [
            numerical_data.reset_index(drop=True),
            categorical_encoded.reset_index(drop=True),
        ],
        axis=1,
    )

    return result


def build_feature_matrix(
    df: pd.DataFrame,
) -> pd.DataFrame:

    engineered = create_features(df)

    return encode_features(engineered)


if __name__ == "__main__":

    from .dataset import (
        load_dataset,
        prepare_dataset,
    )

    data = load_dataset()

    data = prepare_dataset(data)

    features = build_feature_matrix(data)

    print(
        "Feature engineering completed."
    )

    print(
        f"Original rows: {len(data)}"
    )

    print(
        f"Feature count: {features.shape[1]}"
    )

    print(
        f"Feature matrix shape: {features.shape}"
    )