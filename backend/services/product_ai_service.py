
"""Orchestrate KalaSetu product AI models.

Predictions based on synthetic data are explicitly labelled.
Missing inputs never receive fabricated production or sales values.
"""

from datetime import datetime, timezone
from typing import Any


def _model_result(status: str, **values: Any) -> dict:
    return {"status": status, **values}


def _normalise(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "_")


def _run_cataloguing(image_bytes: bytes | None) -> dict:
    if not image_bytes:
        return _model_result(
            "not_run",
            message="Upload a product image to run cataloguing.",
        )

    try:
        from ai.cataloguing.predict import predict_image_bytes

        prediction = predict_image_bytes(image_bytes)
        return _model_result(
            "completed",
            result=prediction,
            experimental=True,
            message="Review the image-derived suggestions before saving.",
        )
    except Exception:
        return _model_result(
            "failed",
            message="Cataloguing failed. You can still enter details manually.",
        )


def _run_pricing(data: dict) -> dict:
    required = (
        "size_cm",
        "production_hours",
        "material_cost",
        "labor_cost",
        "demand_score",
        "complexity_score",
        "craft_category",
        "material",
        "region",
    )
    missing = [key for key in required if data.get(key) in (None, "")]

    if missing:
        return _model_result(
            "needs_input",
            missing_fields=missing,
            message="Provide production, cost and market inputs to estimate a price.",
        )

    try:
        from ai.pricing.predict import predict_fair_price

        result = predict_fair_price(data)
        return _model_result("completed", result=result)
    except Exception:
        return _model_result(
            "failed",
            message="Pricing model could not produce a result.",
        )


def _run_demand(data: dict) -> dict:
    required = (
        "month",
        "historical_demand",
        "previous_demand",
        "price",
        "demand_growth",
        "product_category",
        "region",
        "season",
    )
    missing = [key for key in required if data.get(key) in (None, "")]

    if missing:
        return _model_result(
            "needs_input",
            missing_fields=missing,
            message="Historical demand and market context are required.",
        )

    try:
        from ai.demand.predict import predict_future_demand

        result = predict_future_demand(data)
        return _model_result("completed", result=result)
    except Exception:
        return _model_result(
            "failed",
            message="Demand model could not produce a result.",
        )


def _run_sustainability(data: dict, product_id: str = "new-product") -> dict:
    required = (
        "material_weight_kg",
        "production_energy_kwh",
        "waste_kg",
        "packaging_type",
        "transport_distance_km",
        "recyclability",
        "local_sourcing",
    )
    missing = [key for key in required if data.get(key) in (None, "")]

    if not data.get("material"):
        missing.append("material")

    if not data.get("craft_category"):
        missing.append("craft_category")

    if missing:
        return _model_result(
            "needs_input",
            missing_fields=sorted(set(missing)),
            message="Production and material details are needed for sustainability analysis.",
        )

    try:
        import pandas as pd

        from ai.sustainability.config import (
            MODEL_NAME,
            MODEL_PATH,
            MODEL_VERSION,
            RESEARCH_VALID,
        )
        from ai.sustainability.model import SustainabilityIntelligenceModel

        row = pd.DataFrame([{
            "product_id": product_id,
            "product_category": _normalise(data["craft_category"]),
            "material": _normalise(data["material"]),
            "material_weight_kg": float(data["material_weight_kg"]),
            "production_energy_kwh": float(data["production_energy_kwh"]),
            "waste_kg": float(data["waste_kg"]),
            "packaging_type": _normalise(data["packaging_type"]),
            "transport_distance_km": float(data["transport_distance_km"]),
            "recyclability": _normalise(data["recyclability"]),
            "local_sourcing": _normalise(data["local_sourcing"]),
        }])

        model = SustainabilityIntelligenceModel.load(MODEL_PATH)
        prediction = model.analyze(row)[0]

        return _model_result(
            "completed",
            result={
                "product_id": product_id,
                "product_category": _normalise(data["craft_category"]),
                "material": _normalise(data["material"]),
                "sustainability_score": prediction["sustainability_score"],
                "sustainability_level": prediction["sustainability_level"],
                "component_scores": prediction["component_scores"],
                "estimated_carbon_kg_co2e": prediction["estimated_carbon_kg_co2e"],
                "recommendations": prediction["recommendations"],
                "model": MODEL_NAME,
                "model_version": MODEL_VERSION,
                "research_valid": RESEARCH_VALID,
                "warning": (
                    "Prototype estimate using approximate emission factors; "
                    "not a certified life-cycle assessment."
                ),
            },
        )
    except Exception:
        return _model_result(
            "failed",
            message="Sustainability analysis could not produce a result.",
        )


def analyze_product(
    *,
    image_bytes: bytes | None = None,
    product_data: dict | None = None,
    product_id: str = "new-product",
) -> dict:
    """Run applicable models and return JSON-serialisable results."""

    data = dict(product_data or {})
    catalogue = _run_cataloguing(image_bytes)

    prediction = catalogue.get("result", {})
    category_prediction = prediction.get("category", {})
    material_prediction = prediction.get("material", {})
    color_prediction = prediction.get("color", {})

    # Use image predictions only as fallbacks. Never overwrite artisan input.
    data.setdefault(
        "craft_category",
        category_prediction.get("label"),
    )
    data.setdefault("material", material_prediction.get("label"))
    data.setdefault("color", color_prediction.get("label"))

    pricing = _run_pricing(data)
    demand = _run_demand(data)
    sustainability = _run_sustainability(data, product_id)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "experimental": True,
        "cataloguing": catalogue,
        "pricing": pricing,
        "demand": demand,
        "sustainability": sustainability,
        "notice": (
            "AI outputs are suggestions. Review them before use. "
            "Pricing and demand models currently use synthetic test data."
        ),
    }
