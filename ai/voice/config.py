
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_DIR = (
    PROJECT_ROOT
    / "ml"
    / "datasets"
    / "voice"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "voice"
)

RESEARCH_EXPERIMENT_DIR = (
    PROJECT_ROOT
    / "research"
    / "experiments"
    / "voice"
)

RESEARCH_EVALUATION_DIR = (
    PROJECT_ROOT
    / "research"
    / "evaluation"
    / "voice"
)

RESEARCH_RESULTS_DIR = (
    PROJECT_ROOT
    / "research"
    / "results"
    / "voice"
)


# ============================================================
# MODEL
# ============================================================

MODEL_VERSION = "1.0.0"

MODEL_NAME = (
    "Speech Recognition + Language Detection"
)

LANGUAGE_CONFIDENCE_THRESHOLD = 60.0


# ============================================================
# SUPPORTED LANGUAGES
# ============================================================

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "gu": "Gujarati",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia",
    "ur": "Urdu",
}


# ============================================================
# KALASETU LANGUAGE COMMANDS
# ============================================================

LANGUAGE_KEYWORDS = {

    "en": [
        "craft",
        "artisan",
        "handmade",
        "handcrafted",
        "wood",
        "textile",
        "pottery",
        "metal",
        "product",
        "price",
        "market",
    ],

    "hi": [
        "कारीगर",
        "हस्तशिल्प",
        "हस्तनिर्मित",
        "लकड़ी",
        "कपड़ा",
        "मिट्टी",
        "धातु",
        "उत्पाद",
        "कीमत",
        "बाज़ार",
    ],

    "kn": [
        "ಕುಶಲಕರ್ಮಿ",
        "ಕರಕುಶಲ",
        "ಕೈಮಗ್ಗ",
        "ಮರ",
        "ಬಟ್ಟೆ",
        "ಮಣ್ಣು",
        "ಲೋಹ",
        "ಉತ್ಪನ್ನ",
        "ಬೆಲೆ",
        "ಮಾರುಕಟ್ಟೆ",
    ],

    "mr": [
        "कारागीर",
        "हस्तकला",
        "हाताने",
        "लाकूड",
        "कापड",
        "माती",
        "धातू",
        "उत्पादन",
        "किंमत",
        "बाजार",
    ],
}


# ============================================================
# RESEARCH STATUS
# ============================================================

DATASET_TYPE = "synthetic"

RESEARCH_VALID = False
