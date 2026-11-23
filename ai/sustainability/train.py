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

from .model import (
    SustainabilityIntelligenceModel,
)


def main():

    print()
    print("=" * 60)
    print(
        "KALASETU - SUSTAINABILITY INTELLIGENCE AI TRAINING"
    )
    print("=" * 60)

    df = load_dataset(
        DATASET_PATH
    )

    print(
        f"Dataset rows: {len(df)}"
    )

    print(
        f"Dataset columns: {len(df.columns)}"
    )

    model = (
        SustainabilityIntelligenceModel()
    )

    results = model.analyze(
        df
    )

    model.save(
        MODEL_PATH
    )

    average_score = (
        sum(
            item["sustainability_score"]
            for item in results
        )
        / len(results)
    )

    average_carbon = (
        sum(
            item[
                "estimated_carbon_kg_co2e"
            ]
            for item in results
        )
        / len(results)
    )

    RESEARCH_EXPERIMENT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata = {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "algorithm": (
            "Explainable Sustainability Scoring"
        ),
        "dataset_path": str(
            DATASET_PATH
        ),
        "dataset_rows": len(df),
        "average_sustainability_score": round(
            average_score,
            2,
        ),
        "average_estimated_carbon_kg_co2e": round(
            average_carbon,
            3,
        ),
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
    print(
        f"Average sustainability score: "
        f"{average_score:.2f}"
    )

    print(
        f"Average estimated carbon impact: "
        f"{average_carbon:.3f} kg CO2e"
    )

    print()
    print(
        "Sustainability model saved to:"
    )

    print(MODEL_PATH)

    print()
    print(
        "Research metadata saved to:"
    )

    print(metadata_path)

    print()
    print(
        f"Research valid: {RESEARCH_VALID}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()