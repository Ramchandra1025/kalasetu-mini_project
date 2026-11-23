from pathlib import Path

import joblib
import pandas as pd
from xgboost import XGBClassifier

from .config import (
    MODEL_PATH,
    RANDOM_SEED,
)


class InventoryIntelligenceModel:

    def __init__(
        self,
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        random_state=RANDOM_SEED,
    ):

        self.model = XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=random_state,
            eval_metric="mlogloss",
            n_jobs=1,
        )

        self.feature_columns = None
        self.class_names = None

    def fit(self, X, y):

        self.feature_columns = list(X.columns)

        self.class_names = sorted(
            list(set(y))
        )

        # XGBoost expects integer class labels.
        class_mapping = {
            label: index
            for index, label in enumerate(
                self.class_names
            )
        }

        encoded_y = y.map(class_mapping)

        self.class_mapping = class_mapping

        self.model.fit(
            X,
            encoded_y,
        )

        return self

    def _prepare_features(self, X):

        if self.feature_columns is None:
            raise RuntimeError(
                "Model has not been fitted."
            )

        X = X.copy()

        X = X.reindex(
            columns=self.feature_columns,
            fill_value=0,
        )

        return X

    def predict(self, X):

        X = self._prepare_features(X)

        predictions = self.model.predict(X)

        reverse_mapping = {
            value: key
            for key, value
            in self.class_mapping.items()
        }

        return pd.Series(
            [
                reverse_mapping[int(value)]
                for value in predictions
            ],
            index=X.index,
        )

    def predict_proba(self, X):

        X = self._prepare_features(X)

        return self.model.predict_proba(X)

    def save(self, path=MODEL_PATH):

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        joblib.dump(
            {
                "model": self.model,
                "feature_columns": self.feature_columns,
                "class_names": self.class_names,
                "class_mapping": self.class_mapping,
            },
            path,
        )

    @classmethod
    def load(cls, path=MODEL_PATH):

        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"Model not found: {path}"
            )

        saved = joblib.load(path)

        instance = cls()

        instance.model = saved["model"]
        instance.feature_columns = saved[
            "feature_columns"
        ]
        instance.class_names = saved[
            "class_names"
        ]
        instance.class_mapping = saved[
            "class_mapping"
        ]

        return instance