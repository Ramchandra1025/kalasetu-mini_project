
import sys
from pathlib import Path

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from PIL import Image

from ai.ocr.config import TESSERACT_CMD
from ai.ocr.model import OCRModel

from ai.ocr.preprocessing import (
    load_image,
    preprocess_image,
)


IMAGE_PATH = (
    PROJECT_ROOT
    / "ml"
    / "datasets"
    / "ocr"
    / "images"
    / "OCR001.png"
)


# ============================================================
# TEST 1 — TESSERACT CONFIGURATION
# ============================================================

def test_tesseract_configuration():

    model = OCRModel()

    assert Path(TESSERACT_CMD).exists(), (
        f"Tesseract executable not found: "
        f"{TESSERACT_CMD}"
    )

    print(
        "Tesseract configuration test passed."
    )


# ============================================================
# TEST 2 — MODEL CREATION
# ============================================================

def test_model_creation():

    model = OCRModel()

    assert model is not None

    assert model.model_version == "1.0.0"

    print(
        "Model creation test passed."
    )


# ============================================================
# TEST 3 — IMAGE LOADING
# ============================================================

def test_image_loading():

    assert IMAGE_PATH.exists(), (
        f"Test image not found: "
        f"{IMAGE_PATH}"
    )

    image = load_image(
        IMAGE_PATH
    )

    assert image is not None

    assert len(image.shape) in (2, 3)

    print(
        "Image loading test passed."
    )


# ============================================================
# TEST 4 — PIL IMAGE SUPPORT
# ============================================================

def test_pil_image_support():

    assert IMAGE_PATH.exists()

    image = Image.open(
        IMAGE_PATH
    )

    processed = preprocess_image(
        image
    )

    assert processed is not None

    assert processed.ndim == 2

    print(
        "PIL image preprocessing test passed."
    )


# ============================================================
# TEST 5 — NUMPY IMAGE SUPPORT
# ============================================================

def test_numpy_image_support():

    image = load_image(
        IMAGE_PATH
    )

    processed = preprocess_image(
        image
    )

    assert processed is not None

    assert processed.ndim == 2

    print(
        "NumPy image preprocessing test passed."
    )


# ============================================================
# TEST 6 — COMPLETE PREPROCESSING
# ============================================================

def test_preprocessing_pipeline():

    processed = preprocess_image(
        IMAGE_PATH
    )

    assert processed is not None

    assert processed.ndim == 2

    assert processed.shape[0] > 0

    assert processed.shape[1] > 0

    print(
        "Preprocessing pipeline test passed."
    )


# ============================================================
# TEST 7 — TEXT CLEANING
# ============================================================

def test_text_cleaning():

    model = OCRModel()

    result = model.clean_text(
        "  Handcrafted\nwooden   craft  "
    )

    assert result == (
        "Handcrafted wooden craft"
    )

    print(
        "Text cleaning test passed."
    )


# ============================================================
# TEST 8 — KEYWORD EXTRACTION
# ============================================================

def test_keyword_extraction():

    model = OCRModel()

    keywords = model.extract_keywords(
        "Handcrafted wooden wall decoration "
        "made by traditional artisan"
    )

    assert "handcrafted" in keywords

    assert "wooden" in keywords

    assert "traditional" in keywords

    print(
        "Keyword extraction test passed."
    )


# ============================================================
# TEST 9 — CATEGORY DETECTION
# ============================================================

def test_category_detection():

    model = OCRModel()

    result = model.detect_category(
        "handcrafted wooden wall decoration"
    )

    assert result["category"] == "wood_craft"

    assert result["confidence"] > 0

    print(
        "Category detection test passed."
    )


# ============================================================
# TEST 10 — MATERIAL DETECTION
# ============================================================

def test_material_detection():

    model = OCRModel()

    materials = model.detect_materials(
        "handcrafted wooden craft made from wood"
    )

    assert "wood" in materials

    assert "wooden" in materials

    print(
        "Material detection test passed."
    )


# ============================================================
# TEST 11 — CRAFT TERM DETECTION
# ============================================================

def test_craft_detection():

    model = OCRModel()

    terms = model.detect_craft_terms(
        "handcrafted traditional craft"
    )

    assert "handcrafted" in terms

    assert "traditional" in terms

    print(
        "Craft-term detection test passed."
    )


# ============================================================
# TEST 12 — REAL OCR PREDICTION
# ============================================================

def test_real_ocr_prediction():

    assert IMAGE_PATH.exists(), (
        f"Test image not found: "
        f"{IMAGE_PATH}"
    )

    model = OCRModel()

    result = model.predict(
        IMAGE_PATH
    )

    assert isinstance(
        result,
        dict,
    )

    assert "text" in result

    assert "cleaned_text" in result

    assert "confidence" in result

    assert "confidence_level" in result

    assert "keywords" in result

    assert "detected_category" in result

    assert "category_confidence" in result

    assert "detected_materials" in result

    assert "craft_terms" in result

    assert result["confidence"] >= 0

    assert result["confidence"] <= 100

    print(
        "Real OCR prediction test passed."
    )


# ============================================================
# TEST 13 — SAVE / LOAD
# ============================================================

def test_model_save_load():

    model = OCRModel()

    temporary_path = (
        PROJECT_ROOT
        / "ml"
        / "models"
        / "ocr"
        / "test_ocr_model.joblib"
    )

    model.save(
        temporary_path
    )

    assert temporary_path.exists()

    loaded_model = OCRModel.load(
        temporary_path
    )

    assert loaded_model is not None

    assert (
        loaded_model.model_version
        == model.model_version
    )

    temporary_path.unlink()

    print(
        "Save/load test passed."
    )


# ============================================================
# RUN ALL TESTS
# ============================================================

def run_all_tests():

    print()

    print("=" * 60)

    print(
        "KALASETU MODEL 10 OCR TESTS"
    )

    print("=" * 60)

    tests = [
        test_tesseract_configuration,
        test_model_creation,
        test_image_loading,
        test_pil_image_support,
        test_numpy_image_support,
        test_preprocessing_pipeline,
        test_text_cleaning,
        test_keyword_extraction,
        test_category_detection,
        test_material_detection,
        test_craft_detection,
        test_real_ocr_prediction,
        test_model_save_load,
    ]

    passed = 0
    failed = 0

    for test in tests:

        try:

            test()

            passed += 1

        except Exception as error:

            failed += 1

            print()

            print(
                f"TEST FAILED: "
                f"{test.__name__}"
            )

            print(
                f"Reason: {error}"
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


    if failed == 0:

        print()

        print(
            "ALL MODEL 10 TESTS PASSED"
        )

        print("=" * 60)

        return True


    print()

    print(
        "MODEL 10 TESTS REQUIRE FIXES"
    )

    print("=" * 60)

    return False


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    success = run_all_tests()

    if not success:
        sys.exit(1)
