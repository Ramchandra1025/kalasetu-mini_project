import argparse
import json

import pandas as pd

from .features import (
    build_feature_matrix,
)

from .model import (
    AnomalyDetector,
)

from .config import (
    MODEL_PATH,
)


def classify_risk(
    score: float,
) -> str:

    if score >= 75:
        return "HIGH RISK"

    if score >= 50:
        return "SUSPICIOUS"

    return "NORMAL"


def generate_reasons(
    row: pd.Series,
) -> list[str]:

    reasons = []

    if abs(
        row["price_deviation"]
    ) >= 30:

        reasons.append(
            "large price deviation"
        )

    if abs(
        row["quantity_deviation"]
    ) >= 30:

        reasons.append(
            "unusual order quantity"
        )

    if abs(
        row["amount_deviation"]
    ) >= 30:

        reasons.append(
            "unusual transaction amount"
        )

    if (
        row["cancellation_rate"]
        >= 40
    ):

        reasons.append(
            "high cancellation rate"
        )

    if (
        row["orders_last_7_days"]
        >= 20
    ):

        reasons.append(
            "unusually high recent order frequency"
        )

    if (
        row["repeated_buyer_count"]
        >= 10
    ):

        reasons.append(
            "high repeated buyer activity"
        )

    if (
        row["repeated_artisan_count"]
        >= 10
    ):

        reasons.append(
            "high repeated artisan activity"
        )

    if not reasons:

        reasons.append(
            "no major rule-based anomaly signals detected"
        )

    return reasons


def predict(
    activity: dict,
) -> dict:

    df = pd.DataFrame(
        [activity]
    )

    features = build_feature_matrix(
        df
    )

    detector = AnomalyDetector.load(
        MODEL_PATH
    )

    prediction = detector.predict(
        features
    )[0]

    score = float(
        detector.anomaly_score(
            features
        )[0]
    )

    risk_level = classify_risk(
        score
    )

    reasons = generate_reasons(
        df.iloc[0]
    )

    result = {

        "activity_id": activity.get(
            "activity_id",
            "prediction",
        ),

        "activity_type": activity[
            "activity_type"
        ],

        "anomaly_score": round(
            score,
            2,
        ),

        "risk_level": risk_level,

        "detected_anomaly": bool(
            prediction == -1
        ),

        "reasons": reasons,

        "model": "Isolation Forest",

        "model_version": "1.0.0",

        "research_valid": False,

        "note": (
            "Prototype anomaly detection "
            "using synthetic data. "
            "A detected anomaly does not "
            "necessarily mean fraud."
        ),
    }

    return result


def main():

    parser = argparse.ArgumentParser(
        description=(
            "KalaSetu Scam / Anomaly "
            "Detection Prediction"
        )
    )

    parser.add_argument(
        "--activity-type",
        default="transaction",
    )

    parser.add_argument(
        "--account-type",
        default="buyer",
    )

    parser.add_argument(
        "--region",
        default="karnataka",
    )

    parser.add_argument(
        "--account-age-days",
        type=float,
        default=365,
    )

    parser.add_argument(
        "--orders-7-days",
        type=float,
        default=5,
    )

    parser.add_argument(
        "--orders-30-days",
        type=float,
        default=20,
    )

    parser.add_argument(
        "--order-quantity",
        type=float,
        default=2,
    )

    parser.add_argument(
        "--transaction-amount",
        type=float,
        default=2500,
    )

    parser.add_argument(
        "--cancellation-rate",
        type=float,
        default=5,
    )

    parser.add_argument(
        "--price-deviation",
        type=float,
        default=5,
    )

    parser.add_argument(
        "--repeated-buyer-count",
        type=float,
        default=2,
    )

    parser.add_argument(
        "--repeated-artisan-count",
        type=float,
        default=2,
    )

    parser.add_argument(
        "--quantity-deviation",
        type=float,
        default=5,
    )

    parser.add_argument(
        "--amount-deviation",
        type=float,
        default=5,
    )

    args = parser.parse_args()

    activity = {

        "activity_id": "prediction",

        "activity_type":
            args.activity_type,

        "account_type":
            args.account_type,

        "region":
            args.region,

        "account_age_days":
            args.account_age_days,

        "orders_last_7_days":
            args.orders_7_days,

        "orders_last_30_days":
            args.orders_30_days,

        "order_quantity":
            args.order_quantity,

        "transaction_amount":
            args.transaction_amount,

        "cancellation_rate":
            args.cancellation_rate,

        "price_deviation":
            args.price_deviation,

        "repeated_buyer_count":
            args.repeated_buyer_count,

        "repeated_artisan_count":
            args.repeated_artisan_count,

        "quantity_deviation":
            args.quantity_deviation,

        "amount_deviation":
            args.amount_deviation,
    }

    result = predict(
        activity
    )

    print(
        json.dumps(
            result,
            indent=4,
        )
    )


if __name__ == "__main__":
    main()