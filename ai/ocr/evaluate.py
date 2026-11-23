import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .config import (
    TEST_IMAGE_DIR,
    RESEARCH_EVALUATION_DIR,
    RESEARCH_RESULTS_DIR,
    DATASET_DIR,
    DATASET_FILE,
)
from .dataset import load_dataset, prepare_dataset, resolve_image_path
from .model import OCRModel


def create_test_image(
    text,
    output_path,
):
    """
    Create a controlled synthetic OCR image.
    """
    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    image = Image.new(
        "RGB",
        (1200, 300),
        "white",
    )

    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(
            "arial.ttf",
            42,
        )
    except OSError:
        font = ImageFont.load_default()

    draw.text(
        (40, 100),
        text,
        fill="black",
        font=font,
    )

    image.save(output_path)


def create_dataset():
    """
    Generate a small controlled OCR dataset.
    """
    TEST_IMAGE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    samples = [
        (
            "OCR001",
            "Handcrafted wooden wall decoration made by traditional artisan",
            "wood_craft",
        ),
        (
            "OCR002",
            "Handwoven cotton saree made by skilled artisan",
            "textile",
        ),
        (
            "OCR003",
            "Traditional clay pottery made by local artisan",
            "pottery",
        ),
        (
            "OCR004",
            "Handcrafted brass lamp with traditional carving",
            "metal_craft",
        ),
        (
            "OCR005",
            "Natural wood carving craft for home decoration",
            "wood_craft",
        ),
        (
            "OCR006",
            "Handwoven silk textile with traditional design",
            "textile",
        ),
        (
            "OCR007",
            "Terracotta clay pot made using traditional pottery",
            "pottery",
        ),
        (
            "OCR008",
            "Traditional copper craft made by skilled artisan",
            "metal_craft",
        ),
    ]

    rows = []

    for image_id, text, category in samples:
        filename = f"{image_id}.png"

        image_path = TEST_IMAGE_DIR / filename

        create_test_image(
            text,
            image_path,
        )

        rows.append(
            {
                "image_id": image_id,
                "image_path": filename,
                "expected_text": text,
                "category": category,
            }
        )

    import pandas as pd

    df = pd.DataFrame(rows)

    df.to_csv(
        DATASET_FILE,
        index=False,
    )

    return df


def text_similarity(expected, predicted):
    """
    Calculate token-level Jaccard similarity.
    """
    expected_tokens = set(
        expected.lower().split()
    )

    predicted_tokens = set(
        predicted.lower().split()
    )

    if not expected_tokens:
        return 0.0

    intersection = (
        expected_tokens
        & predicted_tokens
    )

    union = (
        expected_tokens
        | predicted_tokens
    )

    if not union:
        return 0.0

    return (
        len(intersection)
        / len(union)
        * 100
    )


def main():
    print("=" * 60)
    print("KALASETU - OCR INTELLIGENCE EVALUATION")
    print("=" * 60)

    df = create_dataset()

    print(f"Evaluation samples: {len(df)}")

    model = OCRModel()

    results = []

    for _, row in df.iterrows():

        image_path = resolve_image_path(
            row["image_path"]
        )

        image = Image.open(image_path)

        prediction = model.predict(image)

        similarity = text_similarity(
            row["expected_text"],
            prediction["text"],
        )

        category_correct = (
            prediction["detected_category"]
            == row["category"]
        )

        results.append(
            {
                "image_id": row["image_id"],
                "expected_category": row["category"],
                "predicted_category": prediction[
                    "detected_category"
                ],
                "category_correct": category_correct,
                "ocr_confidence": prediction[
                    "confidence"
                ],
                "text_similarity": round(
                    similarity,
                    2,
                ),
                "predicted_text": prediction[
                    "text"
                ],
            }
        )

    category_accuracy = (
        sum(
            result["category_correct"]
            for result in results
        )
        / len(results)
        * 100
    )

    average_confidence = (
        sum(
            result["ocr_confidence"]
            for result in results
        )
        / len(results)
    )

    average_similarity = (
        sum(
            result["text_similarity"]
            for result in results
        )
        / len(results)
    )

    summary = {
        "total_samples": len(results),
        "category_accuracy": round(
            category_accuracy,
            2,
        ),
        "average_ocr_confidence": round(
            average_confidence,
            2,
        ),
        "average_text_similarity": round(
            average_similarity,
            2,
        ),
        "dataset_type": "synthetic",
        "research_valid": False,
        "note": (
            "Evaluation uses controlled synthetic "
            "images. These results validate the "
            "pipeline, not real-world OCR accuracy."
        ),
    }

    RESEARCH_EVALUATION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    RESEARCH_RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_path = (
        RESEARCH_EVALUATION_DIR
        / "evaluation_results.json"
    )

    with open(
        results_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=4,
        )

    summary_path = (
        RESEARCH_EVALUATION_DIR
        / "evaluation_summary.json"
    )

    with open(
        summary_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=4,
        )

    result_summary_path = (
        RESEARCH_RESULTS_DIR
        / "evaluation_results.json"
    )

    with open(
        result_summary_path,
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
        f"Category accuracy: "
        f"{summary['category_accuracy']}%"
    )

    print(
        f"Average OCR confidence: "
        f"{summary['average_ocr_confidence']}"
    )

    print(
        f"Average text similarity: "
        f"{summary['average_text_similarity']}%"
    )

    print(
        f"Research valid: "
        f"{summary['research_valid']}"
    )

    print()
    print("Evaluation saved to:")
    print(RESEARCH_EVALUATION_DIR)

    print("=" * 60)


if __name__ == "__main__":
    main()