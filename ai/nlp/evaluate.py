import json

import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity

from .config import (
    DATASET_PATH,
    EVALUATION_DIR,
    RESEARCH_VALID,
)

from .dataset import (
    load_dataset,
    prepare_dataset,
    validate_dataset,
)

from .features import (
    clean_text_series,
    detect_category,
    description_quality,
)

from .model import NLPModel


def main():

    print(
        "=" * 60
    )

    print(
        "KALASETU - NLP / SEMANTIC INTELLIGENCE EVALUATION"
    )

    print(
        "=" * 60
    )

    # --------------------------------------------------------
    # Dataset
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

    texts = clean_text_series(
        df["product_text"]
    )

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    model = NLPModel.load()

    matrix = model.transform(
        texts
    )

    # --------------------------------------------------------
    # Category + quality
    # --------------------------------------------------------

    results = []

    for index, row in df.iterrows():

        category, category_confidence = (
            detect_category(
                row["product_text"]
            )
        )

        quality = description_quality(
            row["product_text"]
        )

        results.append(
            {
                "product_id": row[
                    "product_id"
                ],
                "actual_category": row[
                    "product_category"
                ],
                "detected_category": category,
                "category_confidence": (
                    category_confidence
                ),
                "quality_score": quality[
                    "quality_score"
                ],
                "quality_level": quality[
                    "quality_level"
                ],
            }
        )

    results_df = pd.DataFrame(
        results
    )

    # --------------------------------------------------------
    # Category accuracy
    # --------------------------------------------------------

    category_accuracy = (
        results_df[
            "actual_category"
        ]
        == results_df[
            "detected_category"
        ]
    ).mean() * 100

    # --------------------------------------------------------
    # Average quality
    # --------------------------------------------------------

    average_quality = (
        results_df[
            "quality_score"
        ].mean()
    )

    # --------------------------------------------------------
    # Similarity
    # --------------------------------------------------------

    similarity_matrix = cosine_similarity(
        matrix
    )

    similarity_values = []

    for i in range(
        len(similarity_matrix)
    ):

        for j in range(
            i + 1,
            len(similarity_matrix),
        ):

            similarity_values.append(
                similarity_matrix[i][j]
            )

    average_similarity = (
        sum(similarity_values)
        / max(
            len(similarity_values),
            1,
        )
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = {
        "total_products": len(df),
        "vocabulary_size": len(
            model.get_feature_names()
        ),
        "category_accuracy": round(
            category_accuracy,
            2,
        ),
        "average_description_quality": round(
            average_quality,
            2,
        ),
        "average_pairwise_similarity": round(
            float(average_similarity),
            4,
        ),
        "research_valid": RESEARCH_VALID,
        "dataset_type": "synthetic",
    }

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    EVALUATION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_path = (
        EVALUATION_DIR
        / "evaluation_summary.json"
    )

    results_path = (
        EVALUATION_DIR
        / "evaluation_results.csv"
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

    results_df.to_csv(
        results_path,
        index=False,
    )

    # --------------------------------------------------------
    # Print
    # --------------------------------------------------------

    print(
        f"Total products: "
        f"{summary['total_products']}"
    )

    print(
        f"Vocabulary size: "
        f"{summary['vocabulary_size']}"
    )

    print(
        f"Category accuracy: "
        f"{summary['category_accuracy']}%"
    )

    print(
        f"Average description quality: "
        f"{summary['average_description_quality']}"
    )

    print(
        f"Average pairwise similarity: "
        f"{summary['average_pairwise_similarity']}"
    )

    print(
        f"Research valid: "
        f"{summary['research_valid']}"
    )

    print(
        "\nEvaluation saved to:"
    )

    print(
        EVALUATION_DIR
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()