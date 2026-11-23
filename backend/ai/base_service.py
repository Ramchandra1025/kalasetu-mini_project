"""
Base classes for KalaSetu production AI services.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class AIServiceError(Exception):
    """Base exception for production AI service errors."""


class AIModelNotAvailableError(AIServiceError):
    """Raised when a required AI model is unavailable."""


class AIInputError(AIServiceError):
    """Raised when AI input is invalid."""


class AIService(ABC):
    """
    Common interface for all KalaSetu production AI services.

    Every production adapter should expose:

        service_name
        model_name
        model_version
        health()
        predict()
    """

    service_name = "unknown"
    model_name = "unknown"
    model_version = "unknown"

    @abstractmethod
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the AI service.
        """
        raise NotImplementedError

    def health(self) -> Dict[str, Any]:
        """
        Return basic service health information.
        """

        return {
            "service": self.service_name,
            "model": self.model_name,
            "version": self.model_version,
            "status": "ready",
        }

    @staticmethod
    def require_fields(
        data: Dict[str, Any],
        fields,
    ):
        """
        Validate required input fields.
        """

        if not isinstance(data, dict):
            raise AIInputError(
                "AI input must be a JSON object."
            )

        missing = [
            field
            for field in fields
            if field not in data
        ]

        if missing:
            raise AIInputError(
                f"Missing required fields: {missing}"
            )

    @staticmethod
    def success(
        result: Dict[str, Any],
        *,
        service_name: str,
        model_name: str,
        model_version: str,
    ) -> Dict[str, Any]:
        """
        Standardize successful AI responses.
        """

        return {
            "success": True,
            "service": service_name,
            "model": model_name,
            "model_version": model_version,
            "result": result,
        }