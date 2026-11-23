"""Pricing regressors with preprocessing fitted only on training rows."""
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from .config import (
    MODEL_DIR, NUMERIC_FEATURES, ENGINEERED_NUMERIC_FEATURES,
    CATEGORICAL_FEATURES, RANDOM_SEED, N_ESTIMATORS, MAX_DEPTH,
    LEARNING_RATE, SUBSAMPLE, COLSAMPLE_BYTREE, MIN_CHILD_WEIGHT,
    REG_ALPHA, REG_LAMBDA, RF_N_ESTIMATORS, RF_MAX_DEPTH,
)

MODEL_FILE = MODEL_DIR / "fair_pricing_model.joblib"
LEGACY_MODEL_FILE = MODEL_DIR / "fair_pricing_model.json"
METADATA_FILE = MODEL_DIR / "model_metadata.json"
ENCODER_FILE = MODEL_DIR / "feature_encoder.joblib"  # legacy path; not used by v2


def _one_hot_encoder():
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def _preprocessor():
    numeric = NUMERIC_FEATURES + ENGINEERED_NUMERIC_FEATURES
    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
    ])
    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", _one_hot_encoder()),
    ])
    return ColumnTransformer([
        ("numeric", numeric_pipe, numeric),
        ("categorical", categorical_pipe, CATEGORICAL_FEATURES),
    ], remainder="drop")


def create_model(model_name="xgboost"):
    """Build one candidate pipeline. Preprocessing is fitted inside fit()."""
    if model_name == "xgboost":
        try:
            from xgboost import XGBRegressor
        except ImportError as exc:
            raise ImportError("Install xgboost to train the XGBoost candidate.") from exc
        estimator = XGBRegressor(
            objective="reg:squarederror",
            n_estimators=N_ESTIMATORS,
            max_depth=MAX_DEPTH,
            learning_rate=LEARNING_RATE,
            subsample=SUBSAMPLE,
            colsample_bytree=COLSAMPLE_BYTREE,
            min_child_weight=MIN_CHILD_WEIGHT,
            reg_alpha=REG_ALPHA,
            reg_lambda=REG_LAMBDA,
            random_state=RANDOM_SEED,
            n_jobs=-1,
        )
        return Pipeline([("preprocessor", _preprocessor()), ("regressor", estimator)])

    if model_name == "random_forest":
        estimator = RandomForestRegressor(
            n_estimators=RF_N_ESTIMATORS,
            max_depth=RF_MAX_DEPTH,
            min_samples_leaf=2,
            max_features=0.9,
            random_state=RANDOM_SEED,
            n_jobs=-1,
        )
        return Pipeline([("preprocessor", _preprocessor()), ("regressor", estimator)])

    if model_name == "catboost":
        try:
            from catboost import CatBoostRegressor
        except ImportError as exc:
            raise ImportError("Install catboost to train the CatBoost candidate.") from exc
        # CatBoost consumes categorical columns directly; no one-hot encoding.
        return CatBoostRegressor(
            iterations=400,
            depth=5,
            learning_rate=0.03,
            loss_function="RMSE",
            random_seed=RANDOM_SEED,
            verbose=False,
            allow_writing_files=False,
        )

    raise ValueError(f"Unknown pricing model: {model_name}")


def train_model(X_train, y_train, X_validation=None, y_validation=None):
    model = create_model("xgboost")
    model.fit(X_train, y_train)
    return model


def predict_price(model, features):
    predictions = np.asarray(model.predict(features), dtype=np.float64)
    if not np.all(np.isfinite(predictions)):
        raise ValueError("Model returned non-finite price predictions.")
    return np.maximum(predictions, 1.0)


def get_feature_importance(model, feature_names=None):
    estimator = model.named_steps["regressor"] if hasattr(model, "named_steps") else model
    values = getattr(estimator, "feature_importances_", None)
    if values is None:
        return []
    try:
        names = model.named_steps["preprocessor"].get_feature_names_out()
    except Exception:
        names = feature_names or [f"feature_{i}" for i in range(len(values))]
    return sorted(
        [{"feature": str(name), "importance": float(value)}
         for name, value in zip(names, values)],
        key=lambda item: item["importance"],
        reverse=True,
    )


def save_model(model, encoder=None, feature_names=None, model_name="xgboost"):
    """Persist complete fitted pipeline so inference uses identical preprocessing."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    metadata = {
        "model_name": model_name,
        "model_version": "2.0.0",
        "model_type": type(model).__name__,
        "target": "fair_price",
        "feature_names": list(feature_names or []),
        "artifact": MODEL_FILE.name,
        "preprocessing": "fitted sklearn Pipeline; train-only fit",
        "data_type": "synthetic_pipeline_testing_data",
        "research_valid": False,
    }
    METADATA_FILE.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return MODEL_FILE


def load_model():
    if MODEL_FILE.exists():
        return joblib.load(MODEL_FILE)
    # Backward compatibility for an older deployment artifact.
    if LEGACY_MODEL_FILE.exists():
        import xgboost as xgb
        legacy = xgb.XGBRegressor()
        legacy.load_model(str(LEGACY_MODEL_FILE))
        return legacy
    raise FileNotFoundError(f"Pricing model not found: {MODEL_FILE}")


def load_encoder():
    """Legacy helper retained for external callers; v2 pipeline embeds preprocessing."""
    if ENCODER_FILE.exists():
        return joblib.load(ENCODER_FILE)
    raise FileNotFoundError("V2 pricing pipeline embeds its preprocessor; no separate encoder exists.")


def prepare_catboost_frame(frame):
    """Ensure CatBoost categorical columns are strings and ordered consistently."""
    result = frame.copy()
    for column in CATEGORICAL_FEATURES:
        result[column] = result[column].astype(str).fillna("unknown")
    return result
