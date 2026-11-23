import hashlib
import json
from datetime import datetime, timezone

from .config import MODEL_NAME, MODEL_VERSION, PASSPORT_VERSION
from .features import (
    calculate_completeness_score,
    generate_missing_fields,
    get_trust_level,
)


def canonicalize_passport(passport):
    """
    Convert a passport into deterministic JSON.

    Sorting keys ensures that the same passport
    always produces the same SHA-256 hash.
    """

    return json.dumps(
        passport,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def calculate_hash(passport):
    """
    Generate SHA-256 integrity hash for a passport.
    """

    canonical_data = canonicalize_passport(
        passport
    )

    return hashlib.sha256(
        canonical_data.encode("utf-8")
    ).hexdigest()


def create_passport(record):
    """
    Create the core Digital Product Passport.
    """

    passport = {
        "passport_version": PASSPORT_VERSION,

        "product_id": record.get(
            "product_id"
        ),

        "product_name": record.get(
            "product_name"
        ),

        "artisan": {
            "artisan_id": record.get(
                "artisan_id"
            ),
            "artisan_name": record.get(
                "artisan_name"
            ),
        },

        "craft": {
            "category": record.get(
                "craft_category"
            ),
            "material": record.get(
                "material"
            ),
        },

        "origin": {
            "state": record.get(
                "origin_state"
            ),
            "district": record.get(
                "origin_district"
            ),
        },

        "production": {
            "method": record.get(
                "production_method"
            ),
            "material_source": record.get(
                "material_source"
            ),
        },

        "sustainability": {
            "score": record.get(
                "sustainability_score"
            ),
            "carbon_impact_kg_co2e": record.get(
                "carbon_impact_kg_co2e"
            ),
        },

        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "model": MODEL_NAME,

        "model_version": MODEL_VERSION,
    }

    return passport


def finalize_passport(record):
    """
    Build the complete Digital Product Passport.

    Correct integrity flow:

    1. Create core passport
    2. Calculate intelligence
    3. Add intelligence
    4. Calculate hash over the complete passport
    5. Add integrity metadata
    """

    passport = create_passport(
        record
    )

    # --------------------------------------------------------
    # Calculate passport intelligence FIRST
    # --------------------------------------------------------

    completeness_score = (
        calculate_completeness_score(
            record
        )
    )

    missing_fields = (
        generate_missing_fields(
            record
        )
    )

    trust_level = get_trust_level(
        completeness_score,
        True,
    )

    passport["intelligence"] = {
        "completeness_score": (
            completeness_score
        ),
        "missing_fields": (
            missing_fields
        ),
        "trust_level": trust_level,
    }

    # --------------------------------------------------------
    # Calculate integrity hash AFTER intelligence exists
    # --------------------------------------------------------

    passport_hash = calculate_hash(
        passport
    )

    passport["integrity"] = {
        "algorithm": "SHA-256",
        "hash": passport_hash,
    }

    return passport


def verify_passport(passport):
    """
    Verify Digital Product Passport integrity.

    The integrity block itself is excluded from
    the hash calculation because it contains the hash
    being verified.

    All other passport data remains protected.
    """

    if "integrity" not in passport:

        return {
            "verified": False,
            "reason": (
                "Integrity information is missing."
            ),
        }

    stored_hash = (
        passport["integrity"].get(
            "hash"
        )
    )

    if not stored_hash:

        return {
            "verified": False,
            "reason": (
                "Passport hash is missing."
            ),
        }

    # --------------------------------------------------------
    # Copy passport
    # --------------------------------------------------------

    passport_copy = json.loads(
        json.dumps(
            passport
        )
    )

    # --------------------------------------------------------
    # Remove only integrity metadata.
    #
    # Intelligence remains included so that
    # tampering with completeness/trust data
    # is also detected.
    # --------------------------------------------------------

    del passport_copy["integrity"]

    calculated_hash = calculate_hash(
        passport_copy
    )

    verified = (
        stored_hash
        == calculated_hash
    )

    return {
        "verified": verified,

        "stored_hash": stored_hash,

        "calculated_hash": calculated_hash,

        "reason": (
            "Passport integrity verified."
            if verified
            else
            "Passport data has been modified."
        ),
    }


def generate_qr_payload(passport):
    """
    Generate a compact QR-ready payload.

    The QR code does not contain the entire passport.
    It contains the passport identifier and integrity hash.
    """

    return json.dumps(
        {
            "passport_version": (
                passport.get(
                    "passport_version"
                )
            ),

            "product_id": (
                passport.get(
                    "product_id"
                )
            ),

            "passport_hash": (
                passport.get(
                    "integrity",
                    {}
                ).get(
                    "hash"
                )
            ),
        },

        separators=(
            ",",
            ":",
        ),
    )