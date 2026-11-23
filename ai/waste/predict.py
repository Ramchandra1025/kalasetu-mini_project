import argparse
import json

from .scoring import score_waste


def main():

    parser = argparse.ArgumentParser(
        description=(
            "KalaSetu Waste Intelligence AI"
        )
    )

    parser.add_argument(
        "--material",
        required=True,
    )

    parser.add_argument(
        "--craft-category",
        required=True,
    )

    parser.add_argument(
        "--quantity",
        type=float,
        required=True,
    )

    parser.add_argument(
        "--condition",
        type=float,
        required=True,
    )

    parser.add_argument(
        "--compatibility",
        type=float,
        required=True,
    )

    parser.add_argument(
        "--demand",
        type=float,
        required=True,
    )

    parser.add_argument(
        "--processing",
        type=float,
        required=True,
    )

    args = parser.parse_args()

    row = {
        "waste_id": "prediction",
        "craft_category": args.craft_category,
        "material": args.material,
        "waste_quantity_kg": args.quantity,
        "condition_score": args.condition,
        "reuse_compatibility": args.compatibility,
        "demand_score": args.demand,
        "processing_effort": args.processing,
        "disposal_cost": 0,
        "expected_reuse_value": 0,
    }

    result = score_waste(row)

    print("=" * 60)
    print(
        "KALASETU WASTE INTELLIGENCE PREDICTION"
    )
    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=4,
        )
    )

    print("\nResearch valid: False")

    print(
        "Note: This prototype uses explainable "
        "scoring and synthetic/prototype assumptions."
    )


if __name__ == "__main__":
    main()