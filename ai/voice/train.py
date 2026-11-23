from datetime import datetime, timezone
from pathlib import Path
import json

from .config import (
    MODEL_DIR,
    RESEARCH_EXPERIMENT_DIR,
    MODEL_NAME,
    MODEL_VERSION,
    DATASET_TYPE,
    RESEARCH_VALID,
)

from .model import VoiceLanguageModel


def main():

    print()
    print("=" * 60)
    print(
        "KALASETU - VOICE & LANGUAGE AI TRAINING"
    )
    print("=" * 60)

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    RESEARCH_EXPERIMENT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model = VoiceLanguageModel()

    model_path = (
        MODEL_DIR
        / "voice_language_model.joblib"
    )

    model.save(
        model_path
    )

    metadata = {

        "model_name": MODEL_NAME,

        "model_version": MODEL_VERSION,

        "speech_backend": (
            "Google Speech Recognition"
        ),

        "language_backend": (
            "langdetect"
        ),

        "dataset_type": DATASET_TYPE,

        "research_valid": RESEARCH_VALID,

        "created_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),

        "description": (
            "Prototype voice and language "
            "intelligence baseline for KalaSetu."
        ),
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
            ensure_ascii=False,
        )

    print()
    print(
        "Voice-language model configuration saved to:"
    )

    print(model_path)

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
