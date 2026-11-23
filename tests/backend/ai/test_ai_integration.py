import sys
import unittest

from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)


if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


from backend.ai.registry import (
    AIServiceRegistry,
)

from backend.ai.pipeline import (
    ProductIntelligencePipeline,
)


EXPECTED_SERVICES = [
    "cataloguing",
    "pricing",
    "demand",
    "market",
    "recommendation",
    "waste",
    "anomaly",
    "nlp",
    "ocr",
    "voice",
    "inventory",
    "logistics",
    "sustainability",
    "digital_product_passport",
]


def dpp_input():

    return {
        "product_id": "INTEGRATION_001",
        "product_name": "Handcrafted Wooden Bowl",
        "artisan_id": "ART_INT_001",
        "artisan_name": "Integration Artisan",
        "craft_category": "wood_craft",
        "material": "wood",
        "origin_state": "Karnataka",
        "origin_district": "Bagalkot",
        "production_method": "handcrafted",
        "material_source": "local",
        "sustainability_score": 84.8,
        "carbon_impact_kg_co2e": 4.212,
    }


def pricing_input():

    return {
        "size_cm": 25,
        "production_hours": 8,
        "material_cost": 800,
        "labor_cost": 1200,
        "demand_score": 80,
        "complexity_score": 75,
        "craft_category": "wood_craft",
        "material": "wood",
        "region": "karnataka",
    }


def demand_input():

    return {
        "product_category": "wood_craft",
        "region": "karnataka",
        "month": 5,
        "season": "summer",
        "historical_demand": 87,
        "previous_demand": 84,
        "price": 2800,
        "demand_growth": 3.57,
    }


def market_input():

    return {
        "product_category": "wood_craft",
        "region": "karnataka",
        "demand_score": 85,
        "price_opportunity": 78,
        "market_growth": 80,
        "regional_fit": 90,
        "seasonality_score": 75,
        "competition_score": 65,
    }


def recommendation_input():

    return {
        "buyer_id": "BUYER_001",
        "buyer_region": "karnataka",
        "preferred_category": "wood_craft",
        "preferred_material": "wood",
        "min_budget": 1000,
        "max_budget": 5000,
        "previous_category": "wood_craft",
        "previous_material": "wood",
        "product_category": "wood_craft",
        "product_material": "wood",
        "product_price": 2800,
        "product_region": "karnataka",
        "product_demand_score": 85,
    }


def waste_input():

    return {
        "craft_category": "wood_craft",
        "material": "wood",
        "waste_quantity_kg": 5,
        "condition_score": 90,
        "reuse_compatibility": 92,
        "demand_score": 85,
        "processing_effort": 20,
    }


def anomaly_input():

    return {
        "activity_id": "ACT_INT_001",
        "activity_type": "transaction",
        "account_type": "buyer",
        "region": "karnataka",
        "account_age_days": 365,
        "orders_last_7_days": 5,
        "orders_last_30_days": 20,
        "order_quantity": 2,
        "transaction_amount": 2500,
        "cancellation_rate": 5,
        "price_deviation": 5,
        "repeated_buyer_count": 2,
        "repeated_artisan_count": 2,
        "quantity_deviation": 5,
        "amount_deviation": 5,
    }


def nlp_input():

    return {
        "text": (
            "Handcrafted wooden bowl made from "
            "locally sourced wood by an artisan."
        )
    }


def inventory_input():

    return {
        "inventory_id": "INV_INT_001",
        "product_category": "wood_craft",
        "material": "wood",
        "region": "Karnataka",
        "current_stock": 12,
        "minimum_stock": 10,
        "maximum_stock": 50,
        "average_daily_sales": 6,
        "recent_daily_sales": 8,
        "historical_demand": 70,
        "demand_growth": 8,
        "lead_time_days": 7,
        "unit_price": 1200,
        "days_since_last_order": 5,
        "stockout_count": 1,
    }


class TestAIIntegration(
    unittest.TestCase
):

    def test_registry_contains_all_integrated_models(self):

        registry = AIServiceRegistry()

        services = registry.list_services()

        for service in EXPECTED_SERVICES:

            self.assertIn(
                service,
                services,
            )

        print(
            "Registry contains all 14 integrated AI services."
        )

    def test_registry_health(self):

        registry = AIServiceRegistry()

        health = registry.health()

        for service in EXPECTED_SERVICES:

            self.assertIn(
                service,
                health,
            )

        print(
            "Registry health test passed."
        )

    def test_pricing(self):

        registry = AIServiceRegistry()

        result = registry.get(
            "pricing"
        ).predict(
            pricing_input()
        )

        self.assertTrue(
            result["success"]
        )

        self.assertIn(
            "recommended_price",
            result["result"],
        )

        print(
            "Pricing adapter test passed."
        )

    def test_demand(self):

        registry = AIServiceRegistry()

        result = registry.get(
            "demand"
        ).predict(
            demand_input()
        )

        self.assertTrue(
            result["success"]
        )

        self.assertIn(
            "predicted_demand",
            result["result"],
        )

        print(
            "Demand adapter test passed."
        )

    def test_market(self):

        registry = AIServiceRegistry()

        result = registry.get(
            "market"
        ).predict(
            market_input()
        )

        self.assertTrue(
            result["success"]
        )

        self.assertIn(
            "opportunity_score",
            result["result"],
        )

        print(
            "Market adapter test passed."
        )

    def test_recommendation(self):

        registry = AIServiceRegistry()

        result = registry.get(
            "recommendation"
        ).predict(
            recommendation_input()
        )

        self.assertTrue(
            result["success"]
        )

        self.assertIn(
            "match_score",
            result["result"],
        )

        print(
            "Recommendation adapter test passed."
        )

    def test_waste(self):

        registry = AIServiceRegistry()

        result = registry.get(
            "waste"
        ).predict(
            waste_input()
        )

        self.assertTrue(
            result["success"]
        )

        self.assertIsInstance(
            result["result"],
            dict,
        )

        print(
            "Waste adapter test passed."
        )

    def test_anomaly(self):

        registry = AIServiceRegistry()

        result = registry.get(
            "anomaly"
        ).predict(
            anomaly_input()
        )

        self.assertTrue(
            result["success"]
        )

        self.assertIn(
            "anomaly_score",
            result["result"],
        )

        print(
            "Anomaly adapter test passed."
        )

    def test_nlp(self):

        registry = AIServiceRegistry()

        result = registry.get(
            "nlp"
        ).predict(
            nlp_input()
        )

        self.assertTrue(
            result["success"]
        )

        self.assertIn(
            "detected_category",
            result["result"],
        )

        print(
            "NLP adapter test passed."
        )

    def test_inventory(self):

        registry = AIServiceRegistry()

        result = registry.get(
            "inventory"
        ).predict(
            inventory_input()
        )

        self.assertTrue(
            result["success"]
        )

        self.assertIn(
            "stock_status",
            result["result"],
        )

        print(
            "Inventory adapter test passed."
        )

    def test_dpp(self):

        registry = AIServiceRegistry()

        result = registry.get(
            "digital_product_passport"
        ).predict(
            dpp_input()
        )

        self.assertTrue(
            result["success"]
        )

        self.assertIn(
            "passport",
            result["result"],
        )

        self.assertTrue(
            result["result"][
                "verification"
            ]["verified"]
        )

        print(
            "DPP adapter test passed."
        )

    def test_unified_pipeline(self):

        pipeline = (
            ProductIntelligencePipeline()
        )

        result = pipeline.run(
            module_inputs={
                "pricing":
                    pricing_input(),

                "demand":
                    demand_input(),

                "market":
                    market_input(),

                "recommendation":
                    recommendation_input(),

                "waste":
                    waste_input(),

                "anomaly":
                    anomaly_input(),

                "nlp":
                    nlp_input(),

                "inventory":
                    inventory_input(),

                "digital_product_passport":
                    dpp_input(),
            }
        )

        self.assertTrue(
            result["success"]
        )

        self.assertEqual(
            len(
                result[
                    "modules_completed"
                ]
            ),
            9,
        )

        print(
            "Unified multi-model pipeline test passed."
        )


if __name__ == "__main__":

    print("=" * 70)
    print(
        "KALASETU MULTI-MODEL AI INTEGRATION TESTS"
    )
    print("=" * 70)

    suite = (
        unittest.defaultTestLoader
        .loadTestsFromTestCase(
            TestAIIntegration
        )
    )

    result = (
        unittest.TextTestRunner(
            verbosity=1
        ).run(
            suite
        )
    )

    passed = (
        result.testsRun
        - len(result.failures)
        - len(result.errors)
    )

    failed = (
        len(result.failures)
        + len(result.errors)
    )

    print()
    print("-" * 70)

    print(
        f"Tests passed: {passed}"
    )

    print(
        f"Tests failed: {failed}"
    )

    print("-" * 70)

    if result.wasSuccessful():

        print()
        print(
            "ALL MULTI-MODEL AI INTEGRATION TESTS PASSED"
        )
        print("=" * 70)

    else:

        print()
        print(
            "MULTI-MODEL AI INTEGRATION TESTS FAILED"
        )
        print("=" * 70)