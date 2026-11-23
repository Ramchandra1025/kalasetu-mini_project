from pathlib import Path

import joblib


class SustainabilityIntelligenceModel:

    def __init__(
        self,
        model_name="Sustainability Intelligence AI",
        model_version="1.0.0",
    ):

        self.model_name = model_name
        self.model_version = model_version

    def analyze(self, df):

        from .scoring import (
            analyze_sustainability,
        )

        return analyze_sustainability(
            df
        )

    def save(self, path):

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        joblib.dump(
            {
                "model_name": self.model_name,
                "model_version": self.model_version,
            },
            path,
        )

    @classmethod
    def load(cls, path):

        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"Sustainability model not found: {path}"
            )

        saved = joblib.load(path)

        return cls(
            model_name=saved["model_name"],
            model_version=saved["model_version"],
        )