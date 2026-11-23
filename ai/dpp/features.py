import pandas as pd


def normalize_text(value):
    if value is None:
        return ""

    if pd.isna(value):
        return ""

    return str(value).strip()


def is_present(value):
    return bool(normalize_text(value))


def calculate_completeness(record):
    identity_complete = all(
        is_present(record.get(field))
        for field in [
            "product_id",
            "product_name",
        ]
    )

    artisan_complete = all(
        is_present(record.get(field))
        for field in [
            "artisan_id",
            "artisan_name",
        ]
    )

    craft_complete = all(
        is_present(record.get(field))
        for field in [
            "craft_category",
            "material",
        ]
    )

    origin_complete = all(
        is_present(record.get(field))
        for field in [
            "origin_state",
            "origin_district",
        ]
    )

    production_complete = all(
        is_present(record.get(field))
        for field in [
            "production_method",
            "material_source",
        ]
    )

    sustainability_complete = (
        record.get("sustainability_score") is not None
        and record.get("carbon_impact_kg_co2e") is not None
    )

    sections = {
        "identity": identity_complete,
        "artisan": artisan_complete,
        "craft": craft_complete,
        "origin": origin_complete,
        "production": production_complete,
        "sustainability": sustainability_complete,
    }

    return sections


def calculate_completeness_score(record):
    sections = calculate_completeness(record)

    weights = {
        "identity": 0.20,
        "artisan": 0.15,
        "craft": 0.15,
        "origin": 0.15,
        "production": 0.15,
        "sustainability": 0.20,
    }

    score = sum(
        weights[key]
        for key, complete in sections.items()
        if complete
    )

    return round(score * 100, 2)


def generate_missing_fields(record):
    fields = [
        "product_id",
        "product_name",
        "artisan_id",
        "artisan_name",
        "craft_category",
        "material",
        "origin_state",
        "origin_district",
        "production_method",
        "material_source",
        "sustainability_score",
        "carbon_impact_kg_co2e",
    ]

    missing = []

    for field in fields:
        value = record.get(field)

        if value is None:
            missing.append(field)
            continue

        if isinstance(value, str) and not value.strip():
            missing.append(field)

    return missing


def get_trust_level(completeness_score, verified):
    if verified and completeness_score >= 90:
        return "HIGH"

    if completeness_score >= 70:
        return "MEDIUM"

    return "LOW"