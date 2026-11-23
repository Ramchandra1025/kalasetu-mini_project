from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "datasets"
    / "nlp"
    / "product_text.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "nlp"
)

MODEL_PATH = (
    MODEL_DIR
    / "tfidf_nlp.joblib"
)

EXPERIMENT_DIR = (
    PROJECT_ROOT
    / "research"
    / "experiments"
    / "nlp"
)

EVALUATION_DIR = (
    PROJECT_ROOT
    / "research"
    / "evaluation"
    / "nlp"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "research"
    / "results"
    / "nlp"
)


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MAX_FEATURES = 5000

NGRAM_RANGE = (1, 2)

MIN_DF = 1

MAX_DF = 0.95

RANDOM_SEED = 42


# ============================================================
# QUALITY THRESHOLDS
# ============================================================

HIGH_QUALITY_THRESHOLD = 75

MEDIUM_QUALITY_THRESHOLD = 50


# ============================================================
# RESEARCH STATUS
# ============================================================

RESEARCH_VALID = False

DATASET_TYPE = "synthetic"


# ============================================================
# KALASETU VOCABULARY
# ============================================================

CATEGORY_KEYWORDS = {
    "wood_craft": [
        "wood",
        "wooden",
        "timber",
        "carved",
        "woodcraft",
    ],
    "textile": [
        "textile",
        "cotton",
        "silk",
        "fabric",
        "cloth",
        "woven",
        "weaving",
        "handloom",
    ],
    "pottery": [
        "pottery",
        "pot",
        "clay",
        "ceramic",
        "terracotta",
        "earthen",
    ],
    "metal_craft": [
        "metal",
        "brass",
        "copper",
        "iron",
        "steel",
        "metallic",
    ],
}


# ============================================================
# REQUIRED DESCRIPTION CONCEPTS
# ============================================================

DESCRIPTION_CONCEPTS = [
    "material",
    "craft",
    "handmade",
    "artisan",
    "traditional",
    "dimensions",
    "usage",
]