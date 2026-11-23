"""
KalaSetu - Market Opportunity Intelligence
Configuration
"""

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_ROOT = PROJECT_ROOT / "ml" / "datasets" / "market"

DATASET_FILE = DATASET_ROOT / "market.csv"

MODEL_DIR = PROJECT_ROOT / "ml" / "models" / "market"

RESEARCH_DIR = PROJECT_ROOT / "research"

EXPERIMENT_DIR = (
    RESEARCH_DIR / "experiments" / "market"
)

EVALUATION_DIR = (
    RESEARCH_DIR / "evaluation" / "market"
)

RESULTS_DIR = (
    RESEARCH_DIR / "results" / "market"
)


# ============================================================
# ENGINE INFORMATION
# ============================================================

ENGINE_NAME = (
    "explainable_market_opportunity_engine"
)

ENGINE_VERSION = "1.0.0"


# ============================================================
# INPUT FEATURES
# ============================================================

NUMERIC_FEATURES = [
    "demand_score",
    "price_opportunity",
    "market_growth",
    "regional_fit",
    "seasonality_score",
    "competition_score",
]


CATEGORICAL_FEATURES = [
    "product_category",
    "region",
]


FEATURE_COLUMNS = (
    NUMERIC_FEATURES
    + CATEGORICAL_FEATURES
)


TARGET_COLUMN = "expected_opportunity"


# ============================================================
# SCORE WEIGHTS
# ============================================================

WEIGHTS = {
    "demand_score": 0.30,
    "price_opportunity": 0.20,
    "market_growth": 0.15,
    "regional_fit": 0.15,
    "seasonality_score": 0.10,
    "competition_score": 0.10,
}


# ============================================================
# SCORE SETTINGS
# ============================================================

MIN_SCORE = 0.0
MAX_SCORE = 100.0

HIGH_OPPORTUNITY_THRESHOLD = 75.0
MEDIUM_OPPORTUNITY_THRESHOLD = 50.0


# ============================================================
# RANDOM SEED
# ============================================================

RANDOM_SEED = 42


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