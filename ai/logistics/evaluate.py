import json

from .config import (
    DATASET_PATH,
    MODEL_PATH,
    RESEARCH_EVALUATION_DIR,
    RESEARCH_VALID,
)
from .dataset import load_dataset
from .features import (
    create_distance_matrix,
    create_location_features,
)
from .model import SmartLogisticsModel


def validate_routes(
    routes,
    node_count,
    depot_index=0,
):
    visited = []

    for route in routes:
        if not route:
            continue

        if route[0] != depot_index:
            return False

        if route[-1] != depot_index:
            return False

        visited.extend(
            node
            for node in route
            if node != depot_index
        )

    expected = set(
        range(1, node_count)
    )

    return set(visited) == expected


def main():

    print()
    print("=" * 60)
    print(
        "KALASETU - SMART LOGISTICS AI EVALUATION"
    )
    print("=" * 60)

    df = load_dataset(DATASET_PATH)

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

    route_valid = validate_routes(
        result["routes"],
        len(data),
    )

    average_distance = (
        result["total_distance_km"]
        / max(len(result["routes"]), 1)
    )

    print()
    print(
        f"Evaluation samples: {len(df)}"
    )

    print(
        f"Routes generated: "
        f"{len(result['routes'])}"
    )

    print(
        f"Total route distance: "
        f"{result['total_distance_km']} km"
    )

    print(
        f"Average route distance: "
        f"{average_distance:.2f} km"
    )

    print(
        f"Route validity: "
        f"{route_valid}"
    )

    print()
    print(
        f"Research valid: {RESEARCH_VALID}"
    )

    RESEARCH_EVALUATION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary = {
        "evaluation_samples": len(df),
        "routes_generated": len(
            result["routes"]
        ),
        "total_distance_km": result[
            "total_distance_km"
        ],
        "average_route_distance_km": round(
            average_distance,
            3,
        ),
        "route_valid": route_valid,
        "routes": result["routes"],
        "research_valid": RESEARCH_VALID,
    }

    output_path = (
        RESEARCH_EVALUATION_DIR
        / "evaluation_summary.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=4,
        )

    print()
    print("Evaluation saved to:")
    print(RESEARCH_EVALUATION_DIR)

    print("=" * 60)


if __name__ == "__main__":
    main()