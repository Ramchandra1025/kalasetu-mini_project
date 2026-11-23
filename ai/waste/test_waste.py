import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from ai.waste.dataset import (
    load_dataset,
    validate_dataset,
)

from ai.waste.features import (
    build_features,
)

from ai.waste.scoring import (
    calculate_reuse_score,
    classify_feasibility,
    recommend_reuse_options,
    estimate_recoverable_value,
    score_waste,
)


def test_dataset():

    df = load_dataset()

    assert len(df) == 24

    validation = validate_dataset(df)

    assert validation["valid"] is True

    print(
        f"Dataset: {len(df)} rows, "
        f"{len(df.columns)} columns"
    )


def test_features():

    df = load_dataset()

    features = build_features(df)

    assert "quantity_score" in features.columns
    assert "processing_ease" in features.columns
    assert "material_reuse_score" in features.columns
    assert "reuse_potential" in features.columns

    assert len(features) == len(df)

    print(
        f"Features: {len(features.columns)} columns"
    )


def test_score():

    row = {
        "waste_id": "TEST001",
        "craft_category": "wood_craft",
        "material": "wood",
        "waste_quantity_kg": 5.0,
        "condition_score": 90,
        "reuse_compatibility": 92,
        "demand_score": 85,
        "processing_effort": 20,
        "disposal_cost": 100,
        "expected_reuse_value": 0,
    }

    result = score_waste(row)

    assert 0 <= result["reuse_score"] <= 100

    assert result["feasibility"] in [
        "HIGH",
        "MEDIUM",
        "LOW",
    ]

    assert len(
        result["recommended_reuse"]
    ) > 0

    assert (
        result["estimated_recoverable_value"]
        > 0
    )

    print(
        f"Reuse Score: "
        f"{result['reuse_score']}"
    )

    print(
        f"Feasibility: "
        f"{result['feasibility']}"
    )

    print(
        f"Reuse options: "
        f"{result['recommended_reuse']}"
    )

    print(
        f"Estimated value: ₹"
        f"{result['estimated_recoverable_value']}"
    )


def test_score_boundaries():

    low_score = calculate_reuse_score(
        material_reuse=20,
        quantity=0.5,
        condition=20,
        compatibility=20,
        demand=20,
        processing=90,
    )

    high_score = calculate_reuse_score(
        material_reuse=100,
        quantity=10,
        condition=100,
        compatibility=100,
        demand=100,
        processing=0,
    )

    assert 0 <= low_score <= 100
    assert 0 <= high_score <= 100

    assert high_score > low_score

    assert classify_feasibility(
        high_score
    ) == "HIGH"

    assert classify_feasibility(
        low_score
    ) == "LOW"

    print(
        f"Boundary scores: "
        f"low={low_score}, high={high_score}"
    )


def test_reuse_options():

    options = recommend_reuse_options(
        material="wood",
        score=90,
        demand_score=90,
        condition_score=90,
    )

    assert len(options) >= 1

    print(
        f"Wood reuse options: {options}"
    )


def test_value_estimation():

    value = estimate_recoverable_value(
        material="wood",
        quantity=5,
        score=80,
    )

    assert value > 0

    print(
        f"Estimated recoverable value: ₹{value}"
    )


if __name__ == "__main__":

    print("=" * 60)
    print("KALASETU MODEL 7 TEST")
    print("WASTE INTELLIGENCE AI")
    print("=" * 60)

    test_dataset()
    test_features()
    test_score()
    test_score_boundaries()
    test_reuse_options()
    test_value_estimation()

    print("\n" + "=" * 60)
    print("ALL WASTE INTELLIGENCE TESTS PASSED")
    print("=" * 60)