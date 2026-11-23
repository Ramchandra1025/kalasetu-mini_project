"""Fair-price inference using the persisted model pipeline."""
import argparse
import json
import numpy as np
import pandas as pd

from .config import (
    NUMERIC_FEATURES, CATEGORICAL_FEATURES, MODEL_FEATURES,
    ROUND_PRICE_TO, MIN_PREDICTED_PRICE,
)
from .features import engineer_features
from .model import load_model, predict_price


def prepare_input(product_data, encoder=None):
    required = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    missing = [key for key in required if key not in product_data or product_data[key] in (None, "")]
    if missing:
        raise ValueError("Missing required pricing fields: " + ", ".join(missing))

    row = pd.DataFrame([{**product_data}])
    for column in NUMERIC_FEATURES:
        row[column] = pd.to_numeric(row[column], errors="coerce")
        if row[column].isna().any() or not np.isfinite(row[column].iloc[0]):
            raise ValueError(f"Invalid numeric value for '{column}'.")
    for column in CATEGORICAL_FEATURES:
        row[column] = row[column].astype(str).str.strip().str.lower()
    engineered = engineer_features(row)
    return engineered[MODEL_FEATURES]


def predict_fair_price(product_data):
    model = load_model()
    features = prepare_input(product_data)
    prediction = float(predict_price(model, features)[0])
    prediction = max(prediction, MIN_PREDICTED_PRICE)
    if ROUND_PRICE_TO > 0:
        prediction = round(prediction / ROUND_PRICE_TO) * ROUND_PRICE_TO

    return {
        "recommended_price": float(prediction),
        "currency": "INR",
        "model": "XGBRegressor",
        "model_version": "2.0.0",
        "data_type": "synthetic_pipeline_testing_data",
        "research_valid": False,
        "warning": (
            "Prototype estimate from a synthetic pipeline-testing dataset. "
            "It is not a verified market price or a substitute for artisan review."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description="KalaSetu Fair Pricing")
    parser.add_argument("--craft-category", required=True)
    parser.add_argument("--material", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--size", required=True, type=float)
    parser.add_argument("--hours", required=True, type=float)
    parser.add_argument("--material-cost", required=True, type=float)
    parser.add_argument("--labor-cost", required=True, type=float)
    parser.add_argument("--demand", required=True, type=float)
    parser.add_argument("--complexity", required=True, type=float)
    args = parser.parse_args()

    product = {
        "craft_category": args.craft_category,
        "material": args.material,
        "region": args.region,
        "size_cm": args.size,
        "production_hours": args.hours,
        "material_cost": args.material_cost,
        "labor_cost": args.labor_cost,
        "demand_score": args.demand,
        "complexity_score": args.complexity,
    }
    print(json.dumps(predict_fair_price(product), indent=2))


if __name__ == "__main__":
    main()
