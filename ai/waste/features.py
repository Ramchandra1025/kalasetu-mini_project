import pandas as pd


def build_features(df: pd.DataFrame) -> pd.DataFrame:

    data = df.copy()

    data["quantity_score"] = (
        data["waste_quantity_kg"]
        .clip(lower=0, upper=10)
        / 10
        * 100
    )

    data["processing_ease"] = (
        100 - data["processing_effort"]
    ).clip(0, 100)

    data["disposal_burden"] = (
        data["disposal_cost"]
        .clip(lower=0)
    )

    data["material_reuse_score"] = (
        data["reuse_compatibility"] * 0.7
        + data["condition_score"] * 0.3
    )

    data["reuse_potential"] = (
        data["material_reuse_score"] * 0.40
        + data["condition_score"] * 0.20
        + data["demand_score"] * 0.20
        + data["processing_ease"] * 0.20
    )

    return data