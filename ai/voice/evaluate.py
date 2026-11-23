import json
from pathlib import Path

from .config import (
    RESEARCH_EVALUATION_DIR,
    RESEARCH_VALID,
)

from .language import (
    language_intelligence,
)


EVALUATION_DATA = [

    {
        "id": "VOICE001",
        "text": (
            "This is a handcrafted wooden "
            "wall decoration made by an artisan"
        ),
        "expected_language": "en",
        "expected_intent": "product_information",
    },

    {
        "id": "VOICE002",
        "text": (
            "हस्तशिल्प उत्पाद की कीमत क्या है"
        ),
        "expected_language": "hi",
        "expected_intent": "pricing",
    },

    {
        "id": "VOICE003",
        "text": (
            "ಕರಕುಶಲ ಉತ್ಪನ್ನದ ಬೆಲೆ ಎಷ್ಟು"
        ),
        "expected_language": "kn",
        "expected_intent": "pricing",
    },

    {
        "id": "VOICE004",
        "text": (
            "The artisan wants to know the "
            "market opportunity for this craft"
        ),
        "expected_language": "en",
        "expected_intent": "market",
    },

    {
        "id": "VOICE005",
        "text": (
            "हस्तशिल्प कारीगर बाजार की जानकारी चाहते हैं"
        ),
        "expected_language": "hi",
        "expected_intent": "market",
    },

    {
        "id": "VOICE006",
        "text": (
            "Handmade pottery product"
        ),
        "expected_language": "en",
        "expected_intent": "product_information",
    },

    {
        "id": "VOICE007",
        "text": (
            "Handwoven textile product"
        ),
        "expected_language": "en",
        "expected_intent": "product_information",
    },

    {
        "id": "VOICE008",
        "text": (
            "The market price of this craft"
        ),
        "expected_language": "en",
        "expected_intent": "pricing",
    },
]


def main():

    print()
    print("=" * 60)
    print(
        "KALASETU - VOICE & LANGUAGE AI EVALUATION"
    )
    print("=" * 60)

    total = len(
        EVALUATION_DATA
    )

    language_correct = 0
    intent_correct = 0

    results = []

    for sample in EVALUATION_DATA:

        result = language_intelligence(
            sample["text"]
        )

        language_ok = (
            result["language_code"]
            == sample["expected_language"]
        )

        intent_ok = (
            result["intent"]
            == sample["expected_intent"]
        )

        if language_ok:
            language_correct += 1

        if intent_ok:
            intent_correct += 1

        results.append({
            "id": sample["id"],
            "text": sample["text"],
            "expected_language": (
                sample["expected_language"]
            ),
            "detected_language": (
                result["language_code"]
            ),
            "expected_intent": (
                sample["expected_intent"]
            ),
            "detected_intent": (
                result["intent"]
            ),
            "language_correct": language_ok,
            "intent_correct": intent_ok,
        })

    language_accuracy = (
        language_correct
        / total
        * 100
    )

    intent_accuracy = (
        intent_correct
        / total
        * 100
    )

    RESEARCH_EVALUATION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        RESEARCH_EVALUATION_DIR
        / "evaluation_summary.json"
    )

    summary = {

        "total_samples": total,

        "language_accuracy": round(
            language_accuracy,
            2,
        ),

        "intent_accuracy": round(
            intent_accuracy,
            2,
        ),

        "research_valid": RESEARCH_VALID,

        "dataset_type": "controlled synthetic examples",
    }

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            {
                "summary": summary,
                "results": results,
            },
            file,
            indent=4,
            ensure_ascii=False,
        )

    print()
    print(
        f"Evaluation samples: {total}"
    )

    print(
        f"Language accuracy: "
        f"{language_accuracy:.2f}%"
    )

    print(
        f"Intent accuracy: "
        f"{intent_accuracy:.2f}%"
    )

    print(
        f"Research valid: "
        f"{RESEARCH_EVALUATION_DIR.exists() and RESEARCH_VALID}"
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
