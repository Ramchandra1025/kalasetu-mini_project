from pathlib import Path


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "datasets"
    / "inventory"
    / "inventory.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "inventory"
)

MODEL_PATH = MODEL_DIR / "inventory_model.joblib"

RESEARCH_EXPERIMENT_DIR = (
    PROJECT_ROOT
    / "research"
    / "experiments"
    / "inventory"
)

RESEARCH_EVALUATION_DIR = (
    PROJECT_ROOT
    / "research"
    / "evaluation"
    / "inventory"
)

RESEARCH_RESULTS_DIR = (
    PROJECT_ROOT
    / "research"
    / "results"
    / "inventory"
)


# ---------------------------------------------------------
# MODEL INFORMATION
# ---------------------------------------------------------

MODEL_NAME = "Inventory Intelligence AI"
MODEL_VERSION = "1.0.0"

ALGORITHM = "XGBoost Classifier"

RANDOM_SEED = 42


# ---------------------------------------------------------
# INVENTORY THRESHOLDS
# ---------------------------------------------------------

LOW_STOCK_COVERAGE_DAYS = 7

CRITICAL_STOCK_COVERAGE_DAYS = 3

OVERSTOCK_COVERAGE_DAYS = 60

DEFAULT_LEAD_TIME_DAYS = 7

SAFETY_STOCK_DAYS = 3


# ---------------------------------------------------------
# STOCK STATUS LABELS
# ---------------------------------------------------------

STOCK_HEALTHY = "HEALTHY"
STOCK_LOW = "LOW_STOCK"
STOCK_CRITICAL = "CRITICAL"
STOCK_OVERSTOCK = "OVERSTOCK"


# ---------------------------------------------------------
# DATASET STATUS
# ---------------------------------------------------------

DATASET_TYPE = "synthetic"

RESEARCH_VALID = False