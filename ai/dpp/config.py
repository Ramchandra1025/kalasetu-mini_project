from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "datasets"
    / "dpp"
    / "dpp.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "dpp"
)

MODEL_PATH = (
    MODEL_DIR
    / "dpp_model.joblib"
)

RESEARCH_EXPERIMENT_DIR = (
    PROJECT_ROOT
    / "research"
    / "experiments"
    / "dpp"
)

RESEARCH_EVALUATION_DIR = (
    PROJECT_ROOT
    / "research"
    / "evaluation"
    / "dpp"
)

RESEARCH_RESULTS_DIR = (
    PROJECT_ROOT
    / "research"
    / "results"
    / "dpp"
)


MODEL_NAME = "Digital Product Passport AI"
MODEL_VERSION = "1.0.0"

ALGORITHM = (
    "Structured Provenance + Integrity Hash + "
    "Completeness Intelligence"
)

DATASET_TYPE = "synthetic"
RESEARCH_VALID = False

PASSPORT_VERSION = "1.0"

REQUIRED_PASSPORT_FIELDS = [
    "product_id",
    "product_name",
    "artisan_id",
    "artisan_name",
    "craft_category",
    "material",
    "origin_state",
    "origin_district",
    "production_method",
    "material_source",
    "sustainability_score",
    "carbon_impact_kg_co2e",
]

COMPLETENESS_WEIGHTS = {
    "identity": 0.20,
    "artisan": 0.15,
    "craft": 0.15,
    "origin": 0.15,
    "production": 0.15,
    "sustainability": 0.20,
}