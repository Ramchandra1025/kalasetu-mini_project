from pathlib import Path

import joblib
import numpy as np
from sklearn.cluster import KMeans

from ortools.constraint_solver import (
    pywrapcp,
    routing_enums_pb2,
)

from .config import (
    CLUSTER_COUNT,
    DEFAULT_VEHICLE_CAPACITY,
    DEFAULT_VEHICLE_COUNT,
    RANDOM_SEED,
)


class SmartLogisticsModel:

    def __init__(
        self,
        vehicle_count=DEFAULT_VEHICLE_COUNT,
        vehicle_capacity=DEFAULT_VEHICLE_CAPACITY,
        cluster_count=CLUSTER_COUNT,
    ):
        self.vehicle_count = vehicle_count
        self.vehicle_capacity = vehicle_capacity
        self.cluster_count = cluster_count

        self.cluster_model = None

    def fit_clusters(self, coordinates):

        coordinates = np.asarray(
            coordinates,
            dtype=float,
        )

        cluster_count = min(
            self.cluster_count,
            len(coordinates),
        )

        self.cluster_model = KMeans(
            n_clusters=cluster_count,
            random_state=RANDOM_SEED,
            n_init=10,
        )

        self.cluster_model.fit(coordinates)

        return self

    def predict_clusters(self, coordinates):

        if self.cluster_model is None:
            raise RuntimeError(
                "Cluster model has not been fitted."
            )

        coordinates = np.asarray(
            coordinates,
            dtype=float,
        )

        return self.cluster_model.predict(
            coordinates
        )

    def optimize_route(
        self,
        distance_matrix,
        demands,
        depot_index=0,
    ):

        distance_matrix = np.asarray(
            distance_matrix,
            dtype=float,
        )

        demands = [
            int(max(0, round(value)))
            for value in demands
        ]

        node_count = len(distance_matrix)

        if node_count == 0:
            raise ValueError(
                "Distance matrix cannot be empty."
            )

        if len(demands) != node_count:
            raise ValueError(
                "Demand count must match matrix size."
            )

        manager = pywrapcp.RoutingIndexManager(
            node_count,
            self.vehicle_count,
            depot_index,
        )

        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(
            from_index,
            to_index,
        ):
            from_node = manager.IndexToNode(
                from_index
            )

            to_node = manager.IndexToNode(
                to_index
            )

            return int(
                round(
                    distance_matrix[
                        from_node
                    ][to_node]
                    * 1000
                )
            )

        distance_callback_index = (
            routing.RegisterTransitCallback(
                distance_callback
            )
        )

        routing.SetArcCostEvaluatorOfAllVehicles(
            distance_callback_index
        )

        def demand_callback(
            from_index,
        ):
            from_node = manager.IndexToNode(
                from_index
            )

            return demands[from_node]

        demand_callback_index = (
            routing.RegisterUnaryTransitCallback(
                demand_callback
            )
        )

        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,
            [self.vehicle_capacity]
            * self.vehicle_count,
            True,
            "Capacity",
        )

        search_parameters = (
            pywrapcp.DefaultRoutingSearchParameters()
        )

        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy
            .PATH_CHEAPEST_ARC
        )

        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic
            .GUIDED_LOCAL_SEARCH
        )

        search_parameters.time_limit.seconds = 5

        solution = routing.SolveWithParameters(
            search_parameters
        )

        if solution is None:
            raise RuntimeError(
                "No feasible logistics route found."
            )

        routes = []

        for vehicle_id in range(
            self.vehicle_count
        ):

            index = routing.Start(vehicle_id)

            route = []

            while not routing.IsEnd(index):

                node = manager.IndexToNode(index)

                route.append(node)

                index = solution.Value(
                    routing.NextVar(index)
                )

            route.append(
                manager.IndexToNode(index)
            )

            if len(route) > 2:
                routes.append(route)

        total_distance = 0.0

        for route in routes:
            for position in range(
                len(route) - 1
            ):
                total_distance += distance_matrix[
                    route[position]
                ][route[position + 1]]

        return {
            "routes": routes,
            "total_distance_km": round(
                total_distance,
                3,
            ),
            "vehicle_count": self.vehicle_count,
        }

    def save(self, path):

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        joblib.dump(
            {
                "vehicle_count": self.vehicle_count,
                "vehicle_capacity": self.vehicle_capacity,
                "cluster_count": self.cluster_count,
                "cluster_model": self.cluster_model,
            },
            path,
        )

    @classmethod
    def load(cls, path):

        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"Logistics model not found: {path}"
            )

        saved = joblib.load(path)

        instance = cls(
            vehicle_count=saved[
                "vehicle_count"
            ],
            vehicle_capacity=saved[
                "vehicle_capacity"
            ],
            cluster_count=saved[
                "cluster_count"
            ],
        )

        instance.cluster_model = saved[
            "cluster_model"
        ]

        return instance