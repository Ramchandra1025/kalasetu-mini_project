import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = (
    Path(__file__).resolve().parents[3]
)

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from ai.voice.audio import (
    normalize_audio,
    audio_duration,
    audio_statistics,
)

from ai.voice.language import (
    clean_text,
    detect_language,
    detect_intent,
    detect_kalasetu_keywords,
    language_intelligence,
)

from ai.voice.model import (
    VoiceLanguageModel,
)


# ============================================================
# TEST 1 — MODEL CREATION
# ============================================================

def test_model_creation():

    model = VoiceLanguageModel()

    assert model is not None

    assert (
        model.model_version
        == "1.0.0"
    )

    print(
        "Model creation test passed."
    )


# ============================================================
# TEST 2 — AUDIO NORMALIZATION
# ============================================================

def test_audio_normalization():

    audio = np.array(
        [-2.0, 0.0, 2.0],
        dtype=np.float32,
    )

    normalized = normalize_audio(
        audio
    )

    assert np.max(
        np.abs(normalized)
    ) == 1.0

    print(
        "Audio normalization test passed."
    )


# ============================================================
# TEST 3 — AUDIO DURATION
# ============================================================

def test_audio_duration():

    audio = np.zeros(
        16000,
        dtype=np.float32,
    )

    duration = audio_duration(
        audio,
        16000,
    )

    assert duration == 1.0

    print(
        "Audio duration test passed."
    )


# ============================================================
# TEST 4 — AUDIO STATISTICS
# ============================================================

def test_audio_statistics():

    audio = np.zeros(
        8000,
        dtype=np.float32,
    )

    stats = audio_statistics(
        audio,
        8000,
    )

    assert stats["sample_rate"] == 8000

    assert stats["samples"] == 8000

    assert (
        stats["duration_seconds"]
        == 1.0
    )

    print(
        "Audio statistics test passed."
    )


# ============================================================
# TEST 5 — TEXT CLEANING
# ============================================================

def test_text_cleaning():

    result = clean_text(
        "  Handmade   wooden\ncraft  "
    )

    assert result == (
        "Handmade wooden craft"
    )

    print(
        "Text cleaning test passed."
    )


# ============================================================
# TEST 6 — ENGLISH LANGUAGE DETECTION
# ============================================================

def test_english_detection():

    result = detect_language(
        "This is a handcrafted wooden craft"
    )

    assert (
        result["language_code"]
        == "en"
    )

    print(
        "English language detection test passed."
    )


# ============================================================
# TEST 7 — HINDI LANGUAGE DETECTION
# ============================================================

def test_hindi_detection():

    result = detect_language(
        "यह एक हस्तशिल्प उत्पाद है"
    )

    assert (
        result["language_code"]
        == "hi"
    )

    print(
        "Hindi language detection test passed."
    )


# ============================================================
# TEST 8 — KANNADA LANGUAGE DETECTION
# ============================================================

def test_kannada_detection():

    result = detect_language(
        "ಇದು ಒಂದು ಕರಕುಶಲ ಉತ್ಪನ್ನವಾಗಿದೆ"
    )

    assert (
        result["language_code"]
        == "kn"
    )

    print(
        "Kannada language detection test passed."
    )


# ============================================================
# TEST 9 — KALASETU KEYWORDS
# ============================================================

def test_kalasetu_keywords():

    result = detect_kalasetu_keywords(
        "handcrafted wooden artisan craft"
    )

    assert "en" in result

    assert (
        "handcrafted"
        in result["en"]
    )

    assert (
        "artisan"
        in result["en"]
    )

    print(
        "KalaSetu keyword detection test passed."
    )


# ============================================================
# TEST 10 — INTENT DETECTION
# ============================================================

def test_intent_detection():

    assert (
        detect_intent(
            "What is the price of this craft?"
        )
        == "pricing"
    )

    assert (
        detect_intent(
            "Tell me about the market"
        )
        == "market"
    )

    assert (
        detect_intent(
            "Tell me about this product"
        )
        == "product_information"
    )

    print(
        "Intent detection test passed."
    )


# ============================================================
# TEST 11 — COMPLETE LANGUAGE INTELLIGENCE
# ============================================================

def test_language_intelligence():

    result = language_intelligence(
        "This handcrafted wooden product "
        "is made by an artisan"
    )

    assert (
        result["language_code"]
        == "en"
    )

    assert (
        result["intent"]
        == "product_information"
    )

    assert (
        "en"
        in result["kalasetu_keywords"]
    )

    print(
        "Complete language intelligence test passed."
    )


# ============================================================
# TEST 12 — TEXT ANALYSIS THROUGH MODEL
# ============================================================

def test_model_text_analysis():

    model = VoiceLanguageModel()

    result = model.analyze_text(
        "What is the price of this craft?"
    )

    assert (
        result["language_code"]
        == "en"
    )

    assert (
        result["intent"]
        == "pricing"
    )

    assert (
        result["model_version"]
        == "1.0.0"
    )

    print(
        "Model text analysis test passed."
    )


# ============================================================
# TEST 13 — SAVE / LOAD
# ============================================================

def test_model_save_load():

    model = VoiceLanguageModel()

    temporary_path = (
        PROJECT_ROOT
        / "ml"
        / "models"
        / "voice"
        / "test_voice_model.joblib"
    )

    model.save(
        temporary_path
    )

    assert temporary_path.exists()

    loaded = (
        VoiceLanguageModel.load(
            temporary_path
        )
    )

    assert loaded is not None

    assert (
        loaded.model_version
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
        "KALASETU MODEL 11 "
        "VOICE & LANGUAGE AI TESTS"
    )

    print("=" * 60)

    tests = [

        test_model_creation,

        test_audio_normalization,

        test_audio_duration,

        test_audio_statistics,

        test_text_cleaning,

        test_english_detection,

        test_hindi_detection,

        test_kannada_detection,

        test_kalasetu_keywords,

        test_intent_detection,

        test_language_intelligence,

        test_model_text_analysis,

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
            "ALL MODEL 11 TESTS PASSED"
        )

        print("=" * 60)

        return True

    print()

    print(
        "MODEL 11 TESTS REQUIRE FIXES"
    )

    print("=" * 60)

    return False


if __name__ == "__main__":

    success = run_all_tests()

    if not success:

        sys.exit(1)
