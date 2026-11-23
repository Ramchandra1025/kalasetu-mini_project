import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from ai.sustainability.dataset import (
    load_dataset,
    validate_dataset,
)

from ai.sustainability.features import (
    create_sustainability_features,
    get_feature_columns,
)

from ai.sustainability.scoring import (
    calculate_sustainability_score,
    estimate_carbon_impact,
    generate_recommendations,
    analyze_sustainability,
)

from ai.sustainability.model import (
    SustainabilityIntelligenceModel,
)


DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "datasets"
    / "sustainability"
    / "sustainability.csv"
)


def test_dataset_loading():

    df = load_dataset(
        DATASET_PATH
    )

    assert not df.empty
    assert len(df) == 30

    print(
        "Dataset loading test passed."
    )


def test_dataset_validation():

    df = load_dataset(
        DATASET_PATH
    )

    assert validate_dataset(df)

    print(
        "Dataset validation test passed."
    )


def test_feature_engineering():

    df = load_dataset(
        DATASET_PATH
    )

    features = (
        create_sustainability_features(
            df
        )
    )

    assert (
        "material_sustainability"
        in features.columns
    )

    assert (
        "waste_ratio"
        in features.columns
    )

    assert (
        "energy_per_kg"
        in features.columns
    )

    print(
        "Feature engineering test passed."
    )


def test_material_score():

    df = load_dataset(
        DATASET_PATH
    )

    features = (
        create_sustainability_features(
            df
        )
    )

    bamboo = features[
        features["material"]
        == "bamboo"
    ].iloc[0]

    assert (
        bamboo[
            "material_sustainability"
        ]
        == 95
    )

    print(
        "Material sustainability test passed."
    )


def test_packaging_score():

    df = load_dataset(
        DATASET_PATH
    )

    features = (
        create_sustainability_features(
            df
        )
    )

    assert (
        features["packaging_score"]
        .min()
        >= 20
    )

    print(
        "Packaging score test passed."
    )


def test_waste_ratio():

    df = load_dataset(
        DATASET_PATH
    )

    features = (
        create_sustainability_features(
            df
        )
    )

    row = features.iloc[0]

    expected = (
        row["waste_kg"]
        / row["material_weight_kg"]
    )

    assert abs(
        row["waste_ratio"]
        - expected
    ) < 0.0001

    print(
        "Waste ratio test passed."
    )


def test_energy_per_kg():

    df = load_dataset(
        DATASET_PATH
    )

    features = (
        create_sustainability_features(
            df
        )
    )

    row = features.iloc[0]

    expected = (
        row["production_energy_kwh"]
        / row["material_weight_kg"]
    )

    assert abs(
        row["energy_per_kg"]
        - expected
    ) < 0.0001

    print(
        "Energy intensity test passed."
    )


def test_feature_columns():

    columns = get_feature_columns()

    assert (
        "material_sustainability"
        in columns
    )

    assert (
        "transport_pressure"
        in columns
    )

    print(
        "Feature column test passed."
    )


def test_sustainability_score():

    df = load_dataset(
        DATASET_PATH
    )

    features = (
        create_sustainability_features(
            df
        )
    )

    result = (
        calculate_sustainability_score(
            features.iloc[0]
        )
    )

    assert 0 <= (
        result["sustainability_score"]
    ) <= 100

    assert result[
        "sustainability_level"
    ] in {
        "HIGH",
        "MEDIUM",
        "LOW",
    }

    print(
        "Sustainability score test passed."
    )


def test_carbon_estimation():

    df = load_dataset(
        DATASET_PATH
    )

    features = (
        create_sustainability_features(
            df
        )
    )

    carbon = estimate_carbon_impact(
        features.iloc[0]
    )

    assert carbon > 0

    print(
        "Carbon estimation test passed."
    )


def test_recommendations():

    df = load_dataset(
        DATASET_PATH
    )

    features = (
        create_sustainability_features(
            df
        )
    )

    score = (
        calculate_sustainability_score(
            features.iloc[0]
        )
    )

    recommendations = (
        generate_recommendations(
            features.iloc[0],
            score,
        )
    )

    assert isinstance(
        recommendations,
        list,
    )

    assert len(
        recommendations
    ) > 0

    print(
        "Recommendation generation test passed."
    )


def test_complete_analysis():

    df = load_dataset(
        DATASET_PATH
    )

    results = analyze_sustainability(
        df
    )

    assert len(results) == len(df)

    for result in results:

        assert (
            0
            <= result[
                "sustainability_score"
            ]
            <= 100
        )

        assert (
            result[
                "estimated_carbon_kg_co2e"
            ]
            > 0
        )

        assert len(
            result["recommendations"]
        ) > 0

    print(
        "Complete sustainability analysis test passed."
    )


def test_model_creation():

    model = (
        SustainabilityIntelligenceModel()
    )

    assert (
        model.model_name
        == "Sustainability Intelligence AI"
    )

    assert (
        model.model_version
        == "1.0.0"
    )

    print(
        "Model creation test passed."
    )


def test_model_analysis():

    df = load_dataset(
        DATASET_PATH
    )

    model = (
        SustainabilityIntelligenceModel()
    )

    results = model.analyze(
        df.head(5)
    )

    assert len(results) == 5

    print(
        "Model analysis test passed."
    )


def test_model_save_load():

    import tempfile

    model = (
        SustainabilityIntelligenceModel()
    )

    with tempfile.TemporaryDirectory() as directory:

        path = (
            Path(directory)
            / "sustainability.joblib"
        )

        model.save(path)

        loaded = (
            SustainabilityIntelligenceModel.load(
                path
            )
        )

        assert (
            loaded.model_name
            == model.model_name
        )

        assert (
            loaded.model_version
            == model.model_version
        )

    print(
        "Model save/load test passed."
    )


def run_tests():

    tests = [
        test_dataset_loading,
        test_dataset_validation,
        test_feature_engineering,
        test_material_score,
        test_packaging_score,
        test_waste_ratio,
        test_energy_per_kg,
        test_feature_columns,
        test_sustainability_score,
        test_carbon_estimation,
        test_recommendations,
        test_complete_analysis,
        test_model_creation,
        test_model_analysis,
        test_model_save_load,
    ]

    passed = 0
    failed = 0

    for test in tests:

        try:
            test()
            passed += 1

        except Exception as error:

            failed += 1

            print(
                f"{test.__name__} failed: "
                f"{error}"
            )

    print()
    print("-" * 60)
    print(
        f"Tests passed: {passed}"
    )
    print(
        f"Tests failed: {failed}"
    )
    print("-" * 60)

    if failed == 0:

        print()
        print(
            "ALL MODEL 14 TESTS PASSED"
        )
        print("=" * 60)

        return 0

    print()
    print(
        "MODEL 14 TESTS FAILED"
    )

    return 1


if __name__ == "__main__":

    print()
    print("=" * 60)
    print(
        "KALASETU MODEL 14 "
        "SUSTAINABILITY INTELLIGENCE AI TESTS"
    )
    print("=" * 60)

    raise SystemExit(
        run_tests()
    )