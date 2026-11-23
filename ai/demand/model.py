"""
KalaSetu - Demand Prediction AI
XGBoost Model
"""

import json

import joblib
import numpy as np
import xgboost as xgb

from .config import (
    MODEL_DIR,
    MODEL_NAME,
    MODEL_VERSION,
    N_ESTIMATORS,
    MAX_DEPTH,
    LEARNING_RATE,
    SUBSAMPLE,
    COLSAMPLE_BYTREE,
    MIN_CHILD_WEIGHT,
    REG_ALPHA,
    REG_LAMBDA,
    MIN_PREDICTED_DEMAND,
)


MODEL_FILE = (
    MODEL_DIR
    / "demand_prediction_model.json"
)

ENCODER_FILE = (
    MODEL_DIR
    / "feature_encoder.joblib"
)

METADATA_FILE = (
    MODEL_DIR
    / "model_metadata.json"
)


# ============================================================
# CREATE MODEL
# ============================================================

def create_model():

    model = xgb.XGBRegressor(
        objective="reg:squarederror",
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        learning_rate=LEARNING_RATE,
        subsample=SUBSAMPLE,
        colsample_bytree=COLSAMPLE_BYTREE,
        min_child_weight=MIN_CHILD_WEIGHT,
        reg_alpha=REG_ALPHA,
        reg_lambda=REG_LAMBDA,
        random_state=42,
        n_jobs=-1,
    )

    return model


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model(
    X_train,
    y_train,
    X_validation=None,
    y_validation=None,
):

    model = create_model()

    if (
        X_validation is not None
        and y_validation is not None
    ):

        model.fit(
            X_train,
            y_train,
            eval_set=[
                (X_train, y_train),
                (
                    X_validation,
                    y_validation,
                ),
            ],
            verbose=False,
        )

    else:

        model.fit(
            X_train,
            y_train,
            verbose=False,
        )

    return model


# ============================================================
# PREDICT
# ============================================================

def predict_demand(
    model,
    features,
):

    predictions = model.predict(
        features
    )

    predictions = np.asarray(
        predictions,
        dtype=np.float64,
    )

    predictions = np.nan_to_num(
        predictions,
        nan=0.0,
        posinf=0.0,
        neginf=0.0,
    )

    predictions = np.maximum(
        predictions,
        MIN_PREDICTED_DEMAND,
    )

    return predictions


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

def get_feature_importance(
    model,
    feature_names,
):

    importance = (
        model.feature_importances_
    )

    results = []

    for name, value in zip(
        feature_names,
        importance,
    ):

        results.append(
            {
                "feature": name,
                "importance": float(
                    value
                ),
            }
        )

    results.sort(
        key=lambda item:
        item["importance"],
        reverse=True,
    )

    return results


# ============================================================
# SAVE MODEL
# ============================================================

def save_model(
    model,
    encoder,
    feature_names,
):

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model.save_model(
        str(MODEL_FILE)
    )

    joblib.dump(
        encoder,
        ENCODER_FILE,
    )

    metadata = {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "model_type": "XGBRegressor",
        "target": "future_demand",
        "feature_count": len(
            feature_names
        ),
        "feature_names": feature_names,
        "model_file": MODEL_FILE.name,
        "encoder_file": ENCODER_FILE.name,
        "data_type": (
            "synthetic_pipeline_testing_data"
        ),
        "research_valid": False,
    }

    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4,
        )


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    if not MODEL_FILE.exists():

        raise FileNotFoundError(
            f"Demand model not found:\n"
            f"{MODEL_FILE}"
        )

    model = xgb.XGBRegressor()

    model.load_model(
        str(MODEL_FILE)
    )

    return model


# ============================================================
# LOAD ENCODER
# ============================================================

def load_encoder():

    if not ENCODER_FILE.exists():

        raise FileNotFoundError(
            f"Demand encoder not found:\n"
            f"{ENCODER_FILE}"
        )

    return joblib.load(
        ENCODER_FILE
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("KALASETU - DEMAND MODEL TEST")
    print("=" * 70)

    model = create_model()

    print(
        f"Model Type      : "
        f"{type(model).__name__}"
    )

    print(
        f"Estimators      : "
        f"{N_ESTIMATORS}"
    )

    print(
        f"Max Depth       : "
        f"{MAX_DEPTH}"
    )

    print(
        f"Learning Rate   : "
        f"{LEARNING_RATE}"
    )

    print(
        "\nMODEL CREATION TEST PASSED."
    )

    print("=" * 70)