"""Configuration for KalaSetu fair-pricing experiments."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = PROJECT_ROOT / "ml" / "datasets" / "pricing"
DATASET_FILE = DATASET_ROOT / "pricing.csv"
MODEL_DIR = PROJECT_ROOT / "ml" / "models" / "pricing"
RESEARCH_DIR = PROJECT_ROOT / "research"
EXPERIMENT_DIR = RESEARCH_DIR / "experiments" / "pricing"
EVALUATION_DIR = RESEARCH_DIR / "evaluation" / "pricing"
RESULTS_DIR = RESEARCH_DIR / "results" / "pricing"

TARGET_COLUMN = "fair_price"
NUMERIC_FEATURES = [
    "size_cm", "production_hours", "material_cost", "labor_cost",
    "demand_score", "complexity_score",
]
CATEGORICAL_FEATURES = ["craft_category", "material", "region"]

# Derived values are deterministic and use input columns only.
ENGINEERED_NUMERIC_FEATURES = [
    "total_cost", "labor_cost_per_hour", "material_cost_per_size",
    "hours_per_size", "production_complexity", "demand_normalized",
    "demand_complexity", "log_size", "labor_material_ratio",
    "labor_cost_ratio", "material_cost_ratio",
]
MODEL_FEATURES = NUMERIC_FEATURES + ENGINEERED_NUMERIC_FEATURES + CATEGORICAL_FEATURES

TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15
TEST_RATIO = 0.15
RANDOM_SEED = 42

# Keep the initial XGBoost capacity conservative for small tabular datasets.
N_ESTIMATORS = 250
MAX_DEPTH = 3
LEARNING_RATE = 0.03
SUBSAMPLE = 0.85
COLSAMPLE_BYTREE = 0.85
MIN_CHILD_WEIGHT = 2
REG_ALPHA = 0.05
REG_LAMBDA = 3.0

RF_N_ESTIMATORS = 400
RF_MAX_DEPTH = 8
CATBOOST_ITERATIONS = 400
CATBOOST_DEPTH = 5
CATBOOST_LEARNING_RATE = 0.03

MIN_PREDICTED_PRICE = 1.0
ROUND_PRICE_TO = 1
MODEL_NAME = "fair_pricing_model_comparison"
MODEL_VERSION = "2.0.0"
CANDIDATE_MODELS = ["xgboost", "random_forest", "catboost"]

for directory in (MODEL_DIR, EXPERIMENT_DIR, EVALUATION_DIR, RESULTS_DIR):
    directory.mkdir(parents=True, exist_ok=True)
