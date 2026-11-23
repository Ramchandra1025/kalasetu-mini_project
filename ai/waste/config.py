from pathlib import Path
import torch


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "datasets"
    / "waste"
    / "waste.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "waste"
)

RESEARCH_DIR = (
    PROJECT_ROOT
    / "research"
    / "experiments"
    / "waste"
)


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# SCORING WEIGHTS
# ============================================================

WEIGHTS = {
    "material_reuse": 0.25,
    "quantity": 0.15,
    "condition": 0.15,
    "compatibility": 0.20,
    "demand": 0.10,
    "processing": 0.15,
}


# ============================================================
# FEASIBILITY THRESHOLDS
# ============================================================

HIGH_THRESHOLD = 75.0
MEDIUM_THRESHOLD = 50.0


# ============================================================
# VALUE ESTIMATION
# ============================================================

# Prototype recoverable-value multipliers.
# These are estimates, not market prices.

VALUE_MULTIPLIERS = {
    "wood": 180.0,
    "cotton": 140.0,
    "clay": 90.0,
    "metal": 220.0,
}


# ============================================================
# CATEGORIES
# ============================================================

WASTE_TYPES = [
    "wood",
    "cotton",
    "clay",
    "metal",
]

CRAFT_CATEGORIES = [
    "wood_craft",
    "textile",
    "pottery",
    "metal_craft",
]

CONDITIONS = [
    "excellent",
    "good",
    "usable",
    "damaged",
]