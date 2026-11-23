from pathlib import Path
import torch


# ============================================================
# KalaSetu
# AI Product Vision & Cataloguing
#
# Configuration
# ============================================================


# ------------------------------------------------------------
# Project paths
# ------------------------------------------------------------

# config.py is:
# E:\kalasetu\ai\cataloguing\config.py
#
# parents[0] = cataloguing
# parents[1] = ai
# parents[2] = kalasetu

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ------------------------------------------------------------
# Dataset paths
# ------------------------------------------------------------

DATASET_DIR = (
    PROJECT_ROOT
    / "ml"
    / "datasets"
    / "cataloguing"
)

DATASET_CSV = (
    DATASET_DIR
    / "cataloguing.csv"
)

IMAGE_DIR = (
    DATASET_DIR
    / "images"
)


# ------------------------------------------------------------
# Model paths
# ------------------------------------------------------------

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "cataloguing"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


BEST_MODEL_PATH = (
    MODEL_DIR
    / "best_model.pth"
)

LABEL_MAP_PATH = (
    MODEL_DIR
    / "label_maps.json"
)


# ------------------------------------------------------------
# Research paths
# ------------------------------------------------------------

RESEARCH_DIR = (
    PROJECT_ROOT
    / "research"
)

EXPERIMENT_DIR = (
    RESEARCH_DIR
    / "experiments"
    / "cataloguing"
)

EVALUATION_DIR = (
    RESEARCH_DIR
    / "evaluation"
    / "cataloguing"
)

RESULTS_DIR = (
    RESEARCH_DIR
    / "results"
    / "cataloguing"
)


for directory in [
    EXPERIMENT_DIR,
    EVALUATION_DIR,
    RESULTS_DIR,
]:
    directory.mkdir(
        parents=True,
        exist_ok=True
    )


# ------------------------------------------------------------
# Dataset configuration
# ------------------------------------------------------------

IMAGE_SIZE = 224

# We keep this small for CPU testing.
# Later, after increasing the dataset,
# we can adjust this.

BATCH_SIZE = 4


# ------------------------------------------------------------
# Dataset split
# ------------------------------------------------------------

TRAIN_RATIO = 0.70

VALIDATION_RATIO = 0.15

TEST_RATIO = 0.15


# ------------------------------------------------------------
# Reproducibility
# ------------------------------------------------------------

RANDOM_SEED = 42


# ------------------------------------------------------------
# Model configuration
# ------------------------------------------------------------

MODEL_NAME = "efficientnet_b0"

PRETRAINED = True

DROPOUT = 0.30


# ------------------------------------------------------------
# Training configuration
# ------------------------------------------------------------

NUM_EPOCHS = 10

LEARNING_RATE = 0.0001

WEIGHT_DECAY = 0.0001


# ------------------------------------------------------------
# Initial labels
# ------------------------------------------------------------

# IMPORTANT:
#
# These are only our initial dataset classes.
# The model will actually build its final label mappings
# from the dataset CSV.
#
# We can expand these later.

CATEGORIES = [
    "wood_craft",
    "textile",
    "pottery",
    "metal_craft",
]


MATERIALS = [
    "wood",
    "cotton",
    "clay",
    "metal",
]


COLORS = [
    "brown",
    "red",
    "blue",
    "green",
    "orange",
    "white",
    "gold",
    "silver",
    "bronze",
]


# ------------------------------------------------------------
# Device
# ------------------------------------------------------------

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ------------------------------------------------------------
# Information
# ------------------------------------------------------------

def print_config():

    print()
    print("=" * 60)
    print("KalaSetu AI Product Cataloguing")
    print("=" * 60)

    print(f"Project root       : {PROJECT_ROOT}")

    print(f"Dataset CSV        : {DATASET_CSV}")

    print(f"Image directory     : {IMAGE_DIR}")

    print(f"Model directory     : {MODEL_DIR}")

    print(f"Best model path     : {BEST_MODEL_PATH}")

    print(f"Label map path      : {LABEL_MAP_PATH}")

    print(f"Image size          : {IMAGE_SIZE}")

    print(f"Batch size          : {BATCH_SIZE}")

    print(f"Epochs              : {NUM_EPOCHS}")

    print(f"Learning rate       : {LEARNING_RATE}")

    print(f"Model               : {MODEL_NAME}")

    print(f"Device              : {DEVICE}")

    print("=" * 60)
    print()


if __name__ == "__main__":

    print_config()