
import copy
import sys
import tempfile
import unittest
from pathlib import Path


# ============================================================
# PROJECT PATH SETUP
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# KALASETU MODEL 15 IMPORTS
# ============================================================

from ai.dpp.dataset import (
    load_dataset,
    validate_dataset,
)

from ai.dpp.features import (
    normalize_text,
    is_present,
    calculate_completeness,
    calculate_completeness_score,
    generate_missing_fields,
    get_trust_level,
)

from ai.dpp.passport import (
    canonicalize_passport,
    calculate_hash,
    create_passport,
    finalize_passport,
    verify_passport,
    generate_qr_payload,
)

from ai.dpp.model import (
    DigitalProductPassportModel,
)


# ============================================================
# TEST DATA
# ============================================================

def sample_record():
    return {
        "product_id": "TEST001",
        "product_name": "Test Wooden Bowl",
        "artisan_id": "ART_TEST",
        "artisan_name": "Test Artisan",
        "craft_category": "wood_craft",
        "material": "wood",
        "origin_state": "Karnataka",
        "origin_district": "Bagalkot",
        "production_method": "handcrafted",
        "material_source": "local",
        "sustainability_score": 84.8,
        "carbon_impact_kg_co2e": 4.212,
    }


# ============================================================
# MODEL 15 TEST SUITE
# ============================================================

class TestDigitalProductPassport(unittest.TestCase):

    # --------------------------------------------------------
    # 1. Dataset loading
    # --------------------------------------------------------

    def test_dataset_loading(self):
        df = load_dataset()

        self.assertGreater(
            len(df),
            0,
        )

        print("Dataset loading test passed.")

    # --------------------------------------------------------
    # 2. Dataset validation
    # --------------------------------------------------------

    def test_dataset_validation(self):
        df = load_dataset()

        self.assertTrue(
            validate_dataset(df)
        )

        print("Dataset validation test passed.")

    # --------------------------------------------------------
    # 3. Text normalization
    # --------------------------------------------------------

    def test_text_normalization(self):
        self.assertEqual(
            normalize_text("  KalaSetu  "),
            "KalaSetu",
        )

        self.assertEqual(
            normalize_text(""),
            "",
        )

        print("Text normalization test passed.")

    # --------------------------------------------------------
    # 4. Presence detection
    # --------------------------------------------------------

    def test_presence_detection(self):
        self.assertTrue(
            is_present("wood")
        )

        self.assertFalse(
            is_present("")
        )

        self.assertFalse(
            is_present(None)
        )

        print("Presence detection test passed.")

    # --------------------------------------------------------
    # 5. Completeness sections
    # --------------------------------------------------------

    def test_completeness_sections(self):
        record = sample_record()

        sections = calculate_completeness(
            record
        )

        self.assertIn(
            "identity",
            sections,
        )

        self.assertIn(
            "artisan",
            sections,
        )

        self.assertIn(
            "craft",
            sections,
        )

        self.assertIn(
            "origin",
            sections,
        )

        self.assertIn(
            "production",
            sections,
        )

        self.assertIn(
            "sustainability",
            sections,
        )

        self.assertTrue(
            all(sections.values())
        )

        print("Completeness section test passed.")

    # --------------------------------------------------------
    # 6. Completeness score
    # --------------------------------------------------------

    def test_completeness_score(self):
        record = sample_record()

        score = calculate_completeness_score(
            record
        )

        self.assertEqual(
            score,
            100.0,
        )

        self.assertGreaterEqual(
            score,
            0,
        )

        self.assertLessEqual(
            score,
            100,
        )

        print("Completeness score test passed.")

    # --------------------------------------------------------
    # 7. Missing field detection
    # --------------------------------------------------------

    def test_missing_fields(self):
        record = sample_record()

        record["artisan_name"] = ""

        missing = generate_missing_fields(
            record
        )

        self.assertIn(
            "artisan_name",
            missing,
        )

        print("Missing field detection test passed.")

    # --------------------------------------------------------
    # 8. Trust level
    # --------------------------------------------------------

    def test_trust_level(self):

        self.assertEqual(
            get_trust_level(
                95,
                True,
            ),
            "HIGH",
        )

        self.assertEqual(
            get_trust_level(
                75,
                True,
            ),
            "MEDIUM",
        )

        self.assertEqual(
            get_trust_level(
                50,
                False,
            ),
            "LOW",
        )

        print("Trust level test passed.")

    # --------------------------------------------------------
    # 9. Canonicalization
    # --------------------------------------------------------

    def test_canonicalization(self):

        passport = {
            "b": 2,
            "a": 1,
        }

        canonical = canonicalize_passport(
            passport
        )

        self.assertEqual(
            canonical,
            '{"a":1,"b":2}',
        )

        print("Canonicalization test passed.")

    # --------------------------------------------------------
    # 10. SHA-256 hash generation
    # --------------------------------------------------------

    def test_hash_generation(self):

        passport = create_passport(
            sample_record()
        )

        hash_value = calculate_hash(
            passport
        )

        # SHA-256 hexadecimal hash = 64 characters
        self.assertEqual(
            len(hash_value),
            64,
        )

        self.assertTrue(
            all(
                character in "0123456789abcdef"
                for character in hash_value
            )
        )

        print("Hash generation test passed.")

    # --------------------------------------------------------
    # 11. Passport creation
    # --------------------------------------------------------

    def test_passport_creation(self):

        passport = create_passport(
            sample_record()
        )

        self.assertIn(
            "passport_version",
            passport,
        )

        self.assertIn(
            "product_id",
            passport,
        )

        self.assertIn(
            "product_name",
            passport,
        )

        self.assertIn(
            "artisan",
            passport,
        )

        self.assertIn(
            "craft",
            passport,
        )

        self.assertIn(
            "origin",
            passport,
        )

        self.assertIn(
            "production",
            passport,
        )

        self.assertIn(
            "sustainability",
            passport,
        )

        print("Passport creation test passed.")

    # --------------------------------------------------------
    # 12. Passport finalization
    # --------------------------------------------------------

    def test_passport_finalization(self):

        passport = finalize_passport(
            sample_record()
        )

        self.assertIn(
            "integrity",
            passport,
        )

        self.assertIn(
            "intelligence",
            passport,
        )

        self.assertIn(
            "hash",
            passport["integrity"],
        )

        self.assertEqual(
            passport["integrity"]["algorithm"],
            "SHA-256",
        )

        self.assertEqual(
            passport["intelligence"][
                "completeness_score"
            ],
            100.0,
        )

        print("Passport finalization test passed.")

    # --------------------------------------------------------
    # 13. Passport verification
    # --------------------------------------------------------

    def test_passport_verification(self):

        passport = finalize_passport(
            sample_record()
        )

        result = verify_passport(
            passport
        )

        self.assertTrue(
            result["verified"]
        )

        self.assertEqual(
            result["stored_hash"],
            result["calculated_hash"],
        )

        print("Passport verification test passed.")

    # --------------------------------------------------------
    # 14. Tamper detection
    # --------------------------------------------------------

    def test_tamper_detection(self):

        passport = finalize_passport(
            sample_record()
        )

        tampered = copy.deepcopy(
            passport
        )

        tampered["product_name"] = (
            "Tampered Product"
        )

        result = verify_passport(
            tampered
        )

        self.assertFalse(
            result["verified"]
        )

        self.assertNotEqual(
            result["stored_hash"],
            result["calculated_hash"],
        )

        print("Tamper detection test passed.")

    # --------------------------------------------------------
    # 15. QR payload generation
    # --------------------------------------------------------

    def test_qr_payload(self):

        passport = finalize_passport(
            sample_record()
        )

        payload = generate_qr_payload(
            passport
        )

        self.assertIsInstance(
            payload,
            str,
        )

        self.assertIn(
            "TEST001",
            payload,
        )

        self.assertIn(
            passport["integrity"]["hash"],
            payload,
        )

        print("QR payload test passed.")

    # --------------------------------------------------------
    # 16. Model creation
    # --------------------------------------------------------

    def test_model_creation(self):

        model = DigitalProductPassportModel()

        self.assertEqual(
            model.model_name,
            "Digital Product Passport AI",
        )

        self.assertEqual(
            model.model_version,
            "1.0.0",
        )

        print("Model creation test passed.")

    # --------------------------------------------------------
    # 17. Model analysis
    # --------------------------------------------------------

    def test_model_analysis(self):

        model = DigitalProductPassportModel()

        passport = model.create(
            sample_record()
        )

        self.assertIn(
            "integrity",
            passport,
        )

        result = model.verify(
            passport
        )

        self.assertTrue(
            result["verified"]
        )

        print("Model analysis test passed.")

    # --------------------------------------------------------
    # 18. Model save / load
    # --------------------------------------------------------

    def test_model_save_load(self):

        model = DigitalProductPassportModel()

        with tempfile.TemporaryDirectory() as temp_dir:

            model_path = (
                Path(temp_dir)
                / "dpp_model.joblib"
            )

            model.save(
                model_path
            )

            self.assertTrue(
                model_path.exists()
            )

            loaded = (
                DigitalProductPassportModel.load(
                    model_path
                )
            )

            self.assertEqual(
                loaded.model_name,
                model.model_name,
            )

            self.assertEqual(
                loaded.model_version,
                model.model_version,
            )

        print("Model save/load test passed.")


# ============================================================
# TEST RUNNER
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "KALASETU MODEL 15 "
        "DIGITAL PRODUCT PASSPORT AI TESTS"
    )

    print("=" * 60)

    suite = (
        unittest.defaultTestLoader
        .loadTestsFromTestCase(
            TestDigitalProductPassport
        )
    )

    result = unittest.TextTestRunner(
        verbosity=0
    ).run(suite)

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
    print("-" * 60)

    print(
        f"Tests passed: {passed}"
    )

    print(
        f"Tests failed: {failed}"
    )

    print("-" * 60)

    if result.wasSuccessful():

        print()

        print(
            "ALL MODEL 15 TESTS PASSED"
        )

        print("=" * 60)

    else:

        print()

        print(
            "MODEL 15 TESTS FAILED"
        )

        print("=" * 60)
