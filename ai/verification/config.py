from pathlib import Path
import torch


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_ROOT = (
    PROJECT_ROOT
    / "ml"
    / "datasets"
    / "verification"
)

REFERENCE_DIR = DATASET_ROOT / "reference"

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "verification"
)

RESEARCH_DIR = (
    PROJECT_ROOT
    / "research"
)

RESULTS_DIR = RESEARCH_DIR / "results" / "verification"
EVALUATION_DIR = RESEARCH_DIR / "evaluation" / "verification"


# ============================================================
# IMAGE SETTINGS
# ============================================================

IMAGE_SIZE = 224

IMAGE_MEAN = [
    0.485,
    0.456,
    0.406
]

IMAGE_STD = [
    0.229,
    0.224,
    0.225
]


# ============================================================
# MODEL SETTINGS
# ============================================================

MODEL_NAME = "efficientnet_b0"

PRETRAINED = True

EMBEDDING_DIMENSION = 1280


# ============================================================
# VERIFICATION SETTINGS
# ============================================================

# Cosine similarity threshold.
#
# This is only an initial engineering threshold.
# It must be calibrated later using a real validation dataset.

VERIFICATION_THRESHOLD = 0.75


# ============================================================
# CRAFT CATEGORIES
# ============================================================

CRAFT_CATEGORIES = [
    "wood_craft",
    "textile",
    "pottery",
    "metal_craft",
]


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# DIRECTORY CREATION
# ============================================================

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

EVALUATION_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CONFIG TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("KALASETU - CRAFT VERIFICATION CONFIGURATION")
    print("=" * 60)

    print(f"Project Root       : {PROJECT_ROOT}")
    print(f"Dataset Root       : {DATASET_ROOT}")
    print(f"Reference Directory: {REFERENCE_DIR}")
    print(f"Model Directory    : {MODEL_DIR}")

    print(f"Image Size         : {IMAGE_SIZE}")
    print(f"Model              : {MODEL_NAME}")
    print(f"Embedding Dimension: {EMBEDDING_DIMENSION}")

    print(
        f"Verification Threshold: "
        f"{VERIFICATION_THRESHOLD}"
    )

    print(f"Device             : {DEVICE}")

    print("\nCraft Categories:")

    for category in CRAFT_CATEGORIES:
        print(f"  - {category}")

    print("\nConfiguration test PASSED.")