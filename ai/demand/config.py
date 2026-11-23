"""
KalaSetu - Demand Prediction AI
Configuration

Model:
    XGBoost Regressor

Task:
    Predict future product demand using historical,
    temporal, product, regional, and market features.

IMPORTANT:
    Initial development uses synthetic pipeline-testing data.
    Research-valid performance will require real-world data.
"""

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_ROOT = PROJECT_ROOT / "ml" / "datasets" / "demand"
DATASET_FILE = DATASET_ROOT / "demand.csv"

MODEL_DIR = PROJECT_ROOT / "ml" / "models" / "demand"

RESEARCH_DIR = PROJECT_ROOT / "research"

EXPERIMENT_DIR = (
    RESEARCH_DIR / "experiments" / "demand"
)

EVALUATION_DIR = (
    RESEARCH_DIR / "evaluation" / "demand"
)

RESULTS_DIR = (
    RESEARCH_DIR / "results" / "demand"
)


# ============================================================
# MODEL INFORMATION
# ============================================================

MODEL_NAME = "xgboost_demand_regressor"

MODEL_VERSION = "1.0.0"

TARGET_COLUMN = "future_demand"


# ============================================================
# INPUT FEATURES
# ============================================================

NUMERIC_FEATURES = [
    "month",
    "historical_demand",
    "previous_demand",
    "price",
    "demand_growth",
]


CATEGORICAL_FEATURES = [
    "product_category",
    "region",
    "season",
]


FEATURE_COLUMNS = (
    NUMERIC_FEATURES
    + CATEGORICAL_FEATURES
)


# ============================================================
# DATA SPLIT
# ============================================================

TRAIN_RATIO = 0.70

VALIDATION_RATIO = 0.15

TEST_RATIO = 0.15

RANDOM_SEED = 42


# ============================================================
# XGBOOST PARAMETERS
# ============================================================

N_ESTIMATORS = 300

MAX_DEPTH = 6

LEARNING_RATE = 0.05

SUBSAMPLE = 0.8

COLSAMPLE_BYTREE = 0.8

MIN_CHILD_WEIGHT = 1

REG_ALPHA = 0.0

REG_LAMBDA = 1.0


# ============================================================
# PREDICTION SETTINGS
# ============================================================

MIN_PREDICTED_DEMAND = 0.0

ROUND_DEMAND_TO = 1


# ============================================================
# CREATE REQUIRED DIRECTORIES
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