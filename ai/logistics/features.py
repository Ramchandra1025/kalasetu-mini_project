import math

import numpy as np
import pandas as pd


def create_location_features(df):
    data = df.copy()

    data["latitude"] = pd.to_numeric(
        data["latitude"],
        errors="coerce",
    )

    data["longitude"] = pd.to_numeric(
        data["longitude"],
        errors="coerce",
    )

    data["package_weight"] = pd.to_numeric(
        data["package_weight"],
        errors="coerce",
    )

    data["priority_score"] = (
        data["priority"]
        .map(
            {
                "HIGH": 3,
                "MEDIUM": 2,
                "LOW": 1,
            }
        )
        .fillna(1)
    )

    data = data.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    data = data.fillna(0)

    return data


def haversine_distance(
    latitude_1,
    longitude_1,
    latitude_2,
    longitude_2,
):
    radius_km = 6371.0

    lat1 = math.radians(latitude_1)
    lat2 = math.radians(latitude_2)

    delta_lat = math.radians(
        latitude_2 - latitude_1
    )

    delta_lon = math.radians(
        longitude_2 - longitude_1
    )

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a),
    )

    return radius_km * c


def create_distance_matrix(df):
    coordinates = list(
        zip(
            df["latitude"],
            df["longitude"],
        )
    )

    matrix = []

    for lat1, lon1 in coordinates:
        row = []

        for lat2, lon2 in coordinates:
            distance = haversine_distance(
                lat1,
                lon1,
                lat2,
                lon2,
            )

            row.append(round(distance, 4))

        matrix.append(row)

    return np.array(matrix)


def estimate_route_time(distance_km, speed_kmph=30):
    if speed_kmph <= 0:
        raise ValueError(
            "Speed must be greater than zero."
        )

    return (distance_km / speed_kmph) * 60