"""
KalaSetu - Buyer Matching & Recommendation AI
Configuration
"""

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_ROOT = (
    PROJECT_ROOT
    / "ml"
    / "datasets"
    / "recommendation"
)

DATASET_FILE = (
    DATASET_ROOT
    / "recommendation.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "recommendation"
)

RESEARCH_DIR = (
    PROJECT_ROOT
    / "research"
)

EXPERIMENT_DIR = (
    RESEARCH_DIR
    / "experiments"
    / "recommendation"
)

EVALUATION_DIR = (
    RESEARCH_DIR
    / "evaluation"
    / "recommendation"
)

RESULTS_DIR = (
    RESEARCH_DIR
    / "results"
    / "recommendation"
)


# ============================================================
# ENGINE INFORMATION
# ============================================================

ENGINE_NAME = (
    "hybrid_buyer_matching_engine"
)

ENGINE_VERSION = "1.0.0"


# ============================================================
# MATCHING WEIGHTS
# ============================================================

WEIGHTS = {

    "category_match":
        0.25,

    "material_match":
        0.15,

    "budget_match":
        0.20,

    "location_match":
        0.10,

    "history_match":
        0.15,

    "demand_relevance":
        0.10,

    "product_fit":
        0.05,
}


# ============================================================
# SCORE SETTINGS
# ============================================================

MIN_SCORE = 0.0

MAX_SCORE = 100.0

HIGH_MATCH_THRESHOLD = 75.0

MEDIUM_MATCH_THRESHOLD = 50.0


# ============================================================
# DATASET COLUMNS
# ============================================================

INPUT_COLUMNS = [

    "buyer_id",
    "buyer_region",
    "preferred_category",
    "preferred_material",
    "min_budget",
    "max_budget",
    "previous_category",
    "previous_material",
    "product_category",
    "product_material",
    "product_price",
    "product_region",
    "product_demand_score",
]


TARGET_COLUMN = "expected_match"


# ============================================================
# CREATE DIRECTORIES
# ============================================================

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

EXPERIMENT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

EVALUATION_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)