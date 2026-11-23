from pathlib import Path

import joblib
import numpy as np

from sklearn.ensemble import IsolationForest

from .config import (
    N_ESTIMATORS,
    CONTAMINATION,
    MAX_SAMPLES,
    N_JOBS,
    RANDOM_SEED,
    MODEL_PATH,
)


class AnomalyDetector:
    """
    Isolation Forest based anomaly detector for KalaSetu.

    Detects unusual activity across:
    - accounts
    - orders
    - products
    - transactions
    """

    def __init__(
        self,
        n_estimators: int = N_ESTIMATORS,
        contamination: float = CONTAMINATION,
        max_samples=MAX_SAMPLES,
        random_state: int = RANDOM_SEED,
    ):
        self.model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            max_samples=max_samples,
            random_state=random_state,
            n_jobs=N_JOBS,
        )

        self.feature_columns = None

    def fit(self, X):
        """
        Train the Isolation Forest model.
        """

        self.feature_columns = list(X.columns)

        self.model.fit(X)

        return self

    def predict(self, X):
        """
        Predict anomaly status.

        Returns:
            1  = normal
           -1  = anomaly
        """

        if self.feature_columns is None:
            raise RuntimeError(
                "Model has not been fitted."
            )

        X = X.reindex(
            columns=self.feature_columns,
            fill_value=0,
        )

        return self.model.predict(X)

    def decision_function(self, X):
        """
        Return Isolation Forest decision scores.

        Higher score:
            More normal

        Lower score:
            More anomalous
        """

        if self.feature_columns is None:
            raise RuntimeError(
                "Model has not been fitted."
            )

        X = X.reindex(
            columns=self.feature_columns,
            fill_value=0,
        )

        return self.model.decision_function(X)

    def anomaly_score(self, X):
        """
        Convert Isolation Forest decision scores
        into a 0-100 anomaly risk score.

        Higher score = higher anomaly risk.
        """

        decision_scores = self.decision_function(X)

        # Convert to NumPy array explicitly.
        decision_scores = np.asarray(
            decision_scores,
            dtype=float,
        )

        # Isolation Forest:
        # lower decision score = more anomalous
        #
        # Convert that into:
        # higher value = higher risk
        risk_scores = 50.0 - (
            decision_scores * 100.0
        )

        # Keep values between 0 and 100.
        #
        # We intentionally do NOT use ndarray.clip()
        # because of compatibility issues with the
        # current NumPy environment.
        risk_scores = np.maximum(
            risk_scores,
            0.0,
        )

        risk_scores = np.minimum(
            risk_scores,
            100.0,
        )

        return risk_scores

    def save(
        self,
        path: str | Path = MODEL_PATH,
    ):
        """
        Save trained model and feature columns.
        """

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        joblib.dump(
            {
                "model": self.model,
                "feature_columns": self.feature_columns,
            },
            path,
        )

    @classmethod
    def load(
        cls,
        path: str | Path = MODEL_PATH,
    ):
        """
        Load a previously trained anomaly detector.
        """

        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"Model not found: {path}"
            )

        saved = joblib.load(path)

        detector = cls()

        detector.model = saved["model"]

        detector.feature_columns = (
            saved["feature_columns"]
        )

        return detector