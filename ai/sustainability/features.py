import numpy as np
import pandas as pd

from .config import (
    LOCAL_SOURCING_SCORE,
    MATERIAL_SUSTAINABILITY,
    PACKAGING_SUSTAINABILITY,
    RECYCLABILITY_SCORE,
)


def create_sustainability_features(df):

    data = df.copy()

    data["material_sustainability"] = (
        data["material"]
        .str.lower()
        .map(MATERIAL_SUSTAINABILITY)
        .fillna(50)
    )

    data["packaging_score"] = (
        data["packaging_type"]
        .str.lower()
        .map(PACKAGING_SUSTAINABILITY)
        .fillna(50)
    )

    data["recyclability_score"] = (
        data["recyclability"]
        .str.lower()
        .map(RECYCLABILITY_SCORE)
        .fillna(50)
    )

    data["local_sourcing_score"] = (
        data["local_sourcing"]
        .str.lower()
        .map(LOCAL_SOURCING_SCORE)
        .fillna(50)
    )

    data["waste_ratio"] = (
        data["waste_kg"]
        / data["material_weight_kg"].replace(
            0,
            0.1,
        )
    )

    data["energy_per_kg"] = (
        data["production_energy_kwh"]
        / data["material_weight_kg"].replace(
            0,
            0.1,
        )
    )

    data["transport_pressure"] = (
        data["transport_distance_km"]
        / 1000.0
    )

    data = data.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    data = data.fillna(0)

    return data


def get_feature_columns():

    return [
        "material_sustainability",
        "packaging_score",
        "recyclability_score",
        "local_sourcing_score",
        "waste_ratio",
        "energy_per_kg",
        "transport_pressure",
    ]