import json

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

from .config import (
    DATASET_PATH,
    RESEARCH_EVALUATION_DIR,
    RESEARCH_VALID,
)
from .dataset import load_dataset
from .features import encode_features
from .model import InventoryIntelligenceModel
from .train import create_inventory_label


def main():

    print()
    print("=" * 60)
    print("KALASETU - INVENTORY INTELLIGENCE AI EVALUATION")
    print("=" * 60)

    df = load_dataset(DATASET_PATH)

    df["stock_status"] = df.apply(
        create_inventory_label,
        axis=1,
    )

    X = encode_features(df)

    y_true = df["stock_status"]

    model = InventoryIntelligenceModel.load()

    y_pred = model.predict(X)

    accuracy = accuracy_score(
        y_true,
        y_pred,
    )

    labels = sorted(
        y_true.unique().tolist()
    )

    report = classification_report(
        y_true,
        y_pred,
        labels=labels,
        zero_division=0,
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=labels,
    )

    print()
    print(
        f"Evaluation samples: {len(df)}"
    )

    print(
        f"Accuracy: {accuracy * 100:.2f}%"
    )

    print()
    print("Classification report:")
    print(report)

    print("Confusion matrix:")

    print(matrix)

    print()
    print(
        f"Research valid: {RESEARCH_VALID}"
    )

    RESEARCH_EVALUATION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary = {
        "evaluation_samples": len(df),
        "accuracy": float(accuracy),
        "classification_report": classification_report(
            y_true,
            y_pred,
            labels=labels,
            zero_division=0,
            output_dict=True,
        ),
        "confusion_matrix": matrix.tolist(),
        "labels": labels,
        "research_valid": RESEARCH_VALID,
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
    print(RESEARCH_EVALUATION_DIR)

    print("=" * 60)


if __name__ == "__main__":
    main()