import pandas as pd

from ai.nlp.dataset import (
    validate_dataset,
    prepare_dataset,
)

from ai.nlp.features import (
    clean_text,
    detect_category,
    description_quality,
)

from ai.nlp.model import NLPModel


def test_dataset():

    df = pd.DataFrame(
        {
            "product_id": [
                "TEST001",
                "TEST002",
            ],
            "product_category": [
                "wood_craft",
                "textile",
            ],
            "product_text": [
                "Handcrafted wooden product",
                "Handwoven cotton textile",
            ],
        }
    )

    assert validate_dataset(
        df
    ) is True

    prepared = prepare_dataset(
        df
    )

    assert len(prepared) == 2

    print(
        "Dataset test passed."
    )


def test_cleaning():

    text = (
        "Handcrafted WOODEN! Product "
        "for Home."
    )

    cleaned = clean_text(
        text
    )

    assert cleaned == (
        "handcrafted wooden product "
        "for home"
    )

    print(
        "Text cleaning test passed."
    )


def test_category():

    category, confidence = (
        detect_category(
            "Handcrafted wooden bowl "
            "made by traditional artisans."
        )
    )

    assert category == "wood_craft"

    assert confidence > 0

    print(
        "Category detection test passed."
    )


def test_quality():

    result = description_quality(
        "Handcrafted wooden bowl made "
        "by traditional artisans for "
        "home decoration."
    )

    assert "quality_score" in result

    assert (
        0 <= result["quality_score"] <= 100
    )

    assert result["quality_level"] in [
        "LOW",
        "MEDIUM",
        "HIGH",
    ]

    print(
        "Description quality test passed."
    )


def test_model():

    texts = [
        "handcrafted wooden bowl",
        "handwoven cotton textile",
        "traditional clay pottery",
        "brass metal artifact",
    ]

    model = NLPModel()

    model.fit(
        texts
    )

    matrix = model.transform(
        [
            "handcrafted wooden craft"
        ]
    )

    assert matrix.shape[0] == 1

    assert matrix.shape[1] > 0

    print(
        "NLP model test passed."
    )


def test_save_load():

    texts = [
        "wooden handcrafted product",
        "cotton textile product",
        "clay pottery product",
    ]

    model = NLPModel()

    model.fit(
        texts
    )

    model.save()

    loaded = NLPModel.load()

    matrix = loaded.transform(
        [
            "wooden product"
        ]
    )

    assert matrix.shape[0] == 1

    assert matrix.shape[1] > 0

    print(
        "Save/load test passed."
    )


def run_all_tests():

    print(
        "=" * 60
    )

    print(
        "KALASETU MODEL 9 TESTS"
    )

    print(
        "=" * 60
    )

    test_dataset()
    test_cleaning()
    test_category()
    test_quality()
    test_model()
    test_save_load()

    print()
    print(
        "ALL MODEL 9 TESTS PASSED"
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":
    run_all_tests()