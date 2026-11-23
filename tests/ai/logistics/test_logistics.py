import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from ai.logistics.dataset import (
    load_dataset,
    validate_dataset,
)

from ai.logistics.features import (
    create_location_features,
    haversine_distance,
    create_distance_matrix,
    estimate_route_time,
)

from ai.logistics.model import (
    SmartLogisticsModel,
)

from ai.logistics.train import (
    main as train_main,
)

from ai.logistics.predict import (
    main as predict_main,
)


DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "datasets"
    / "logistics"
    / "logistics.csv"
)


def test_dataset_loading():

    df = load_dataset(
        DATASET_PATH
    )

    assert not df.empty
    assert len(df) == 20

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


def test_location_features():

    df = load_dataset(
        DATASET_PATH
    )

    features = create_location_features(
        df
    )

    assert "priority_score" in features.columns
    assert len(features) == len(df)

    print(
        "Location feature test passed."
    )


def test_haversine_distance():

    distance = haversine_distance(
        12.9716,
        77.5946,
        12.9352,
        77.6245,
    )

    assert distance > 0
    assert distance < 10

    print(
        "Haversine distance test passed."
    )


def test_distance_matrix():

    df = load_dataset(
        DATASET_PATH
    )

    matrix = create_distance_matrix(
        df
    )

    assert matrix.shape == (
        len(df),
        len(df),
    )

    assert np.allclose(
        np.diag(matrix),
        0,
    )

    print(
        "Distance matrix test passed."
    )


def test_distance_symmetry():

    df = load_dataset(
        DATASET_PATH
    )

    matrix = create_distance_matrix(
        df
    )

    assert np.allclose(
        matrix,
        matrix.T,
        atol=1e-6,
    )

    print(
        "Distance symmetry test passed."
    )


def test_route_time():

    time = estimate_route_time(
        30,
        30,
    )

    assert time == 60

    print(
        "Route time estimation test passed."
    )


def test_model_creation():

    model = SmartLogisticsModel()

    assert model.vehicle_count == 4
    assert model.vehicle_capacity == 10
    assert model.cluster_count == 2

    print(
        "Model creation test passed."
    )


def test_cluster_training():

    df = load_dataset(
        DATASET_PATH
    )

    coordinates = df[
        ["latitude", "longitude"]
    ].values

    model = SmartLogisticsModel()

    model.fit_clusters(
        coordinates
    )

    clusters = model.predict_clusters(
        coordinates
    )

    assert len(clusters) == len(df)
    assert len(set(clusters)) == 2

    print(
        "Geographic clustering test passed."
    )


def test_route_optimization():

    df = load_dataset(
        DATASET_PATH
    )

    matrix = create_distance_matrix(
        df
    )

    demands = (
        df["package_weight"]
        .round()
        .astype(int)
        .tolist()
    )

    model = SmartLogisticsModel()

    result = model.optimize_route(
        matrix,
        demands,
    )

    assert result["total_distance_km"] > 0
    assert len(result["routes"]) > 0

    print(
        "VRP route optimization test passed."
    )


def test_route_validity():

    df = load_dataset(
        DATASET_PATH
    )

    matrix = create_distance_matrix(
        df
    )

    demands = (
        df["package_weight"]
        .round()
        .astype(int)
        .tolist()
    )

    model = SmartLogisticsModel()

    result = model.optimize_route(
        matrix,
        demands,
    )

    visited = []

    for route in result["routes"]:

        assert route[0] == 0
        assert route[-1] == 0

        visited.extend(
            node
            for node in route
            if node != 0
        )

    assert set(visited) == set(
        range(1, len(df))
    )

    print(
        "Route validity test passed."
    )


def test_model_save_load():

    import tempfile

    df = load_dataset(
        DATASET_PATH
    )

    coordinates = df[
        ["latitude", "longitude"]
    ].values

    model = SmartLogisticsModel()

    model.fit_clusters(
        coordinates
    )

    with tempfile.TemporaryDirectory() as directory:

        path = (
            Path(directory)
            / "logistics.joblib"
        )

        model.save(path)

        loaded = (
            SmartLogisticsModel.load(path)
        )

        predictions = (
            loaded.predict_clusters(
                coordinates
            )
        )

        assert len(predictions) == len(
            df
        )

    print(
        "Model save/load test passed."
    )


def run_tests():

    tests = [
        test_dataset_loading,
        test_dataset_validation,
        test_location_features,
        test_haversine_distance,
        test_distance_matrix,
        test_distance_symmetry,
        test_route_time,
        test_model_creation,
        test_cluster_training,
        test_route_optimization,
        test_route_validity,
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
            "ALL MODEL 13 TESTS PASSED"
        )
        print("=" * 60)

        return 0

    print()
    print(
        "MODEL 13 TESTS FAILED"
    )

    return 1


if __name__ == "__main__":

    print()
    print("=" * 60)
    print(
        "KALASETU MODEL 13 "
        "SMART LOGISTICS AI TESTS"
    )
    print("=" * 60)

    raise SystemExit(
        run_tests()
    )