import json

from .config import (
    MODEL_PATH,
    RESEARCH_EVALUATION_DIR,
    RESEARCH_VALID,
)
from .dataset import (
    load_dataset,
    validate_dataset,
)
from .model import DigitalProductPassportModel


def main():

    print("=" * 60)
    print("KALASETU - DIGITAL PRODUCT PASSPORT AI EVALUATION")
    print("=" * 60)

    df = load_dataset()

    validate_dataset(df)

    model = DigitalProductPassportModel.load(
        MODEL_PATH
    )

    records = df.to_dict(
        orient="records"
    )

    passports = [
        model.create(record)
        for record in records
    ]

    completeness_scores = [
        passport["intelligence"]["completeness_score"]
        for passport in passports
    ]

    verification_results = [
        model.verify(passport)
        for passport in passports
    ]

    average_completeness = (
        sum(completeness_scores)
        / len(completeness_scores)
    )

    verified_count = sum(
        result["verified"]
        for result in verification_results
    )

    high = sum(
        score >= 90
        for score in completeness_scores
    )

    medium = sum(
        70 <= score < 90
        for score in completeness_scores
    )

    low = sum(
        score < 70
        for score in completeness_scores
    )

    summary = {
        "evaluation_samples": len(df),
        "average_completeness_score": round(
            average_completeness,
            2,
        ),
        "verified_passports": verified_count,
        "high_completeness": high,
        "medium_completeness": medium,
        "low_completeness": low,
        "research_valid": RESEARCH_VALID,
    }

    RESEARCH_EVALUATION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        RESEARCH_EVALUATION_DIR
        / "evaluation_summary.json"
    )

    output_path.write_text(
        json.dumps(
            summary,
            indent=4,
        ),
        encoding="utf-8",
    )

    print()
    print(
        f"Evaluation samples: {len(df)}"
    )

    print(
        "Average passport completeness score: "
        f"{average_completeness:.2f}"
    )

    print()
    print("Completeness levels:")
    print(f"HIGH: {high}")
    print(f"MEDIUM: {medium}")
    print(f"LOW: {low}")

    print()
    print(
        "Integrity-verified passports: "
        f"{verified_count}/{len(df)}"
    )

    print()
    print(
        f"Research valid: {RESEARCH_VALID}"
    )

    print()
    print("Evaluation saved to:")
    print(RESEARCH_EVALUATION_DIR)

    print("=" * 60)


if __name__ == "__main__":
    main()