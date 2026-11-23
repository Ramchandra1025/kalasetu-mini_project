
import json
import sys
import time
from pathlib import Path

# --------------------------------------------------
# Project setup
# --------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.ai.registry import ai_registry


# --------------------------------------------------
# Sample dataset paths
# --------------------------------------------------
SAMPLE_IMAGE = (
    ROOT / "ml" / "datasets" / "cataloguing"
    / "images" / "pottery" / "pottery_01.jpg"
)

SAMPLE_OCR_IMAGE = (
    ROOT / "ml" / "datasets" / "ocr"
    / "images" / "OCR001.png"
)

LOGISTICS_DATASET = (
    ROOT / "ml" / "datasets" / "logistics"
    / "logistics.csv"
)


# --------------------------------------------------
# Independent AI service smoke-test payloads
# --------------------------------------------------
PAYLOADS = {
    "cataloguing": {
        "image_path": str(SAMPLE_IMAGE),
    },

    "pricing": {
        "size_cm": 30,
        "production_hours": 5,
        "material_cost": 400,
        "labor_cost": 600,
        "demand_score": 65,
        "complexity_score": 40,
        "craft_category": "wood_craft",
        "material": "wood",
        "region": "karnataka",
    },

    "demand": {
        "product_category": "pottery",
        "region": "karnataka",
        "month": 10,
        "season": "festival",
        "historical_demand": 100,
        "previous_demand": 90,
        "price": 1200,
        "demand_growth": 10,
    },

    "market": {
        "product_category": "pottery",
        "region": "karnataka",
        "demand_score": 70,
        "price_opportunity": 60,
        "market_growth": 12,
        "regional_fit": 75,
        "seasonality_score": 65,
        "competition_score": 40,
    },

    "recommendation": {
        "buyer_id": "TEST_BUYER",
        "buyer_region": "karnataka",
        "preferred_category": "pottery",
        "preferred_material": "clay",
        "min_budget": 500,
        "max_budget": 3000,
        "previous_category": "pottery",
        "previous_material": "clay",
        "product_category": "pottery",
        "product_material": "clay",
        "product_price": 1500,
        "product_region": "karnataka",
        "product_demand_score": 70,
    },

    "waste": {
        "craft_category": "pottery",
        "material": "clay",
        "waste_quantity_kg": 5,
        "condition_score": 75,
        "reuse_compatibility": 80,
        "demand_score": 60,
        "processing_effort": 25,
    },

    "anomaly": {
        "activity_type": "purchase",
        "account_type": "buyer",
        "region": "karnataka",
        "account_age_days": 180,
        "orders_last_7_days": 3,
        "orders_last_30_days": 8,
        "order_quantity": 2,
        "transaction_amount": 1500,
        "cancellation_rate": 0.05,
        "price_deviation": 0.1,
        "repeated_buyer_count": 2,
        "repeated_artisan_count": 1,
        "quantity_deviation": 0.1,
        "amount_deviation": 0.1,
    },

    "nlp": {
        "text": "Handcrafted clay pottery made by Indian artisans",
    },

    "ocr": {
        "image_path": str(SAMPLE_OCR_IMAGE),
    },

    "inventory": {
        "product_category": "pottery",
        "material": "clay",
        "region": "karnataka",
        "current_stock": 20,
        "minimum_stock": 10,
        "maximum_stock": 50,
        "average_daily_sales": 2,
        "recent_daily_sales": 3,
        "historical_demand": 60,
        "demand_growth": 10,
        "lead_time_days": 5,
        "unit_price": 1200,
        "days_since_last_order": 10,
        "stockout_count": 1,
    },

    "logistics": {
        "dataset_path": str(LOGISTICS_DATASET),
    },

    "sustainability": {
        "product_id": "TEST_PRODUCT",
        "product_category": "pottery",
        "material": "clay",
        "material_weight_kg": 2.0,
        "production_energy_kwh": 1.5,
        "waste_kg": 0.2,
        "packaging_type": "recyclable",
        "transport_distance_km": 20,
        # These fields require categorical strings.
        "recyclability": "high",
        "local_sourcing": "local",
    },
}


# --------------------------------------------------
# Run tests independently
# --------------------------------------------------
def main():
    report = {}

    print("=" * 72)
    print("KALASETU AI SERVICE SMOKE TEST")
    print("=" * 72)

    for name, payload in PAYLOADS.items():
        start = time.perf_counter()

        try:
            # Report missing files without stopping other tests.
            if name == "cataloguing":
                if not SAMPLE_IMAGE.is_file():
                    raise FileNotFoundError(
                        f"Cataloguing test image not found: {SAMPLE_IMAGE}"
                    )

            elif name == "ocr":
                if not SAMPLE_OCR_IMAGE.is_file():
                    raise FileNotFoundError(
                        f"OCR test image not found: {SAMPLE_OCR_IMAGE}"
                    )

            elif name == "logistics":
                if not LOGISTICS_DATASET.is_file():
                    raise FileNotFoundError(
                        f"Logistics dataset not found: {LOGISTICS_DATASET}"
                    )

            service = ai_registry.get(name)
            result = service.predict(payload)

            if isinstance(result, dict) and result.get("success") is True:
                status = "PASS"
            else:
                status = "CHECK"

            report[name] = {
                "status": status,
                "elapsed_seconds": round(
                    time.perf_counter() - start, 3
                ),
                "response": result,
            }

        except Exception as exc:
            report[name] = {
                "status": "FAIL",
                "elapsed_seconds": round(
                    time.perf_counter() - start, 3
                ),
                "error_type": type(exc).__name__,
                "error": str(exc),
            }

        result_entry = report[name]

        print(
            f"{name:20} "
            f"{result_entry['status']:5} "
            f"{result_entry['elapsed_seconds']:>8.3f}s"
        )

        if result_entry["status"] == "FAIL":
            print(
                f"  {result_entry['error_type']}: "
                f"{result_entry['error']}"
            )

        elif result_entry["status"] == "CHECK":
            print("  Service returned a response without success=True.")

    # --------------------------------------------------
    # Save JSON report
    # --------------------------------------------------
    output_path = (
        ROOT
        / "research"
        / "results"
        / "ai_service_smoke_test.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8",
    )

    passed = sum(
        item["status"] == "PASS"
        for item in report.values()
    )
    failed = sum(
        item["status"] == "FAIL"
        for item in report.values()
    )
    check = sum(
        item["status"] == "CHECK"
        for item in report.values()
    )

    print("-" * 72)
    print(f"Total services tested: {len(report)}")
    print(f"PASS: {passed} | FAIL: {failed} | CHECK: {check}")
    print(f"Full report: {output_path}")
    print("=" * 72)


if __name__ == "__main__":
    main()
