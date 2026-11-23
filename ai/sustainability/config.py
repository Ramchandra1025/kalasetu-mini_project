from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "datasets"
    / "sustainability"
    / "sustainability.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "sustainability"
)

MODEL_PATH = (
    MODEL_DIR
    / "sustainability_model.joblib"
)

RESEARCH_EXPERIMENT_DIR = (
    PROJECT_ROOT
    / "research"
    / "experiments"
    / "sustainability"
)

RESEARCH_EVALUATION_DIR = (
    PROJECT_ROOT
    / "research"
    / "evaluation"
    / "sustainability"
)

RESEARCH_RESULTS_DIR = (
    PROJECT_ROOT
    / "research"
    / "results"
    / "sustainability"
)


MODEL_NAME = "Sustainability Intelligence AI"
MODEL_VERSION = "1.0.0"

ALGORITHM = "Explainable Sustainability Scoring"

RANDOM_SEED = 42

DATASET_TYPE = "synthetic"

RESEARCH_VALID = False


# Material sustainability factors.
# Higher value means relatively better sustainability
# for this prototype scoring system.
MATERIAL_SUSTAINABILITY = {
    "bamboo": 95,
    "clay": 90,
    "cotton": 75,
    "wood": 78,
    "metal": 65,
    "leather": 45,
    "plastic": 20,
}


# Approximate prototype emission factors.
# These are NOT certified lifecycle-assessment values.
MATERIAL_CARBON_FACTOR = {
    "bamboo": 0.4,
    "clay": 0.8,
    "cotton": 1.5,
    "wood": 0.7,
    "metal": 2.5,
    "leather": 3.0,
    "plastic": 3.2,
}


PACKAGING_SUSTAINABILITY = {
    "recycled": 95,
    "paper": 85,
    "cloth": 90,
    "biodegradable": 98,
    "mixed": 55,
    "plastic": 20,
}


RECYCLABILITY_SCORE = {
    "high": 95,
    "medium": 65,
    "low": 30,
}


LOCAL_SOURCING_SCORE = {
    "local": 95,
    "regional": 75,
    "national": 50,
    "international": 20,
}