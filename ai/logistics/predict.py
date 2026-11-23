import argparse
import json

import pandas as pd

from .config import (
    AVERAGE_SPEED_KMPH,
    MODEL_NAME,
    MODEL_PATH,
    MODEL_VERSION,
    RESEARCH_VALID,
)
from .features import (
    create_distance_matrix,
    create_location_features,
    estimate_route_time,
)
from .model import SmartLogisticsModel


def main():

    parser = argparse.ArgumentParser(
        description=(
            "KalaSetu Smart Logistics prediction"
        )
    )

    parser.add_argument(
        "--vehicle-count",
        type=int,
        default=2,
    )

    parser.add_argument(
        "--vehicle-capacity",
        type=int,
        default=10,
    )

    args = parser.parse_args()

    df = pd.read_csv(
        "ml/datasets/logistics/logistics.csv"
    )

    data = create_location_features(df)

    distance_matrix = create_distance_matrix(
        data
    )

    demands = (
        data["package_weight"]
        .round()
        .astype(int)
        .tolist()
    )

    model = SmartLogisticsModel.load(
        MODEL_PATH
    )

    result = model.optimize_route(
        distance_matrix,
        demands,
    )

    estimated_time = estimate_route_time(
        result["total_distance_km"],
        AVERAGE_SPEED_KMPH,
    )

    output = {
        "model": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "orders_processed": len(data),
        "routes_generated": len(
            result["routes"]
        ),
        "total_distance_km": result[
            "total_distance_km"
        ],
        "estimated_delivery_time_minutes": round(
            estimated_time,
            2,
        ),
        "routes": result["routes"],
        "vehicle_count": result[
            "vehicle_count"
        ],
        "research_valid": RESEARCH_VALID,
        "note": (
            "Prototype logistics optimization "
            "using synthetic location data. "
            "Distance and delivery time are "
            "decision-support estimates and "
            "do not represent live traffic."
        ),
    }

    print()
    print(
        json.dumps(
            output,
            indent=4,
        )
    )


if __name__ == "__main__":
    main()