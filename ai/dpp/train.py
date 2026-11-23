import json

from .config import (
    MODEL_NAME,
    MODEL_VERSION,
    ALGORITHM,
    DATASET_TYPE,
    RESEARCH_VALID,
    MODEL_PATH,
    RESEARCH_EXPERIMENT_DIR,
)
from .dataset import (
    load_dataset,
    validate_dataset,
)
from .model import DigitalProductPassportModel


def main():

    print("=" * 60)
    print("KALASETU - DIGITAL PRODUCT PASSPORT AI TRAINING")
    print("=" * 60)

    df = load_dataset()

    validate_dataset(df)

    print(f"Dataset rows: {len(df)}")
    print(f"Dataset columns: {len(df.columns)}")

    model = DigitalProductPassportModel(
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
    )

    records = df.to_dict(
        orient="records"
    )

    passports = [
        model.create(record)
        for record in records
    ]

    average_completeness = sum(
        passport["intelligence"]["completeness_score"]
        for passport in passports
    ) / len(passports)

    verified_count = sum(
        model.verify(passport)["verified"]
        for passport in passports
    )

    model.save(MODEL_PATH)

    RESEARCH_EXPERIMENT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata = {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "algorithm": ALGORITHM,
        "dataset_type": DATASET_TYPE,
        "dataset_rows": len(df),
        "average_completeness_score": round(
            average_completeness,
            2,
        ),
        "verified_passports": verified_count,
        "research_valid": RESEARCH_VALID,
    }

    metadata_path = (
        RESEARCH_EXPERIMENT_DIR
        / "training_metadata.json"
    )

    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=4,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "Average passport completeness score: "
        f"{average_completeness:.2f}"
    )

    print(
        f"Integrity-verified passports: "
        f"{verified_count}/{len(passports)}"
    )

    print()
    print("DPP model saved to:")
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