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


from ai.inventory.dataset import (
    load_dataset,
    validate_dataset,
)

from ai.inventory.features import (
    create_inventory_features,
    encode_features,
)

from ai.inventory.model import (
    InventoryIntelligenceModel,
)

from ai.inventory.train import (
    create_inventory_label,
)

from ai.inventory.predict import (
    calculate_inventory_intelligence,
)


passed = 0
failed = 0


def run_test(name, function):

    global passed
    global failed

    try:

        function()

        print(
            f"{name} test passed."
        )

        passed += 1

    except Exception as error:

        print(
            f"{name} test FAILED: {error}"
        )

        failed += 1


def test_dataset_loading():

    df = load_dataset()

    assert len(df) == 30

    assert "current_stock" in df.columns

    assert "recent_daily_sales" in df.columns


def test_dataset_validation():

    df = load_dataset()

    assert validate_dataset(df) is True


def test_feature_engineering():

    df = load_dataset()

    result = create_inventory_features(df)

    assert (
        "stock_coverage_days"
        in result.columns
    )

    assert (
        "reorder_point"
        in result.columns
    )

    assert (
        "inventory_gap"
        in result.columns
    )


def test_sales_momentum():

    df = load_dataset()

    result = create_inventory_features(df)

    expected = (
        df["recent_daily_sales"]
        - df["average_daily_sales"]
    )

    assert np.allclose(
        result["sales_momentum"],
        expected,
    )


def test_stock_coverage():

    df = load_dataset()

    result = create_inventory_features(df)

    assert (
        result["stock_coverage_days"]
        .notna()
        .all()
    )


def test_reorder_point():

    df = load_dataset()

    result = create_inventory_features(df)

    expected = (
        df["recent_daily_sales"]
        * df["lead_time_days"]
        + df["recent_daily_sales"] * 3
    )

    assert np.allclose(
        result["reorder_point"],
        expected,
    )


def test_feature_encoding():

    df = load_dataset()

    X = encode_features(df)

    assert X.shape[0] == 30

    assert X.shape[1] > 15

    assert X.isna().sum().sum() == 0


def test_stock_label_generation():

    df = load_dataset()

    labels = df.apply(
        create_inventory_label,
        axis=1,
    )

    valid_labels = {
        "CRITICAL",
        "LOW_STOCK",
        "HEALTHY",
        "OVERSTOCK",
    }

    assert set(labels).issubset(
        valid_labels
    )


def test_model_creation():

    model = InventoryIntelligenceModel()

    assert model.model is not None


def test_model_training():

    df = load_dataset()

    df["stock_status"] = df.apply(
        create_inventory_label,
        axis=1,
    )

    X = encode_features(df)

    y = df["stock_status"]

    model = InventoryIntelligenceModel()

    model.fit(
        X,
        y,
    )

    predictions = model.predict(X)

    assert len(predictions) == len(df)


def test_probability_prediction():

    df = load_dataset()

    df["stock_status"] = df.apply(
        create_inventory_label,
        axis=1,
    )

    X = encode_features(df)

    y = df["stock_status"]

    model = InventoryIntelligenceModel()

    model.fit(
        X,
        y,
    )

    probabilities = (
        model.predict_proba(X)
    )

    assert probabilities.shape[0] == 30

    assert np.allclose(
        probabilities.sum(axis=1),
        1.0,
        atol=1e-5,
    )


def test_inventory_intelligence():

    row = pd.Series(
        {
            "current_stock": 5,
            "minimum_stock": 10,
            "maximum_stock": 50,
            "average_daily_sales": 5,
            "recent_daily_sales": 8,
            "lead_time_days": 7,
            "demand_growth": 10,
        }
    )

    result = calculate_inventory_intelligence(
        row
    )

    assert (
        result["stock_coverage_days"]
        > 0
    )

    assert (
        result["reorder_point"]
        > 0
    )

    assert (
        result["recommended_reorder_quantity"]
        >= 0
    )


def test_model_save_load():

    df = load_dataset()

    df["stock_status"] = df.apply(
        create_inventory_label,
        axis=1,
    )

    X = encode_features(df)

    y = df["stock_status"]

    model = InventoryIntelligenceModel()

    model.fit(
        X,
        y,
    )

    temporary_path = (
        PROJECT_ROOT
        / "ml"
        / "models"
        / "inventory"
        / "test_inventory_model.joblib"
    )

    model.save(
        temporary_path
    )

    loaded = (
        InventoryIntelligenceModel.load(
            temporary_path
        )
    )

    predictions = loaded.predict(X)

    assert len(predictions) == 30

    temporary_path.unlink(
        missing_ok=True
    )


print()
print("=" * 60)
print(
    "KALASETU MODEL 12 INVENTORY INTELLIGENCE AI TESTS"
)
print("=" * 60)


run_test(
    "Dataset loading",
    test_dataset_loading,
)

run_test(
    "Dataset validation",
    test_dataset_validation,
)

run_test(
    "Feature engineering",
    test_feature_engineering,
)

run_test(
    "Sales momentum",
    test_sales_momentum,
)

run_test(
    "Stock coverage",
    test_stock_coverage,
)

run_test(
    "Reorder point",
    test_reorder_point,
)

run_test(
    "Feature encoding",
    test_feature_encoding,
)

run_test(
    "Stock label generation",
    test_stock_label_generation,
)

run_test(
    "Model creation",
    test_model_creation,
)

run_test(
    "Model training",
    test_model_training,
)

run_test(
    "Probability prediction",
    test_probability_prediction,
)

run_test(
    "Inventory intelligence",
    test_inventory_intelligence,
)

run_test(
    "Model save/load",
    test_model_save_load,
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
        "ALL MODEL 12 TESTS PASSED"
    )

else:

    print()
    print(
        "MODEL 12 TESTS REQUIRE FIXES"
    )

print("=" * 60)