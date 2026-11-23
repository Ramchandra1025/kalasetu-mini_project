import json

from .config import (
    DATASET_PATH,
    MODEL_PATH,
    RESEARCH_EVALUATION_DIR,
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
        "KALASETU - SUSTAINABILITY INTELLIGENCE AI EVALUATION"
    )
    print("=" * 60)

    df = load_dataset(
        DATASET_PATH
    )

    model = (
        SustainabilityIntelligenceModel.load(
            MODEL_PATH
        )
    )

    results = model.analyze(
        df
    )

    total = len(results)

    average_score = (
        sum(
            item["sustainability_score"]
            for item in results
        )
        / total
    )

    average_carbon = (
        sum(
            item[
                "estimated_carbon_kg_co2e"
            ]
            for item in results
        )
        / total
    )

    high_count = sum(
        item["sustainability_level"]
        == "HIGH"
        for item in results
    )

    medium_count = sum(
        item["sustainability_level"]
        == "MEDIUM"
        for item in results
    )

    low_count = sum(
        item["sustainability_level"]
        == "LOW"
        for item in results
    )

    print()
    print(
        f"Evaluation samples: {total}"
    )

    print(
        f"Average sustainability score: "
        f"{average_score:.2f}"
    )

    print(
        f"Average estimated carbon impact: "
        f"{average_carbon:.3f} kg CO2e"
    )

    print()
    print("Sustainability levels:")

    print(
        f"HIGH: {high_count}"
    )

    print(
        f"MEDIUM: {medium_count}"
    )

    print(
        f"LOW: {low_count}"
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
        "evaluation_samples": total,
        "average_sustainability_score": round(
            average_score,
            2,
        ),
        "average_estimated_carbon_kg_co2e": round(
            average_carbon,
            3,
        ),
        "high_count": high_count,
        "medium_count": medium_count,
        "low_count": low_count,
        "research_valid": RESEARCH_VALID,
        "results": results,
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
    print(
        "Evaluation saved to:"
    )

    print(
        RESEARCH_EVALUATION_DIR
    )

    print("=" * 60)


if __name__ == "__main__":
    main()