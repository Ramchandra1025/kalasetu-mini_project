import argparse
import json

import pandas as pd

from .config import (
    MODEL_NAME,
    MODEL_PATH,
    MODEL_VERSION,
    RESEARCH_VALID,
)

from .model import (
    SustainabilityIntelligenceModel,
)


def main():

    parser = argparse.ArgumentParser(
        description=(
            "KalaSetu Sustainability Intelligence prediction"
        )
    )

    parser.add_argument(
        "--product-id",
        default="prediction",
    )

    parser.add_argument(
        "--category",
        default="wood_craft",
    )

    parser.add_argument(
        "--material",
        default="wood",
    )

    parser.add_argument(
        "--material-weight",
        type=float,
        default=2.0,
    )

    parser.add_argument(
        "--energy",
        type=float,
        default=4.0,
    )

    parser.add_argument(
        "--waste",
        type=float,
        default=0.2,
    )

    parser.add_argument(
        "--packaging",
        default="paper",
    )

    parser.add_argument(
        "--distance",
        type=float,
        default=80,
    )

    parser.add_argument(
        "--recyclability",
        default="high",
    )

    parser.add_argument(
        "--sourcing",
        default="local",
    )

    args = parser.parse_args()

    row = pd.DataFrame(
        [
            {
                "product_id": args.product_id,
                "product_category": args.category,
                "material": args.material,
                "material_weight_kg": args.material_weight,
                "production_energy_kwh": args.energy,
                "waste_kg": args.waste,
                "packaging_type": args.packaging,
                "transport_distance_km": args.distance,
                "recyclability": args.recyclability,
                "local_sourcing": args.sourcing,
            }
        ]
    )

    model = (
        SustainabilityIntelligenceModel.load(
            MODEL_PATH
        )
    )

    result = model.analyze(
        row
    )[0]

    output = {
        "product_id": args.product_id,
        "product_category": args.category,
        "material": args.material,
        "sustainability_score": result[
            "sustainability_score"
        ],
        "sustainability_level": result[
            "sustainability_level"
        ],
        "component_scores": result[
            "component_scores"
        ],
        "estimated_carbon_kg_co2e": result[
            "estimated_carbon_kg_co2e"
        ],
        "recommendations": result[
            "recommendations"
        ],
        "model": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "research_valid": RESEARCH_VALID,
        "note": (
            "Prototype sustainability intelligence "
            "using synthetic data and approximate "
            "emission factors. Carbon estimates are "
            "decision-support estimates, not certified "
            "life-cycle assessment results."
        ),
    }

    print()

    print(
        json.dumps(
            output,
            indent=4,
        )
    )


if __name__ == "__main__":
    main()