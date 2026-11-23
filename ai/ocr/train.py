import json
from datetime import datetime, timezone

from .config import (
    MODEL_FILE,
    MODEL_DIR,
    RESEARCH_EXPERIMENT_DIR,
    RESEARCH_RESULTS_DIR,
    DATASET_FILE,
    RESEARCH_VALID,
    DATASET_TYPE,
    MODEL_VERSION,
)
from .dataset import load_dataset, prepare_dataset
from .model import OCRModel


def main():
    print("=" * 60)
    print("KALASETU - OCR INTELLIGENCE TRAINING")
    print("=" * 60)

    df = load_dataset()
    df = prepare_dataset(df)

    print(f"Dataset rows: {len(df)}")
    print(f"Dataset columns: {len(df.columns)}")

    model = OCRModel()

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    RESEARCH_EXPERIMENT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    RESEARCH_RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model.save(MODEL_FILE)

    metadata = {
        "model": "Tesseract OCR",
        "model_version": MODEL_VERSION,
        "dataset": str(DATASET_FILE),
        "dataset_type": DATASET_TYPE,
        "dataset_rows": len(df),
        "language": model.language,
        "page_segmentation_mode": model.psm,
        "ocr_engine_mode": model.oem,
        "tesseract_path": model.tesseract_cmd,
        "training_type": (
            "configuration_and_pipeline_setup"
        ),
        "created_at": datetime.now(timezone.utc).isoformat(),
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

    result_path = (
        RESEARCH_RESULTS_DIR
        / "training_result.json"
    )

    with open(
        result_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            indent=4,
        )

    print()
    print("OCR configuration saved to:")
    print(MODEL_FILE)

    print()
    print("Research metadata saved to:")
    print(metadata_path)

    print()
    print(f"Research valid: {RESEARCH_VALID}")

    print("=" * 60)


if __name__ == "__main__":
    main()