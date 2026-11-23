import argparse
import json

from .config import RESEARCH_VALID

from .features import (
    clean_text,
    detect_category,
    description_quality,
    extract_keywords,
)

from .model import NLPModel


def predict(
    text: str,
):

    cleaned = clean_text(
        text
    )

    if not cleaned:
        raise ValueError(
            "Product description cannot be empty."
        )

    model = NLPModel.load()

    matrix = model.transform(
        [cleaned]
    )

    category, category_confidence = (
        detect_category(
            cleaned
        )
    )

    quality = description_quality(
        cleaned
    )

    keywords = extract_keywords(
        cleaned,
        model.vectorizer,
        matrix[0],
    )

    # TF-IDF encodes lexical overlap; it does not calculate semantic similarity.
    # A self-comparison would always return 1.0 and is intentionally omitted.
    nonzero_terms = int(matrix.nnz)

    result = {
        "text": text,
        "cleaned_text": cleaned,
        "detected_category": category,
        "category_confidence": category_confidence,
        "keywords": keywords,
        "description_quality": quality,
        "semantic_representation_size": (
            matrix.shape[1]
        ),
        "nonzero_tfidf_terms": nonzero_terms,
        "category_detection_method": "domain_keyword_rules",
        "model": "TF-IDF",
        "model_version": "1.0.0",
        "research_valid": RESEARCH_VALID,
        "note": (
            "TF-IDF is lexical feature extraction, not a semantic embedding model. "
            "Category confidence is a keyword-score ratio, not a calibrated probability. "
            "Research claims require human-labelled multilingual query-product relevance data."
        ),
    }

    return result


def main():

    parser = argparse.ArgumentParser(
        description=(
            "KalaSetu NLP / Semantic Intelligence"
        )
    )

    parser.add_argument(
        "--text",
        required=True,
        help="Product description",
    )

    args = parser.parse_args()

    result = predict(
        args.text
    )

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()