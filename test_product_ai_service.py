
from backend.services.product_ai_service import analyze_product

result = analyze_product(
    product_data={
        "craft_category": "wood_craft",
        "material": "wood",
    }
)

for model_name in (
    "cataloguing",
    "pricing",
    "demand",
    "sustainability",
):
    item = result[model_name]
    print(f"{model_name}: {item['status']}")
    if item.get("missing_fields"):
        print("  Missing:", ", ".join(item["missing_fields"]))
    if item.get("message"):
        print("  Message:", item["message"])
