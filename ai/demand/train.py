"""Train and evaluate KalaSetu demand regression.

The test partition is kept out of fitting and validation decisions. Because the
current sample data is synthetic and has no timestamp column, this is a
reproducible random holdout—not a chronological forecasting backtest.
"""
import json
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .dataset import create_datasets
from .model import train_model, predict_demand, get_feature_importance, save_model
from .config import EXPERIMENT_DIR, RESULTS_DIR


def regression_metrics(actual, predicted):
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    nonzero = actual != 0
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "r2": float(r2_score(actual, predicted)) if len(actual) > 1 else None,
        "mape_percent": (
            float(np.mean(np.abs((actual[nonzero] - predicted[nonzero]) / actual[nonzero])) * 100)
            if np.any(nonzero) else None
        ),
    }


def main():
    datasets = create_datasets()
    model = train_model(
        datasets["X_train"], datasets["y_train"],
        datasets["X_validation"], datasets["y_validation"],
    )

    validation_predictions = predict_demand(model, datasets["X_validation"])
    test_predictions = predict_demand(model, datasets["X_test"])
    validation_metrics = regression_metrics(
        datasets["y_validation"], validation_predictions
    )
    test_metrics = regression_metrics(datasets["y_test"], test_predictions)

    importance = get_feature_importance(model, datasets["feature_names"])
    save_model(model, datasets["encoder"], datasets["feature_names"])

    summary = {
        "model": "XGBRegressor",
        "model_name": "xgboost_demand_regressor",
        "model_version": "1.1.0",
        "target": "future_demand",
        "split_sizes": datasets["split_sizes"],
        "validation_metrics": validation_metrics,
        "held_out_test_metrics": test_metrics,
        "feature_count": len(datasets["feature_names"]),
        "feature_importance": importance,
        "preprocessing_fit_scope": "training_rows_only",
        "split_strategy": "random_holdout_no_timestamp_available",
        "data_type": "synthetic_pipeline_testing_data",
        "research_valid": False,
        "research_note": (
            "Synthetic data only. Metrics are pipeline diagnostics, not evidence "
            "of real-world demand forecasting performance. Collect dated product "
            "sales/orders and use chronological backtesting before research claims."
        ),
    }

    for directory, filename in (
        (EXPERIMENT_DIR, "training_summary.json"),
        (RESULTS_DIR, "training_result.json"),
    ):
        directory.mkdir(parents=True, exist_ok=True)
        (directory / filename).write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )

    print("Demand model training and holdout evaluation completed.")
    print(json.dumps({
        "validation_metrics": validation_metrics,
        "held_out_test_metrics": test_metrics,
        "research_valid": False,
    }, indent=2))


if __name__ == "__main__":
    main()
