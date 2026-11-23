from pathlib import Path
import os


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_DIR = PROJECT_ROOT / "ml" / "datasets" / "ocr"
DATASET_FILE = DATASET_DIR / "ocr.csv"

MODEL_DIR = PROJECT_ROOT / "ml" / "models" / "ocr"
MODEL_FILE = MODEL_DIR / "ocr_model.joblib"

RESEARCH_EXPERIMENT_DIR = (
    PROJECT_ROOT / "research" / "experiments" / "ocr"
)

RESEARCH_EVALUATION_DIR = (
    PROJECT_ROOT / "research" / "evaluation" / "ocr"
)

RESEARCH_RESULTS_DIR = (
    PROJECT_ROOT / "research" / "results" / "ocr"
)

TEST_IMAGE_DIR = DATASET_DIR / "images"


# ============================================================
# TESSERACT
# ============================================================

DEFAULT_TESSERACT_PATH = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

TESSERACT_CMD = os.getenv(
    "TESSERACT_CMD",
    DEFAULT_TESSERACT_PATH,
)


# ============================================================
# OCR SETTINGS
# ============================================================

OCR_LANGUAGE = "eng"

# Page segmentation mode.
# 6 = Assume a single uniform block of text.
TESSERACT_PSM = 6

# OCR Engine Mode.
# 3 = Default available engine.
TESSERACT_OEM = 3

MIN_CONFIDENCE = 40.0


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

IMAGE_WIDTH = 1200
IMAGE_HEIGHT = 500

GAUSSIAN_BLUR_KERNEL = (3, 3)

ADAPTIVE_BLOCK_SIZE = 31
ADAPTIVE_C = 11

UPSCALE_FACTOR = 2


# ============================================================
# TEXT INTELLIGENCE
# ============================================================

CATEGORY_KEYWORDS = {
    "wood_craft": [
        "wood",
        "wooden",
        "carving",
        "carved",
        "timber",
    ],
    "textile": [
        "textile",
        "cotton",
        "silk",
        "saree",
        "woven",
        "handwoven",
        "fabric",
    ],
    "pottery": [
        "clay",
        "pottery",
        "pot",
        "ceramic",
        "terracotta",
        "earthen",
    ],
    "metal_craft": [
        "metal",
        "brass",
        "copper",
        "bronze",
        "iron",
        "metallic",
    ],
}

MATERIAL_KEYWORDS = [
    "wood",
    "wooden",
    "cotton",
    "silk",
    "clay",
    "ceramic",
    "terracotta",
    "brass",
    "copper",
    "bronze",
    "iron",
    "metal",
    "bamboo",
    "jute",
    "wool",
    "leather",
]

CRAFT_KEYWORDS = [
    "handcrafted",
    "handmade",
    "handwoven",
    "carving",
    "carved",
    "weaving",
    "pottery",
    "craft",
    "artisan",
    "traditional",
]

# Prototype only.
RESEARCH_VALID = False
DATASET_TYPE = "synthetic"
MODEL_VERSION = "1.0.0"