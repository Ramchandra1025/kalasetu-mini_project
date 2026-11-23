"""
KalaSetu AI service registry.
"""

from .dpp_service import DPPService

from .model_services import (
    CataloguingService,
    PricingService,
    DemandService,
    MarketService,
    RecommendationService,
    WasteService,
    AnomalyService,
    NLPService,
    OCRService,
    VoiceService,
    InventoryService,
    LogisticsService,
    SustainabilityService,
)


class AIServiceRegistry:

    def __init__(self):

        self._services = {

            "cataloguing":
                CataloguingService(),

            "pricing":
                PricingService(),

            "demand":
                DemandService(),

            "market":
                MarketService(),

            "recommendation":
                RecommendationService(),

            "waste":
                WasteService(),

            "anomaly":
                AnomalyService(),

            "nlp":
                NLPService(),

            "ocr":
                OCRService(),

            "voice":
                VoiceService(),

            "inventory":
                InventoryService(),

            "logistics":
                LogisticsService(),

            "sustainability":
                SustainabilityService(),

            "digital_product_passport":
                DPPService(),
        }

    def get(
        self,
        service_name: str,
    ):

        service = self._services.get(
            service_name
        )

        if service is None:

            raise KeyError(
                f"AI service not registered: "
                f"{service_name}"
            )

        return service

    def list_services(self):

        return list(
            self._services.keys()
        )

    def health(self):

        return {
            name: service.health()
            for name, service
            in self._services.items()
        }


ai_registry = AIServiceRegistry()