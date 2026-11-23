from typing import Dict, List

from .config import (
    WEIGHTS,
    HIGH_THRESHOLD,
    MEDIUM_THRESHOLD,
    VALUE_MULTIPLIERS,
)


REUSE_OPTIONS = {
    "wood": [
        "decorative_artifacts",
        "small_home_decor",
        "wooden_utility_items",
        "craft_components",
    ],
    "cotton": [
        "textile_accessories",
        "patchwork_products",
        "small_bags",
        "decorative_fabric_items",
    ],
    "clay": [
        "decorative_pottery",
        "small_planters",
        "ceramic_artifacts",
        "mosaic_components",
    ],
    "metal": [
        "decorative_metal_artifacts",
        "jewellery_components",
        "utility_items",
        "craft_components",
    ],
}


def _clamp(
    value: float,
    minimum: float = 0,
    maximum: float = 100,
) -> float:

    return max(
        minimum,
        min(maximum, value)
    )


def calculate_reuse_score(
    material_reuse: float,
    quantity: float,
    condition: float,
    compatibility: float,
    demand: float,
    processing: float,
) -> float:

    quantity_score = _clamp(
        quantity / 10.0 * 100
    )

    processing_score = _clamp(
        100 - processing
    )

    score = (
        material_reuse * WEIGHTS["material_reuse"]
        + quantity_score * WEIGHTS["quantity"]
        + condition * WEIGHTS["condition"]
        + compatibility * WEIGHTS["compatibility"]
        + demand * WEIGHTS["demand"]
        + processing_score * WEIGHTS["processing"]
    )

    return round(
        _clamp(score),
        2
    )


def classify_feasibility(score: float) -> str:

    if score >= HIGH_THRESHOLD:
        return "HIGH"

    if score >= MEDIUM_THRESHOLD:
        return "MEDIUM"

    return "LOW"


def recommend_reuse_options(
    material: str,
    score: float,
    demand_score: float,
    condition_score: float,
) -> List[str]:

    options = REUSE_OPTIONS.get(
        material.lower(),
        ["custom_reuse_product"],
    )

    if (
        score >= HIGH_THRESHOLD
        and demand_score >= 70
        and condition_score >= 70
    ):
        return options[:3]

    if score >= MEDIUM_THRESHOLD:
        return options[:2]

    return options[:1]


def estimate_recoverable_value(
    material: str,
    quantity: float,
    score: float,
) -> float:

    multiplier = VALUE_MULTIPLIERS.get(
        material.lower(),
        100.0,
    )

    value = (
        quantity
        * multiplier
        * (score / 100)
    )

    return round(value, 2)


def generate_explanation(
    material: str,
    quantity: float,
    condition: float,
    compatibility: float,
    demand: float,
    processing: float,
    score: float,
    feasibility: str,
) -> str:

    reasons = []

    if compatibility >= 75:
        reasons.append(
            "high material reuse compatibility"
        )
    elif compatibility >= 50:
        reasons.append(
            "moderate material reuse compatibility"
        )
    else:
        reasons.append(
            "limited material reuse compatibility"
        )

    if condition >= 75:
        reasons.append(
            "good waste condition"
        )
    elif condition >= 50:
        reasons.append(
            "usable waste condition"
        )
    else:
        reasons.append(
            "damaged waste condition"
        )

    if demand >= 70:
        reasons.append(
            "strong product demand signal"
        )
    elif demand >= 50:
        reasons.append(
            "moderate product demand signal"
        )

    if processing <= 30:
        reasons.append(
            "low processing effort"
        )
    elif processing >= 70:
        reasons.append(
            "high processing effort"
        )

    return (
        f"{material} waste with {quantity:.2f} kg quantity "
        f"received a reuse score of {score:.2f} ({feasibility}) "
        f"because of "
        + ", ".join(reasons)
        + "."
    )


def score_waste(row: Dict) -> Dict:

    material = str(
        row["material"]
    ).lower()

    material_reuse = float(
        row["reuse_compatibility"]
    )

    quantity = float(
        row["waste_quantity_kg"]
    )

    condition = float(
        row["condition_score"]
    )

    compatibility = float(
        row["reuse_compatibility"]
    )

    demand = float(
        row["demand_score"]
    )

    processing = float(
        row["processing_effort"]
    )

    score = calculate_reuse_score(
        material_reuse=material_reuse,
        quantity=quantity,
        condition=condition,
        compatibility=compatibility,
        demand=demand,
        processing=processing,
    )

    feasibility = classify_feasibility(
        score
    )

    options = recommend_reuse_options(
        material=material,
        score=score,
        demand_score=demand,
        condition_score=condition,
    )

    estimated_value = estimate_recoverable_value(
        material=material,
        quantity=quantity,
        score=score,
    )

    explanation = generate_explanation(
        material=material,
        quantity=quantity,
        condition=condition,
        compatibility=compatibility,
        demand=demand,
        processing=processing,
        score=score,
        feasibility=feasibility,
    )

    return {
        "waste_id": row.get("waste_id"),
        "craft_category": row.get(
            "craft_category"
        ),
        "material": material,
        "waste_quantity_kg": quantity,
        "reuse_score": score,
        "feasibility": feasibility,
        "recommended_reuse": options,
        "estimated_recoverable_value": estimated_value,
        "value_note": (
            "Prototype estimate; "
            "not a guaranteed market value."
        ),
        "explanation": explanation,
    }