from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "datasets"
    / "logistics"
    / "logistics.csv"
)

MODEL_DIR = PROJECT_ROOT / "ml" / "models" / "logistics"
MODEL_PATH = MODEL_DIR / "logistics_model.joblib"

RESEARCH_EXPERIMENT_DIR = (
    PROJECT_ROOT / "research" / "experiments" / "logistics"
)

RESEARCH_EVALUATION_DIR = (
    PROJECT_ROOT / "research" / "evaluation" / "logistics"
)

RESEARCH_RESULTS_DIR = (
    PROJECT_ROOT / "research" / "results" / "logistics"
)


MODEL_NAME = "Smart Logistics AI"
MODEL_VERSION = "1.0.0"

ALGORITHM = "Geographic Clustering + OR-Tools VRP"

RANDOM_SEED = 42

DEFAULT_VEHICLE_COUNT = 4
DEFAULT_VEHICLE_CAPACITY = 10

AVERAGE_SPEED_KMPH = 30

CLUSTER_COUNT = 2

DATASET_TYPE = "synthetic"

RESEARCH_VALID = False