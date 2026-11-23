import json

from .config import (
    DATASET_PATH,
    MODEL_NAME,
    MODEL_PATH,
    MODEL_VERSION,
    RESEARCH_EXPERIMENT_DIR,
    RESEARCH_VALID,
)
from .dataset import load_dataset
from .features import create_location_features
from .model import SmartLogisticsModel


def main():

    print()
    print("=" * 60)
    print(
        "KALASETU - SMART LOGISTICS AI TRAINING"
    )
    print("=" * 60)

    df = load_dataset(DATASET_PATH)

    print(
        f"Dataset rows: {len(df)}"
    )

    print(
        f"Dataset columns: {len(df.columns)}"
    )

    data = create_location_features(df)

    coordinates = data[
        ["latitude", "longitude"]
    ].values

    model = SmartLogisticsModel()

    model.fit_clusters(coordinates)

    cluster_labels = model.predict_clusters(
        coordinates
    )

    data["cluster"] = cluster_labels

    print(
        f"Clusters created: "
        f"{len(set(cluster_labels))}"
    )

    print()
    print("Cluster distribution:")

    print(
        data["cluster"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    model.save(MODEL_PATH)

    RESEARCH_EXPERIMENT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata = {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "algorithm": (
            "Geographic Clustering + OR-Tools VRP"
        ),
        "dataset_path": str(DATASET_PATH),
        "dataset_rows": len(df),
        "cluster_count": model.cluster_count,
        "vehicle_count": model.vehicle_count,
        "vehicle_capacity": model.vehicle_capacity,
        "dataset_type": "synthetic",
        "research_valid": RESEARCH_VALID,
    }

    metadata_path = (
        RESEARCH_EXPERIMENT_DIR
        / "training_metadata.json"
    )

    with open(
        metadata_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            indent=4,
        )

    print()
    print("Logistics model saved to:")
    print(MODEL_PATH)

    print()
    print("Research metadata saved to:")
    print(metadata_path)

    print()
    print(
        f"Research valid: {RESEARCH_VALID}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()