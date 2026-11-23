from pathlib import Path

import joblib

from .passport import (
    finalize_passport,
    verify_passport,
    generate_qr_payload,
)


class DigitalProductPassportModel:

    def __init__(
        self,
        model_name="Digital Product Passport AI",
        model_version="1.0.0",
    ):
        self.model_name = model_name
        self.model_version = model_version

    def create(self, record):
        return finalize_passport(record)

    def verify(self, passport):
        return verify_passport(passport)

    def qr_payload(self, passport):
        return generate_qr_payload(passport)

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
                f"DPP model not found: {path}"
            )

        saved = joblib.load(path)

        return cls(
            model_name=saved["model_name"],
            model_version=saved["model_version"],
        )