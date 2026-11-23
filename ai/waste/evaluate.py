from pathlib import Path

from .dataset import (
    load_dataset,
    validate_dataset,
)

from .scoring import score_waste

from .config import DATASET_PATH


def evaluate_dataset(
    path: str | Path = DATASET_PATH,
) -> dict:

    df = load_dataset(path)

    validation = validate_dataset(df)

    if not validation["valid"]:
        raise ValueError(
            f"Dataset validation failed: {validation}"
        )

    results = []

    for _, row in df.iterrows():

        result = score_waste(
            row.to_dict()
        )

        results.append(result)

    scores = [
        item["reuse_score"]
        for item in results
    ]

    high = sum(
        item["feasibility"] == "HIGH"
        for item in results
    )

    medium = sum(
        item["feasibility"] == "MEDIUM"
        for item in results
    )

    low = sum(
        item["feasibility"] == "LOW"
        for item in results
    )

    average_score = (
        sum(scores) / len(scores)
        if scores
        else 0
    )

    return {
        "dataset_rows": len(df),
        "average_reuse_score": round(
            average_score,
            2,
        ),
        "high_feasibility": high,
        "medium_feasibility": medium,
        "low_feasibility": low,
        "validation": validation,
        "research_valid": False,
        "research_note": (
            "Dataset is synthetic/prototype data. "
            "Results must not be reported as "
            "real-world research performance."
        ),
        "sample_results": results[:5],
    }


if __name__ == "__main__":

    result = evaluate_dataset()

    print("=" * 60)
    print(
        "KALASETU WASTE INTELLIGENCE EVALUATION"
    )
    print("=" * 60)

    print(
        f"Dataset rows: "
        f"{result['dataset_rows']}"
    )

    print(
        f"Average reuse score: "
        f"{result['average_reuse_score']}"
    )

    print(
        f"High feasibility: "
        f"{result['high_feasibility']}"
    )

    print(
        f"Medium feasibility: "
        f"{result['medium_feasibility']}"
    )

    print(
        f"Low feasibility: "
        f"{result['low_feasibility']}"
    )

    print(
        f"Research valid: "
        f"{result['research_valid']}"
    )

    print("\nSample results:")

    for item in result["sample_results"]:

        print(
            f"- {item['waste_id']}: "
            f"{item['reuse_score']} "
            f"({item['feasibility']})"
        )

    print("\nEvaluation complete.")