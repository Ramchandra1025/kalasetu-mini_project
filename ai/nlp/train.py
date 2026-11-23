import json

from .config import (
    DATASET_PATH,
    EXPERIMENT_DIR,
    MODEL_PATH,
    RESEARCH_VALID,
    DATASET_TYPE,
)

from .dataset import (
    load_dataset,
    prepare_dataset,
    validate_dataset,
)

from .features import (
    clean_text_series,
)

from .model import NLPModel


def main():

    print(
        "=" * 60
    )

    print(
        "KALASETU - NLP / SEMANTIC INTELLIGENCE TRAINING"
    )

    print(
        "=" * 60
    )

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    df = load_dataset(
        DATASET_PATH
    )

    validate_dataset(
        df
    )

    df = prepare_dataset(
        df
    )

    print(
        f"Dataset rows: {len(df)}"
    )

    print(
        f"Dataset columns: {len(df.columns)}"
    )

    # --------------------------------------------------------
    # Clean text
    # --------------------------------------------------------

    texts = clean_text_series(
        df["product_text"]
    )

    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    model = NLPModel()

    model.fit(
        texts
    )

    vocabulary_size = len(
        model.get_feature_names()
    )

    print(
        f"Vocabulary size: {vocabulary_size}"
    )

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    model.save(
        MODEL_PATH
    )

    print(
        "\nModel saved to:"
    )

    print(
        MODEL_PATH
    )

    # --------------------------------------------------------
    # Research metadata
    # --------------------------------------------------------

    EXPERIMENT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata = {
        "model": "TF-IDF",
        "model_version": "1.0.0",
        "dataset_type": DATASET_TYPE,
        "dataset_rows": len(df),
        "vocabulary_size": vocabulary_size,
        "research_valid": RESEARCH_VALID,
    }

    metadata_path = (
        EXPERIMENT_DIR
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

    print(
        f"\nResearch metadata saved to:"
    )

    print(
        metadata_path
    )

    print(
        f"\nResearch valid: "
        f"{RESEARCH_VALID}"
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()