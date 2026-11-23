from .config import MATERIAL_CARBON_FACTOR
from .features import create_sustainability_features


def clamp(value, minimum=0, maximum=100):

    return max(
        minimum,
        min(maximum, value),
    )


def calculate_sustainability_score(row):

    material_score = float(
        row["material_sustainability"]
    )

    packaging_score = float(
        row["packaging_score"]
    )

    recyclability_score = float(
        row["recyclability_score"]
    )

    local_score = float(
        row["local_sourcing_score"]
    )

    waste_ratio = float(
        row["waste_ratio"]
    )

    energy_per_kg = float(
        row["energy_per_kg"]
    )

    transport_distance = float(
        row["transport_distance_km"]
    )

    waste_score = clamp(
        100 - (waste_ratio * 100)
    )

    energy_score = clamp(
        100 - (energy_per_kg * 15)
    )

    transport_score = clamp(
        100 - (transport_distance / 10)
    )

    score = (
        material_score * 0.25
        + waste_score * 0.15
        + energy_score * 0.15
        + packaging_score * 0.10
        + transport_score * 0.15
        + recyclability_score * 0.10
        + local_score * 0.10
    )

    score = clamp(score)

    if score >= 80:
        level = "HIGH"
    elif score >= 60:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "sustainability_score": round(
            score,
            2,
        ),
        "sustainability_level": level,
        "component_scores": {
            "material": round(
                material_score,
                2,
            ),
            "waste": round(
                waste_score,
                2,
            ),
            "energy": round(
                energy_score,
                2,
            ),
            "packaging": round(
                packaging_score,
                2,
            ),
            "transport": round(
                transport_score,
                2,
            ),
            "recyclability": round(
                recyclability_score,
                2,
            ),
            "local_sourcing": round(
                local_score,
                2,
            ),
        },
    }


def estimate_carbon_impact(row):

    material = str(
        row["material"]
    ).lower()

    material_weight = float(
        row["material_weight_kg"]
    )

    energy = float(
        row["production_energy_kwh"]
    )

    transport_distance = float(
        row["transport_distance_km"]
    )

    material_factor = (
        MATERIAL_CARBON_FACTOR.get(
            material,
            1.5,
        )
    )

    material_carbon = (
        material_weight
        * material_factor
    )

    energy_carbon = (
        energy
        * 0.7
    )

    transport_carbon = (
        transport_distance
        * 0.00015
    )

    total_carbon = (
        material_carbon
        + energy_carbon
        + transport_carbon
    )

    return round(
        total_carbon,
        3,
    )


def generate_recommendations(row, result):

    recommendations = []

    if result["component_scores"]["material"] < 60:
        recommendations.append(
            "Consider a more sustainable or renewable material."
        )

    if result["component_scores"]["waste"] < 60:
        recommendations.append(
            "Reduce production waste or reuse leftover material."
        )

    if result["component_scores"]["energy"] < 60:
        recommendations.append(
            "Reduce production energy consumption."
        )

    if result["component_scores"]["packaging"] < 60:
        recommendations.append(
            "Use recyclable or biodegradable packaging."
        )

    if result["component_scores"]["transport"] < 60:
        recommendations.append(
            "Consider shorter delivery routes or consolidated shipments."
        )

    if result["component_scores"]["recyclability"] < 60:
        recommendations.append(
            "Improve recyclability of the final product."
        )

    if result["component_scores"]["local_sourcing"] < 60:
        recommendations.append(
            "Prefer locally or regionally sourced materials."
        )

    if not recommendations:
        recommendations.append(
            "Current sustainability profile is strong; maintain the existing practices."
        )

    return recommendations


def analyze_sustainability(df):

    features = create_sustainability_features(
        df
    )

    results = []

    for index, row in features.iterrows():

        score = calculate_sustainability_score(
            row
        )

        carbon = estimate_carbon_impact(
            row
        )

        recommendations = (
            generate_recommendations(
                row,
                score,
            )
        )

        results.append(
            {
                "product_id": row["product_id"],
                **score,
                "estimated_carbon_kg_co2e": carbon,
                "recommendations": recommendations,
            }
        )

    return results