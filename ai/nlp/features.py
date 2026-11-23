import re

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer

from .config import (
    CATEGORY_KEYWORDS,
    DESCRIPTION_CONCEPTS,
)


def clean_text(text: str) -> str:
    """
    Basic NLP text cleaning.
    """

    text = str(text).lower()

    text = re.sub(
        r"[^\w\s]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def clean_text_series(series):
    """
    Clean a pandas text series.
    """

    return series.astype(str).apply(
        clean_text
    )


def build_tfidf(
    texts,
    max_features=5000,
    ngram_range=(1, 2),
    min_df=1,
    max_df=0.95,
):
    """
    Build TF-IDF representation.
    """

    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        max_df=max_df,
        stop_words="english",
    )

    matrix = vectorizer.fit_transform(
        texts
    )

    return vectorizer, matrix


def transform_tfidf(
    vectorizer,
    texts,
):
    """
    Transform new text using trained TF-IDF vectorizer.
    """

    return vectorizer.transform(
        texts
    )


def extract_keywords(
    text: str,
    vectorizer,
    matrix_row,
    top_k: int = 8,
):
    """
    Extract top TF-IDF keywords from one document.
    """

    feature_names = np.array(
        vectorizer.get_feature_names_out()
    )

    scores = matrix_row.toarray().flatten()

    ranked_indices = np.argsort(
        scores
    )[::-1]

    keywords = []

    for index in ranked_indices:

        if scores[index] <= 0:
            continue

        word = feature_names[index]

        if word not in keywords:
            keywords.append(word)

        if len(keywords) >= top_k:
            break

    return keywords


def detect_category(
    text: str,
):
    """
    Detect likely KalaSetu craft category
    using domain vocabulary.
    """

    cleaned = clean_text(text)

    category_scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if keyword in cleaned:
                score += 1

        category_scores[category] = score

    if not category_scores:
        return "unknown", 0.0

    best_category = max(
        category_scores,
        key=category_scores.get,
    )

    best_score = category_scores[
        best_category
    ]

    total_score = sum(
        category_scores.values()
    )

    if best_score == 0:
        return "unknown", 0.0

    confidence = (
        best_score / max(total_score, 1)
    ) * 100.0

    return (
        best_category,
        round(confidence, 2),
    )


def description_quality(
    text: str,
):
    """
    Estimate description quality using
    explainable content indicators.

    This is not a learned quality model.
    """

    cleaned = clean_text(text)

    words = cleaned.split()

    word_count = len(words)

    score = 0.0

    reasons = []

    # Length
    if word_count >= 20:
        score += 20
        reasons.append(
            "adequate description length"
        )
    elif word_count >= 10:
        score += 12
        reasons.append(
            "moderate description length"
        )
    else:
        score += 5
        reasons.append(
            "short description"
        )

    # Material
    material_terms = [
        "wood",
        "wooden",
        "cotton",
        "silk",
        "clay",
        "ceramic",
        "brass",
        "copper",
        "metal",
        "iron",
    ]

    if any(
        term in cleaned
        for term in material_terms
    ):
        score += 15
        reasons.append(
            "material information present"
        )

    # Craft information
    craft_terms = [
        "handcrafted",
        "handmade",
        "traditional",
        "artisan",
        "craft",
        "carved",
        "woven",
        "pottery",
    ]

    if any(
        term in cleaned
        for term in craft_terms
    ):
        score += 15
        reasons.append(
            "craft information present"
        )

    # Usage
    usage_terms = [
        "decorative",
        "decoration",
        "home",
        "storage",
        "lamp",
        "bag",
        "bowl",
        "vase",
        "planter",
    ]

    if any(
        term in cleaned
        for term in usage_terms
    ):
        score += 15
        reasons.append(
            "usage information present"
        )

    # Artisan information
    if "artisan" in cleaned:
        score += 10
        reasons.append(
            "artisan information present"
        )

    # Traditional information
    if "traditional" in cleaned:
        score += 10
        reasons.append(
            "traditional context present"
        )

    # Basic uniqueness / information density
    unique_words = len(
        set(words)
    )

    if word_count > 0:

        uniqueness_ratio = (
            unique_words / word_count
        )

        if uniqueness_ratio >= 0.65:
            score += 15
            reasons.append(
                "good vocabulary diversity"
            )

    score = min(
        max(score, 0.0),
        100.0,
    )

    if score >= 75:
        quality_level = "HIGH"

    elif score >= 50:
        quality_level = "MEDIUM"

    else:
        quality_level = "LOW"

    return {
        "quality_score": round(
            score,
            2,
        ),
        "quality_level": quality_level,
        "reasons": reasons,
    }


def semantic_similarity(
    matrix_a,
    matrix_b,
):
    """
    Calculate cosine similarity between
    TF-IDF representations.
    """

    from sklearn.metrics.pairwise import cosine_similarity

    return cosine_similarity(
        matrix_a,
        matrix_b,
    )