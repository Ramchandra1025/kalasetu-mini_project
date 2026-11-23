"""Train and compare pricing candidates; retain XGBoost as active until evidence supports change."""
import json
from datetime import datetime, timezone

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .config import (
    DATASET_FILE, EXPERIMENT_DIR, RESULTS_DIR, RANDOM_SEED,
    CANDIDATE_MODELS,
)
from .dataset import create_datasets
from .model import (
    create_model, predict_price, save_model, get_feature_importance,
    prepare_catboost_frame,
)


def _metrics(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    nonzero = y_true != 0
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)) if len(y_true) >= 2 else None,
        "mape": float(np.mean(np.abs((y_true[nonzero] - y_pred[nonzero]) / y_true[nonzero])) * 100)
        if np.any(nonzero) else None,
    }


def _cost_plus_baseline(frame):
    """Transparent baseline: predict direct material + labour cost, no invented margin."""
    return (
        frame["material_cost"].to_numpy(dtype=float)
        + frame["labor_cost"].to_numpy(dtype=float)
    )


def main():
    data = create_datasets()
    X_train, X_val, X_test = data["X_train"], data["X_validation"], data["X_test"]
    y_train, y_val = data["y_train"], data["y_validation"]
    val_rows = data["validation_dataframe"]

    comparison = {}
    fitted = {}
    for name in CANDIDATE_MODELS:
        try:
            model = create_model(name)
            if name == "catboost":
                train_frame = prepare_catboost_frame(X_train)
                val_frame = prepare_catboost_frame(X_val)
                model.fit(train_frame, y_train, cat_features=[
                    X_train.columns.get_loc(c) for c in ("craft_category", "material", "region")
                ])
                predictions = model.predict(val_frame)
            else:
                model.fit(X_train, y_train)
                predictions = predict_price(model, X_val)
            comparison[name] = {
                "status": "trained",
                "validation_metrics": _metrics(y_val, predictions),
            }
            fitted[name] = model
        except ImportError as exc:
            comparison[name] = {"status": "skipped_dependency_missing", "reason": str(exc)}

    baseline_predictions = _cost_plus_baseline(val_rows)
    comparison["cost_plus_direct_cost"] = {
        "status": "baseline",
        "validation_metrics": _metrics(y_val, baseline_predictions),
        "note": "Direct material + labour cost only; excludes overhead and margin.",
    }

    # Keep the current production family until a meaningful dataset supports selection.
    active_name = "xgboost"
    if active_name not in fitted:
        raise RuntimeError("XGBoost training failed; no production artifact was changed.")
    active_model = fitted[active_name]
    importance = get_feature_importance(active_model, data["feature_names"])
    save_model(active_model, feature_names=data["feature_names"], model_name=active_name)

    result = {
        "experiment": "fair_pricing_candidate_comparison_v2",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "dataset_file": str(DATASET_FILE),
        "dataset_rows": int(len(data["dataframe"])),
        "split_sizes": {
            "train": int(len(X_train)),
            "validation": int(len(X_val)),
            "test_reserved": int(len(X_test)),
        },
        "random_seed": RANDOM_SEED,
        "candidates": comparison,
        "active_model": active_name,
        "selection_policy": (
            "XGBoost remains active during pipeline upgrade. Validation on the current "
            "30-row synthetic dataset is too small for reliable model selection."
        ),
        "feature_importance": importance,
        "data_type": data["data_type"],
        "research_valid": False,
        "warning": "Synthetic pipeline-testing data only; do not report these metrics as research evidence.",
    }
    (EXPERIMENT_DIR / "model_comparison.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (RESULTS_DIR / "training_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("Pricing candidate comparison completed.")
    print(json.dumps(comparison, indent=2))
    print(f"Active model saved: {active_name}")
    print("Research-valid: NO (synthetic 30-row dataset).")


if __name__ == "__main__":
    main()
