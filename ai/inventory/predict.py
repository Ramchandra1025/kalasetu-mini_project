"""Explainable inventory policy baseline.

This deliberately does not load the legacy XGBoost classifier: that classifier
was trained on labels derived from current stock coverage (target leakage).
"""
import argparse
import json

from .config import MODEL_NAME, MODEL_VERSION, RESEARCH_VALID


def calculate_inventory_intelligence(data):
    current_stock = float(data["current_stock"])
    daily_sales = max(float(data["recent_daily_sales"]), 0.0)
    average_sales = max(float(data["average_daily_sales"]), 0.0)
    lead_time = max(float(data["lead_time_days"]), 0.0)
    minimum_stock = max(float(data["minimum_stock"]), 0.0)
    maximum_stock = max(float(data["maximum_stock"]), 0.0)

    coverage_days = current_stock / daily_sales if daily_sales > 0 else None
    safety_stock = daily_sales * 3.0
    reorder_point = daily_sales * lead_time + safety_stock
    target_stock = max(maximum_stock, reorder_point)
    reorder_quantity = max(0.0, target_stock - current_stock)

    if daily_sales == 0:
        status = "NO_RECENT_DEMAND"
        action = "REVIEW_DEMAND_AND_STOCK"
    elif coverage_days <= lead_time:
        status = "CRITICAL"
        action = "RESTOCK_IMMEDIATELY"
    elif current_stock <= reorder_point:
        status = "LOW_STOCK"
        action = "REORDER_SOON"
    elif coverage_days >= 60:
        status = "OVERSTOCK"
        action = "PAUSE_OR_REDUCE_PRODUCTION"
    else:
        status = "HEALTHY"
        action = "MAINTAIN_AND_MONITOR"

    reasons = []
    if daily_sales > average_sales:
        reasons.append("recent sales exceed the historical average")
    if current_stock <= reorder_point and daily_sales > 0:
        reasons.append("stock is at or below lead-time demand plus safety stock")
    if coverage_days is not None and coverage_days >= 60:
        reasons.append("estimated stock coverage is at least 60 days")
    if not reasons:
        reasons.append("no threshold-based inventory warning was triggered")

    return {
        "stock_status": status,
        "stock_coverage_days": round(coverage_days, 2) if coverage_days is not None else None,
        "safety_stock": round(safety_stock, 2),
        "reorder_point": round(reorder_point, 2),
        "recommended_stock_level": round(target_stock, 2),
        "recommended_reorder_quantity": round(reorder_quantity, 2),
        "recommended_action": action,
        "reasons": reasons,
        "method": "deterministic_reorder_point_policy",
        "confidence": None,
    }


def main():
    parser = argparse.ArgumentParser(description="KalaSetu inventory policy baseline")
    parser.add_argument("--category", default="wood_craft")
    parser.add_argument("--material", default="wood")
    parser.add_argument("--region", default="Karnataka")
    parser.add_argument("--stock", type=float, default=12)
    parser.add_argument("--minimum-stock", type=float, default=10)
    parser.add_argument("--maximum-stock", type=float, default=50)
    parser.add_argument("--average-sales", type=float, default=6)
    parser.add_argument("--recent-sales", type=float, default=8)
    parser.add_argument("--historical-demand", type=float, default=70)
    parser.add_argument("--demand-growth", type=float, default=8)
    parser.add_argument("--lead-time", type=float, default=7)
    parser.add_argument("--price", type=float, default=1200)
    parser.add_argument("--days-last-order", type=float, default=5)
    parser.add_argument("--stockouts", type=float, default=1)
    args = parser.parse_args()

    result = calculate_inventory_intelligence({
        "current_stock": args.stock,
        "minimum_stock": args.minimum_stock,
        "maximum_stock": args.maximum_stock,
        "average_daily_sales": args.average_sales,
        "recent_daily_sales": args.recent_sales,
        "lead_time_days": args.lead_time,
    })
    result.update({
        "inventory_id": "prediction",
        "product_category": args.category,
        "material": args.material,
        "region": args.region,
        "current_stock": args.stock,
        "model": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "research_valid": RESEARCH_VALID,
        "note": "This is an explainable policy baseline, not a trained prediction. "
                "It is not validated against real stockout outcomes.",
    })
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
