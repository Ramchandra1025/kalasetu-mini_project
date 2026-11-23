from pathlib import Path

from ai.anomaly.config import MODEL_PATH

from ai.anomaly.dataset import (
    load_dataset,
    prepare_dataset,
    validate_dataset,
)

from ai.anomaly.features import (
    build_feature_matrix,
)

from ai.anomaly.model import (
    AnomalyDetector,
)


def test_dataset():

    df = load_dataset()

    validation = validate_dataset(df)

    assert validation["valid"], (
        f"Dataset validation failed: {validation}"
    )

    assert len(df) > 0

    prepared = prepare_dataset(df)

    assert len(prepared) > 0

    print(
        f"Dataset test passed: {len(prepared)} rows"
    )


def test_features():

    df = load_dataset()

    df = prepare_dataset(df)

    X = build_feature_matrix(df)

    assert len(X) == len(df)

    assert X.shape[1] > 0

    assert X.isnull().sum().sum() == 0

    print(
        f"Feature test passed: {X.shape[1]} features"
    )


def test_model():

    df = load_dataset()

    df = prepare_dataset(df)

    X = build_feature_matrix(df)

    detector = AnomalyDetector()

    detector.fit(X)

    predictions = detector.predict(X)

    scores = detector.anomaly_score(X)

    assert len(predictions) == len(df)

    assert len(scores) == len(df)

    assert all(
        prediction in [-1, 1]
        for prediction in predictions
    )

    assert all(
        0 <= score <= 100
        for score in scores
    )

    print("Model test passed.")


def test_save_load():

    df = load_dataset()

    df = prepare_dataset(df)

    X = build_feature_matrix(df)

    detector = AnomalyDetector()

    detector.fit(X)

    detector.save(MODEL_PATH)

    assert Path(MODEL_PATH).exists()

    loaded = AnomalyDetector.load(MODEL_PATH)

    predictions = loaded.predict(X)

    assert len(predictions) == len(df)

    print("Save/load test passed.")


def run_all_tests():

    print("=" * 60)
    print("KALASETU MODEL 8 TESTS")
    print("=" * 60)

    test_dataset()
    test_features()
    test_model()
    test_save_load()

    print()
    print("ALL MODEL 8 TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()