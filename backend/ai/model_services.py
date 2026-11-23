"""
KalaSetu production adapters for AI Models 1-14.

These adapters connect the existing research/model layer
under ai/ to the Flask production layer under backend/ai/.

IMPORTANT:
The underlying AI models are not modified here.
"""

from pathlib import Path
from typing import Any, Dict

import pandas as pd
from PIL import Image

from .base_service import (
    AIService,
    AIInputError,
)


# ============================================================
# MODEL 1 — CATALOGUING
# ============================================================

class CataloguingService(AIService):

    service_name = "cataloguing"
    model_name = "EfficientNet-B0"
    model_version = "1.0.0"

    def predict(self, data: Dict[str, Any]):

        self.require_fields(
            data,
            ["image_path"],
        )

        image_path = Path(
            data["image_path"]
        )

        if not image_path.exists():
            raise AIInputError(
                f"Image not found: {image_path}"
            )

        from ai.cataloguing.predict import (
            predict_image,
        )

        result = predict_image(
            image_path
        )

        result["research_valid"] = False

        result["prototype"] = True

        return self.success(
            result,
            service_name=self.service_name,
            model_name=self.model_name,
            model_version=self.model_version,
        )


# ============================================================
# MODEL 3 — FAIR PRICING
# ============================================================

class PricingService(AIService):

    service_name = "pricing"
    model_name = "XGBRegressor (candidate comparison v2)"
    model_version = "2.0.0"

    REQUIRED_FIELDS = [
        "size_cm",
        "production_hours",
        "material_cost",
        "labor_cost",
        "demand_score",
        "complexity_score",
        "craft_category",
        "material",
        "region",
    ]

    def predict(self, data: Dict[str, Any]):

        self.require_fields(
            data,
            self.REQUIRED_FIELDS,
        )

        from ai.pricing.predict import (
            predict_fair_price,
        )

        result = predict_fair_price(
            data
        )

        return self.success(
            result,
            service_name=self.service_name,
            model_name=self.model_name,
            model_version=self.model_version,
        )


# ============================================================
# MODEL 4 — DEMAND
# ============================================================

class DemandService(AIService):

    service_name = "demand"
    model_name = "XGBRegressor"
    model_version = "1.0.0"

    REQUIRED_FIELDS = [
        "product_category",
        "region",
        "month",
        "season",
        "historical_demand",
        "previous_demand",
        "price",
        "demand_growth",
    ]

    def predict(self, data: Dict[str, Any]):

        self.require_fields(
            data,
            self.REQUIRED_FIELDS,
        )

        from ai.demand.predict import (
            predict_future_demand,
        )

        result = predict_future_demand(
            data
        )

        return self.success(
            result,
            service_name=self.service_name,
            model_name=self.model_name,
            model_version=self.model_version,
        )


# ============================================================
# MODEL 5 — MARKET OPPORTUNITY
# ============================================================

class MarketService(AIService):

    service_name = "market"
    model_name = "Explainable Market Opportunity Engine"
    model_version = "1.0.0"

    REQUIRED_FIELDS = [
        "product_category",
        "region",
        "demand_score",
        "price_opportunity",
        "market_growth",
        "regional_fit",
        "seasonality_score",
        "competition_score",
    ]

    def predict(self, data: Dict[str, Any]):

        self.require_fields(
            data,
            self.REQUIRED_FIELDS,
        )

        from ai.market.predict import (
            predict_market_opportunity,
        )

        result = predict_market_opportunity(
            data
        )

        return self.success(
            result,
            service_name=self.service_name,
            model_name=self.model_name,
            model_version=self.model_version,
        )


# ============================================================
# MODEL 6 — BUYER RECOMMENDATION
# ============================================================

class RecommendationService(AIService):

    service_name = "recommendation"
    model_name = "Hybrid Buyer Matching Engine"
    model_version = "1.0.0"

    REQUIRED_FIELDS = [
        "buyer_id",
        "buyer_region",
        "preferred_category",
        "preferred_material",
        "min_budget",
        "max_budget",
        "previous_category",
        "previous_material",
        "product_category",
        "product_material",
        "product_price",
        "product_region",
        "product_demand_score",
    ]

    def predict(self, data: Dict[str, Any]):

        self.require_fields(
            data,
            self.REQUIRED_FIELDS,
        )

        from ai.recommendation.predict import (
            predict,
        )

        result = predict(
            data
        )

        return self.success(
            result,
            service_name=self.service_name,
            model_name=self.model_name,
            model_version=self.model_version,
        )


# ============================================================
# MODEL 7 — WASTE
# ============================================================

class WasteService(AIService):

    service_name = "waste"
    model_name = "Explainable Waste Intelligence Engine"
    model_version = "1.0.0"

    REQUIRED_FIELDS = [
        "craft_category",
        "material",
        "waste_quantity_kg",
        "condition_score",
        "reuse_compatibility",
        "demand_score",
        "processing_effort",
    ]

    def predict(self, data: Dict[str, Any]):

        self.require_fields(
            data,
            self.REQUIRED_FIELDS,
        )

        from ai.waste.scoring import (
            score_waste,
        )

        row = {
            "waste_id": data.get(
                "waste_id",
                "production",
            ),
            "craft_category": data[
                "craft_category"
            ],
            "material": data[
                "material"
            ],
            "waste_quantity_kg": float(
                data["waste_quantity_kg"]
            ),
            "condition_score": float(
                data["condition_score"]
            ),
            "reuse_compatibility": float(
                data["reuse_compatibility"]
            ),
            "demand_score": float(
                data["demand_score"]
            ),
            "processing_effort": float(
                data["processing_effort"]
            ),
            "disposal_cost": float(
                data.get(
                    "disposal_cost",
                    0,
                )
            ),
            "expected_reuse_value": float(
                data.get(
                    "expected_reuse_value",
                    0,
                )
            ),
        }

        result = score_waste(
            row
        )

        result["research_valid"] = False

        result["prototype"] = True

        return self.success(
            result,
            service_name=self.service_name,
            model_name=self.model_name,
            model_version=self.model_version,
        )


# ============================================================
# MODEL 8 — ANOMALY
# ============================================================

class AnomalyService(AIService):

    service_name = "anomaly"
    model_name = "Isolation Forest"
    model_version = "1.0.0"

    REQUIRED_FIELDS = [
        "activity_type",
        "account_type",
        "region",
        "account_age_days",
        "orders_last_7_days",
        "orders_last_30_days",
        "order_quantity",
        "transaction_amount",
        "cancellation_rate",
        "price_deviation",
        "repeated_buyer_count",
        "repeated_artisan_count",
        "quantity_deviation",
        "amount_deviation",
    ]

    def predict(self, data: Dict[str, Any]):

        self.require_fields(
            data,
            self.REQUIRED_FIELDS,
        )

        from ai.anomaly.predict import (
            predict,
        )

        result = predict(
            data
        )

        return self.success(
            result,
            service_name=self.service_name,
            model_name=self.model_name,
            model_version=self.model_version,
        )


# ============================================================
# MODEL 9 — NLP
# ============================================================

class NLPService(AIService):

    service_name = "nlp"
    model_name = "TF-IDF"
    model_version = "1.0.0"

    def predict(self, data: Dict[str, Any]):

        self.require_fields(
            data,
            ["text"],
        )

        text = str(
            data["text"]
        ).strip()

        if not text:
            raise AIInputError(
                "NLP text cannot be empty."
            )

        from ai.nlp.predict import (
            predict,
        )

        result = predict(
            text
        )

        return self.success(
            result,
            service_name=self.service_name,
            model_name=self.model_name,
            model_version=self.model_version,
        )


# ============================================================
# MODEL 10 — OCR
# ============================================================

class OCRService(AIService):

    service_name = "ocr"
    model_name = "Tesseract OCR"
    model_version = "1.0.0"

    def predict(self, data: Dict[str, Any]):

        self.require_fields(
            data,
            ["image_path"],
        )

        image_path = Path(
            data["image_path"]
        )

        if not image_path.exists():
            raise AIInputError(
                f"Image not found: {image_path}"
            )

        try:
            image = Image.open(
                image_path
            )
        except Exception as exc:
            raise AIInputError(
                f"Unable to open image: {exc}"
            )

        from ai.ocr.model import (
            OCRModel,
        )

        model = OCRModel()

        result = model.predict(
            image
        )

        result["image_path"] = str(
            image_path
        )

        return self.success(
            result,
            service_name=self.service_name,
            model_name=self.model_name,
            model_version=self.model_version,
        )


# ============================================================
# MODEL 11 — VOICE
# ============================================================

class VoiceService(AIService):

    service_name = "voice"
    model_name = "SpeechRecognition + langdetect"
    model_version = "1.0.0"

    def predict(self, data: Dict[str, Any]):

        self.require_fields(
            data,
            ["audio_path"],
        )

        audio_path = Path(
            data["audio_path"]
        )

        if not audio_path.exists():
            raise AIInputError(
                f"Audio file not found: {audio_path}"
            )

        language = data.get(
            "language",
            "en-IN",
        )

        from ai.voice.model import (
            VoiceLanguageModel,
        )

        model = VoiceLanguageModel()

        result = model.predict(
            str(audio_path),
            language=language,
        )

        return self.success(
            result,
            service_name=self.service_name,
            model_name=self.model_name,
            model_version=self.model_version,
        )


# ============================================================
# MODEL 12 — INVENTORY
# ============================================================

class InventoryService(AIService):

    service_name = "inventory"
    model_name = "XGBoost Inventory Intelligence"
    model_version = "1.0.0"

    REQUIRED_FIELDS = [
        "product_category",
        "material",
        "region",
        "current_stock",
        "minimum_stock",
        "maximum_stock",
        "average_daily_sales",
        "recent_daily_sales",
        "historical_demand",
        "demand_growth",
        "lead_time_days",
        "unit_price",
        "days_since_last_order",
        "stockout_count",
    ]

    def predict(self, data: Dict[str, Any]):

        self.require_fields(
            data,
            self.REQUIRED_FIELDS,
        )

        from ai.inventory.config import (
            MODEL_PATH,
            MODEL_NAME,
            MODEL_VERSION,
            RESEARCH_VALID,
        )

        from ai.inventory.features import (
            encode_features,
        )

        from ai.inventory.model import (
            InventoryIntelligenceModel,
        )

        row = pd.DataFrame(
            [
                {
                    "inventory_id": data.get(
                        "inventory_id",
                        "production",
                    ),
                    "product_category": data[
                        "product_category"
                    ],
                    "material": data[
                        "material"
                    ],
                    "region": data[
                        "region"
                    ],
                    "current_stock": float(
                        data["current_stock"]
                    ),
                    "minimum_stock": float(
                        data["minimum_stock"]
                    ),
                    "maximum_stock": float(
                        data["maximum_stock"]
                    ),
                    "average_daily_sales": float(
                        data["average_daily_sales"]
                    ),
                    "recent_daily_sales": float(
                        data["recent_daily_sales"]
                    ),
                    "historical_demand": float(
                        data["historical_demand"]
                    ),
                    "demand_growth": float(
                        data["demand_growth"]
                    ),
                    "lead_time_days": float(
                        data["lead_time_days"]
                    ),
                    "unit_price": float(
                        data["unit_price"]
                    ),
                    "days_since_last_order": float(
                        data["days_since_last_order"]
                    ),
                    "stockout_count": float(
                        data["stockout_count"]
                    ),
                }
            ]
        )

        model = (
            InventoryIntelligenceModel.load(
                MODEL_PATH
            )
        )

        X = encode_features(
            row
        )

        predicted_status = model.predict(
            X
        ).iloc[0]

        probabilities = model.predict_proba(
            X
        )[0]

        class_names = model.class_names

        confidence = dict(
            zip(
                class_names,
                [
                    round(
                        float(p) * 100,
                        2,
                    )
                    for p in probabilities
                ],
            )
        )

        current_stock = float(
            data["current_stock"]
        )

        daily_sales = max(
            float(
                data["recent_daily_sales"]
            ),
            0.1,
        )

        lead_time = float(
            data["lead_time_days"]
        )

        coverage = (
            current_stock
            / daily_sales
        )

        safety_stock = (
            daily_sales * 3
        )

        reorder_point = (
            daily_sales * lead_time
            + safety_stock
        )

        recommended_stock = max(
            float(
                data["maximum_stock"]
            ),
            reorder_point,
        )

        reorder_quantity = max(
            0,
            recommended_stock
            - current_stock,
        )

        if predicted_status == "CRITICAL":
            action = "RESTOCK IMMEDIATELY"

        elif predicted_status == "LOW_STOCK":
            action = "REORDER SOON"

        elif predicted_status == "OVERSTOCK":
            action = "REDUCE NEW PRODUCTION"

        else:
            action = "MAINTAIN CURRENT INVENTORY"

        result = {
            "inventory_id": data.get(
                "inventory_id",
                "production",
            ),
            "product_category": data[
                "product_category"
            ],
            "material": data[
                "material"
            ],
            "region": data[
                "region"
            ],
            "current_stock": current_stock,
            "stock_status": predicted_status,
            "confidence": confidence,
            "stock_coverage_days": round(
                coverage,
                2,
            ),
            "safety_stock": round(
                safety_stock,
                2,
            ),
            "reorder_point": round(
                reorder_point,
                2,
            ),
            "recommended_stock_level": round(
                recommended_stock,
                2,
            ),
            "recommended_reorder_quantity": round(
                reorder_quantity,
                2,
            ),
            "recommended_action": action,
            "model": MODEL_NAME,
            "model_version": MODEL_VERSION,
            "research_valid": RESEARCH_VALID,
        }

        return self.success(
            result,
            service_name=self.service_name,
            model_name=MODEL_NAME,
            model_version=MODEL_VERSION,
        )


# ============================================================
# MODEL 13 — LOGISTICS
# ============================================================

class LogisticsService(AIService):

    service_name = "logistics"
    model_name = "OR-Tools VRP"
    model_version = "1.0.0"

    def predict(self, data: Dict[str, Any]):

        dataset_path = Path(
            data.get(
                "dataset_path",
                "ml/datasets/logistics/logistics.csv",
            )
        )

        if not dataset_path.exists():
            raise AIInputError(
                f"Logistics dataset not found: {dataset_path}"
            )

        from ai.logistics.config import (
            AVERAGE_SPEED_KMPH,
            MODEL_NAME,
            MODEL_PATH,
            MODEL_VERSION,
            RESEARCH_VALID,
        )

        from ai.logistics.features import (
            create_distance_matrix,
            create_location_features,
            estimate_route_time,
        )

        from ai.logistics.model import (
            SmartLogisticsModel,
        )

        df = pd.read_csv(
            dataset_path
        )

        locations = create_location_features(
            df
        )

        distance_matrix = create_distance_matrix(
            locations
        )

        demands = (
            locations[
                "package_weight"
            ]
            .round()
            .astype(int)
            .tolist()
        )

        model = SmartLogisticsModel.load(
            MODEL_PATH
        )

        route_result = model.optimize_route(
            distance_matrix,
            demands,
        )

        estimated_time = estimate_route_time(
            route_result[
                "total_distance_km"
            ],
            AVERAGE_SPEED_KMPH,
        )

        result = {
            "model": MODEL_NAME,
            "model_version": MODEL_VERSION,
            "orders_processed": len(
                locations
            ),
            "routes_generated": len(
                route_result["routes"]
            ),
            "total_distance_km": route_result[
                "total_distance_km"
            ],
            "estimated_delivery_time_minutes": round(
                estimated_time,
                2,
            ),
            "routes": route_result[
                "routes"
            ],
            "vehicle_count": route_result[
                "vehicle_count"
            ],
            "research_valid": RESEARCH_VALID,
            "note": (
                "Prototype logistics optimization "
                "using synthetic location data. "
                "Distance and delivery time do not "
                "represent live traffic."
            ),
        }

        return self.success(
            result,
            service_name=self.service_name,
            model_name=MODEL_NAME,
            model_version=MODEL_VERSION,
        )


# ============================================================
# MODEL 14 — SUSTAINABILITY
# ============================================================

class SustainabilityService(AIService):

    service_name = "sustainability"
    model_name = "Sustainability Intelligence Model"
    model_version = "1.0.0"

    REQUIRED_FIELDS = [
        "product_id",
        "product_category",
        "material",
        "material_weight_kg",
        "production_energy_kwh",
        "waste_kg",
        "packaging_type",
        "transport_distance_km",
        "recyclability",
        "local_sourcing",
    ]

    def predict(self, data: Dict[str, Any]):

        self.require_fields(
            data,
            self.REQUIRED_FIELDS,
        )

        from ai.sustainability.config import (
            MODEL_NAME,
            MODEL_PATH,
            MODEL_VERSION,
            RESEARCH_VALID,
        )

        from ai.sustainability.model import (
            SustainabilityIntelligenceModel,
        )

        row = pd.DataFrame(
            [
                {
                    key: data[key]
                    for key in self.REQUIRED_FIELDS
                }
            ]
        )

        model = (
            SustainabilityIntelligenceModel.load(
                MODEL_PATH
            )
        )

        result = model.analyze(
            row
        )[0]

        output = {
            "product_id": data[
                "product_id"
            ],
            "product_category": data[
                "product_category"
            ],
            "material": data[
                "material"
            ],
            "sustainability_score": result[
                "sustainability_score"
            ],
            "sustainability_level": result[
                "sustainability_level"
            ],
            "component_scores": result[
                "component_scores"
            ],
            "estimated_carbon_kg_co2e": result[
                "estimated_carbon_kg_co2e"
            ],
            "recommendations": result[
                "recommendations"
            ],
            "model": MODEL_NAME,
            "model_version": MODEL_VERSION,
            "research_valid": RESEARCH_VALID,
        }

        return self.success(
            output,
            service_name=self.service_name,
            model_name=MODEL_NAME,
            model_version=MODEL_VERSION,
        )