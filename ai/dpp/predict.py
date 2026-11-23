import argparse
import json

from .config import MODEL_PATH
from .model import DigitalProductPassportModel


def main():

    parser = argparse.ArgumentParser(
        description="KalaSetu Digital Product Passport AI"
    )

    parser.add_argument(
        "--product-id",
        default="prediction",
    )

    parser.add_argument(
        "--product-name",
        default="Handcrafted Wooden Bowl",
    )

    parser.add_argument(
        "--artisan-id",
        default="ART001",
    )

    parser.add_argument(
        "--artisan-name",
        default="Demo Artisan",
    )

    parser.add_argument(
        "--category",
        default="wood_craft",
    )

    parser.add_argument(
        "--material",
        default="wood",
    )

    parser.add_argument(
        "--state",
        default="Karnataka",
    )

    parser.add_argument(
        "--district",
        default="Bagalkot",
    )

    parser.add_argument(
        "--production-method",
        default="handcrafted",
    )

    parser.add_argument(
        "--material-source",
        default="local",
    )

    parser.add_argument(
        "--sustainability-score",
        type=float,
        default=84.8,
    )

    parser.add_argument(
        "--carbon-impact",
        type=float,
        default=4.212,
    )

    args = parser.parse_args()

    model = DigitalProductPassportModel.load(
        MODEL_PATH
    )

    record = {
        "product_id": args.product_id,
        "product_name": args.product_name,
        "artisan_id": args.artisan_id,
        "artisan_name": args.artisan_name,
        "craft_category": args.category,
        "material": args.material,
        "origin_state": args.state,
        "origin_district": args.district,
        "production_method": args.production_method,
        "material_source": args.material_source,
        "sustainability_score": args.sustainability_score,
        "carbon_impact_kg_co2e": args.carbon_impact,
    }

    passport = model.create(record)

    verification = model.verify(
        passport
    )

    qr_payload = model.qr_payload(
        passport
    )

    result = {
        "passport": passport,
        "verification": verification,
        "qr_payload": qr_payload,
        "research_valid": False,
        "note": (
            "Prototype Digital Product Passport using "
            "structured provenance, SHA-256 integrity "
            "verification, and synthetic demonstration data. "
            "This is not a blockchain-backed passport yet."
        ),
    }

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()