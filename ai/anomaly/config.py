from pathlib import Path
import os

import numpy as np
import torch


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "datasets"
    / "anomaly"
    / "anomaly.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "anomaly"
)

MODEL_PATH = MODEL_DIR / "isolation_forest.joblib"

RESEARCH_EXPERIMENT_DIR = (
    PROJECT_ROOT
    / "research"
    / "experiments"
    / "anomaly"
)

RESEARCH_EVALUATION_DIR = (
    PROJECT_ROOT
    / "research"
    / "evaluation"
    / "anomaly"
)

RESEARCH_RESULTS_DIR = (
    PROJECT_ROOT
    / "research"
    / "results"
    / "anomaly"
)


# ============================================================
# RANDOMNESS
# ============================================================

RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_NAME = "IsolationForest"
MODEL_VERSION = "1.0.0"

N_ESTIMATORS = 300
CONTAMINATION = 0.10
MAX_SAMPLES = "auto"

N_JOBS = -1


# ============================================================
# RISK THRESHOLDS
# ============================================================

HIGH_RISK_THRESHOLD = 75.0
SUSPICIOUS_THRESHOLD = 50.0


# ============================================================
# ACTIVITY TYPES
# ============================================================

ACTIVITY_TYPES = [
    "order",
    "account",
    "product",
    "transaction",
]


# ============================================================
# CATEGORICAL FEATURES
# ============================================================

CATEGORICAL_FEATURES = [
    "activity_type",
    "account_type",
    "region",
]


# ============================================================
# NUMERICAL FEATURES
# ============================================================

NUMERICAL_FEATURES = [
    "account_age_days",
    "orders_last_7_days",
    "orders_last_30_days",
    "order_quantity",
    "transaction_amount",
    "cancellation_rate",
    "price_deviation",
    "repeated_buyer_count",
    "repeated_artisan_count",
    "quantity_deviation",
    "amount_deviation",
]


# ============================================================
# MODEL FEATURES
# ============================================================

FEATURE_COLUMNS = (
    CATEGORICAL_FEATURES +
    NUMERICAL_FEATURES
)


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# RESEARCH STATUS
# ============================================================

# Current dataset is synthetic and therefore not suitable
# for claiming real-world fraud/scam detection performance.

RESEARCH_VALID = False
DATASET_TYPE = "synthetic"


# ============================================================
# DIRECTORY CREATION
# ============================================================

for directory in [
    MODEL_DIR,
    RESEARCH_EXPERIMENT_DIR,
    RESEARCH_EVALUATION_DIR,
    RESEARCH_RESULTS_DIR,
]:
    directory.mkdir(
        parents=True,
        exist_ok=True
    )