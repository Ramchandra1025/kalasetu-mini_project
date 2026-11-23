"""
Production adapter for KalaSetu Digital Product Passport AI.
"""

from pathlib import Path
from typing import Any, Dict

from ai.dpp.config import (
    MODEL_NAME,
    MODEL_PATH,
    MODEL_VERSION,
)

from ai.dpp.model import (
    DigitalProductPassportModel,
)

from .base_service import (
    AIModelNotAvailableError,
    AIService,
    AIInputError,
)


class DPPService(AIService):
    """
    Production-facing adapter for Model 15.

    Research/model development code remains inside:

        ai/dpp/

    This adapter is responsible only for application integration.
    """

    service_name = "digital_product_passport"
    model_name = MODEL_NAME
    model_version = MODEL_VERSION

    REQUIRED_FIELDS = [
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

    def __init__(
        self,
        model_path=MODEL_PATH,
    ):
        self.model_path = Path(model_path)
        self.model = None

    def load(self):
        """
        Load the trained/frozen DPP model.
        """

        if not self.model_path.exists():
            raise AIModelNotAvailableError(
                f"DPP model not found: {self.model_path}"
            )

        self.model = (
            DigitalProductPassportModel.load(
                self.model_path
            )
        )

        return self

    def ensure_loaded(self):
        """
        Lazily load the model.
        """

        if self.model is None:
            self.load()

        return self.model

    def predict(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:

        self.require_fields(
            data,
            self.REQUIRED_FIELDS,
        )

        model = self.ensure_loaded()

        passport = model.create(data)

        verification = model.verify(
            passport
        )

        qr_payload = model.qr_payload(
            passport
        )

        return self.success(
            {
                "passport": passport,
                "verification": verification,
                "qr_payload": qr_payload,
                "research_valid": False,
                "prototype": True,
                "blockchain_backed": False,
            },
            service_name=self.service_name,
            model_name=self.model_name,
            model_version=self.model_version,
        )

    def health(self):
        """
        DPP-specific health check.
        """

        model_exists = (
            self.model_path.exists()
        )

        return {
            "service": self.service_name,
            "model": self.model_name,
            "version": self.model_version,
            "model_path": str(
                self.model_path
            ),
            "model_file_exists": model_exists,
            "status": (
                "ready"
                if model_exists
                else "unavailable"
            ),
        }