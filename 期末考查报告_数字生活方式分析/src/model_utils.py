from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    calinski_harabasz_score,
    confusion_matrix,
    davies_bouldin_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    silhouette_score,
)
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import (
    GridSearchCV,
    KFold,
    ParameterGrid,
    RandomizedSearchCV,
    StratifiedKFold,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

try:
    from .config import (
        CLASSIFICATION_CONFUSION_PATH,
        CLASSIFICATION_CV_RESULTS_PATH,
        CLASSIFICATION_FEATURE_IMPORTANCE_PATH,
        CLASSIFICATION_FINAL_CONFUSION_PATH,
        CLASSIFICATION_METRICS_PATH,
        CLASSIFICATION_MODEL_SELECTION_SUMMARY_PATH,
        CLASSIFICATION_TARGET,
        CLASSIFICATION_THRESHOLD_TUNING_PATH,
        CLASSIFICATION_TUNED_METRICS_PATH,
        CLUSTER_PROFILE_CONTEXT_COLUMNS,
        CLUSTERING_ASSIGNMENTS_PATH,
        CLUSTERING_MODEL_COMPARISON_PATH,
        CLUSTERING_PCA_PATH,
        CLUSTERING_PROFILE_INTERPRETATION_PATH,
        CLUSTERING_PROFILE_PATH,
        CLUSTERING_SCORES_PATH,
        MODEL_TEST_SIZE,
        RANDOM_STATE,
        REGRESSION_BACKUP_TARGET,
        REGRESSION_FEATURE_IMPORTANCE_PATH,
        REGRESSION_METRICS_PATH,
        REGRESSION_MODEL_SELECTION_SUMMARY_PATH,
        REGRESSION_PREDICTIONS_PATH,
        REGRESSION_TARGET,
        REGRESSION_TARGET_COMPARISON_PATH,
        RESULTS_DIR,
    )
    from .feature_engineering import add_behavior_features, make_feature_target, make_preprocessor
except ImportError:
    from config import (
        CLASSIFICATION_CONFUSION_PATH,
        CLASSIFICATION_CV_RESULTS_PATH,
        CLASSIFICATION_FEATURE_IMPORTANCE_PATH,
        CLASSIFICATION_FINAL_CONFUSION_PATH,
        CLASSIFICATION_METRICS_PATH,
        CLASSIFICATION_MODEL_SELECTION_SUMMARY_PATH,
        CLASSIFICATION_TARGET,
        CLASSIFICATION_THRESHOLD_TUNING_PATH,
        CLASSIFICATION_TUNED_METRICS_PATH,
        CLUSTER_PROFILE_CONTEXT_COLUMNS,
        CLUSTERING_ASSIGNMENTS_PATH,
        CLUSTERING_MODEL_COMPARISON_PATH,
        CLUSTERING_PCA_PATH,
        CLUSTERING_PROFILE_INTERPRETATION_PATH,
        CLUSTERING_PROFILE_PATH,
        CLUSTERING_SCORES_PATH,
        MODEL_TEST_SIZE,
        RANDOM_STATE,
        REGRESSION_BACKUP_TARGET,
        REGRESSION_FEATURE_IMPORTANCE_PATH,
        REGRESSION_METRICS_PATH,
        REGRESSION_MODEL_SELECTION_SUMMARY_PATH,
        REGRESSION_PREDICTIONS_PATH,
        REGRESSION_TARGET,
        REGRESSION_TARGET_COMPARISON_PATH,
        RESULTS_DIR,
    )
    from feature_engineering import add_behavior_features, make_feature_target, make_preprocessor


def _ensure_results_dir() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def _search_iterations(param_grid: dict[str, list[Any]], cap: int = 16) -> int:
    return min(cap, len(list(ParameterGrid(param_grid))))


def classification_models() -> dict[str, object]:
    return {
        "logistic_regression": LogisticRegression(max_iter=3000, random_state=RANDOM_STATE),
        "random_forest": RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1),
        "gradient_boosting": GradientBoostingClassifier(random_state=RANDOM_STATE),
    }


def classification_param_grids() -> dict[str, dict[str, list[Any]]]:
    return {
        "logistic_regression": {
            "model__C": [0.01, 0.1, 1, 10],
            "model__class_weight": ["balanced", None],
        },
        "random_forest": {
            "model__n_estimators": [200, 400],
            "model__max_depth": [None, 5, 10, 20],
            "model__min_samples_leaf": [1, 3, 5],
            "model__class_weight": ["balanced", "balanced_subsample"],
        },
        "gradient_boosting": {
            "model__learning_rate": [0.03, 0.05, 0.1],
            "model__n_estimators": [100, 200],
            "model__max_depth": [2, 3, 5],
        },
    }


def regression_models() -> dict[str, object]:
    return {
        "linear_regression": LinearRegression(),
        "ridge": Ridge(random_state=RANDOM_STATE),
        "random_forest": RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1),
        "gradient_boosting": GradientBoostingRegressor(random_state=RANDOM_STATE),
    }


def regression_param_grids() -> dict[str, dict[str, list[Any]]]:
    return {
        "linear_regression": {},
        "ridge": {"model__alpha": [0.01, 0.1, 1, 10, 100]},
        "random_forest": {
            "model__n_estimators": [200, 400],
            "model__max_depth": [None, 5, 10, 20],
            "model__min_samples_leaf": [1, 3, 5],
        },
        "gradient_boosting": {
            "model__learning_rate": [0.03, 0.05, 0.1],
            "model__n_estimators": [100, 200],
            "model__max_depth": [2, 3, 5],
        },
    }


def build_pipeline(X: pd.DataFrame, model: object) -> Pipeline:
    return Pipeline(
        steps=[
            ("preprocess", make_preprocessor(X)),
            ("model", model),
        ]
    )


def _get_probability_or_score(model: Pipeline, X: pd.DataFrame) -> np.ndarray | None:
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X)
        if probabilities.shape[1] > 1:
            return probabilities[:, 1]
    if hasattr(model, "decision_function"):
        return model.decision_function(X)
    return None


def _classification_metrics(
    y_true: pd.Series | np.ndarray,
    y_pred: np.ndarray,
    y_score: np.ndarray | None,
    prefix: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row = dict(prefix or {})
    row.update(
        {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0),
            "f1": f1_score(y_true, y_pred, zero_division=0),
            "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
            "roc_auc": roc_auc_score(y_true, y_score) if y_score is not None else np.nan,
            "pr_auc": average_precision_score(y_true, y_score) if y_score is not None else np.nan,
        }
    )
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    row.update({"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)})
    return row


def _flatten_cv_results(search: GridSearchCV | RandomizedSearchCV, model_name: str, search_type: str) -> pd.DataFrame:
    df = pd.DataFrame(search.cv_results_).copy()
    df.insert(0, "model", model_name)
    df.insert(1, "search_type", search_type)
    df["best_params"] = str(search.best_params_)
    return df


def _make_classification_search(model_name: str, pipeline: Pipeline, param_grid: dict[str, list[Any]], cv) -> Any:
    scoring = {
        "accuracy": "accuracy",
        "precision": "precision",
        "recall": "recall",
        "f1": "f1",
        "roc_auc": "roc_auc",
        "average_precision": "average_precision",
        "balanced_accuracy": "balanced_accuracy",
    }
    if model_name == "logistic_regression":
        return GridSearchCV(
            pipeline,
            param_grid=param_grid,
            scoring=scoring,
            refit="average_precision",
            cv=cv,
            n_jobs=-1,
            return_train_score=False,
        )
    return RandomizedSearchCV(
        pipeline,
        param_distributions=param_grid,
        n_iter=_search_iterations(param_grid, cap=16),
        scoring=scoring,
        refit="average_precision",
        cv=cv,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        return_train_score=False,
    )


def _threshold_grid_metrics(
    y_true: pd.Series,
    y_score: np.ndarray,
    model_name: str,
    thresholds: np.ndarray | None = None,
) -> pd.DataFrame:
    thresholds = thresholds if thresholds is not None else np.round(np.linspace(0.01, 0.99, 99), 2)
    rows = []
    for threshold in thresholds:
        y_pred = (y_score >= threshold).astype(int)
        rows.append(
            _classification_metrics(
                y_true,
                y_pred,
                y_score,
                prefix={"model": model_name, "threshold": float(threshold), "policy": "grid"},
            )
        )
    return pd.DataFrame(rows)


def _select_threshold_policies(threshold_grid: pd.DataFrame) -> pd.DataFrame:
    selected = []

    default_row = threshold_grid.iloc[(threshold_grid["threshold"] - 0.5).abs().argsort()[:1]].copy()
    default_row["policy"] = "default_0_50"
    selected.append(default_row)

    max_f1 = threshold_grid.sort_values(["f1", "precision"], ascending=False).head(1).copy()
    max_f1["policy"] = "max_f1"
    selected.append(max_f1)

    for recall_floor in [0.60, 0.70]:
        candidates = threshold_grid[threshold_grid["recall"] >= recall_floor].copy()
        if candidates.empty:
            best = threshold_grid.sort_values(["recall", "f1"], ascending=False).head(1).copy()
        else:
            best = candidates.sort_values(["precision", "f1"], ascending=False).head(1).copy()
        best["policy"] = f"recall_at_least_{int(recall_floor * 100)}_best_precision"
        selected.append(best)

    return pd.concat(selected, ignore_index=True)


def _threshold_for_policy(threshold_table: pd.DataFrame, policy: str) -> float:
    match = threshold_table[threshold_table["policy"] == policy]
    if match.empty:
        return float(threshold_table.sort_values("f1", ascending=False).iloc[0]["threshold"])
    return float(match.iloc[0]["threshold"])


def run_classification_experiment(df: pd.DataFrame) -> dict[str, object]:
    """Tune CPU-only classifiers, tune probability thresholds on validation data, and save outputs."""
    _ensure_results_dir()
    X, y = make_feature_target(df, task="classification")
    X_train_all, X_test, y_train_all, y_test = train_test_split(
        X,
        y,
        test_size=MODEL_TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    X_fit, X_val, y_fit, y_val = train_test_split(
        X_train_all,
        y_train_all,
        test_size=0.25,
        random_state=RANDOM_STATE,
        stratify=y_train_all,
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_tables = []
    validation_rows = []
    searches = {}

    for name, estimator in classification_models().items():
        search = _make_classification_search(name, build_pipeline(X_fit, estimator), classification_param_grids()[name], cv)
        search.fit(X_fit, y_fit)
        searches[name] = search
        search_type = "grid" if isinstance(search, GridSearchCV) else "randomized"
        cv_tables.append(_flatten_cv_results(search, name, search_type))

        y_score_val = _get_probability_or_score(search.best_estimator_, X_val)
        y_pred_val = (y_score_val >= 0.5).astype(int)
        validation_rows.append(
            _classification_metrics(
                y_val,
                y_pred_val,
                y_score_val,
                prefix={
                    "dataset": "validation",
                    "model": name,
                    "threshold_policy": "default_0_50",
                    "threshold": 0.5,
                    "best_params": str(search.best_params_),
                },
            )
        )

    cv_results = pd.concat(cv_tables, ignore_index=True)
    cv_results.to_csv(CLASSIFICATION_CV_RESULTS_PATH, index=False)

    validation_metrics = pd.DataFrame(validation_rows).sort_values(["pr_auc", "f1"], ascending=False)
    selected_model_name = str(validation_metrics.iloc[0]["model"])
    selected_search = searches[selected_model_name]
    selected_val_score = _get_probability_or_score(selected_search.best_estimator_, X_val)

    threshold_grid = _threshold_grid_metrics(y_val, selected_val_score, selected_model_name)
    selected_thresholds = _select_threshold_policies(threshold_grid)
    selected_thresholds.insert(0, "dataset", "validation")
    selected_thresholds["best_params"] = str(selected_search.best_params_)
    selected_thresholds.to_csv(CLASSIFICATION_THRESHOLD_TUNING_PATH, index=False)

    final_policy = "recall_at_least_60_best_precision"
    final_threshold = _threshold_for_policy(selected_thresholds, final_policy)
    final_model = clone(selected_search.best_estimator_)
    final_model.fit(X_train_all, y_train_all)
    test_score = _get_probability_or_score(final_model, X_test)

    test_rows = []
    for _, row in selected_thresholds.iterrows():
        threshold = float(row["threshold"])
        y_pred_test = (test_score >= threshold).astype(int)
        test_rows.append(
            _classification_metrics(
                y_test,
                y_pred_test,
                test_score,
                prefix={
                    "dataset": "test",
                    "model": selected_model_name,
                    "threshold_policy": row["policy"],
                    "threshold": threshold,
                    "best_params": str(selected_search.best_params_),
                },
            )
        )
    tuned_metrics = pd.concat([validation_metrics, pd.DataFrame(test_rows)], ignore_index=True)
    tuned_metrics.to_csv(CLASSIFICATION_TUNED_METRICS_PATH, index=False)
    tuned_metrics.to_csv(CLASSIFICATION_METRICS_PATH, index=False)

    final_pred = (test_score >= final_threshold).astype(int)
    final_cm = confusion_matrix(y_test, final_pred, labels=[0, 1])
    final_cm_df = pd.DataFrame(final_cm, index=["actual_0", "actual_1"], columns=["predicted_0", "predicted_1"])
    final_cm_df.to_csv(CLASSIFICATION_FINAL_CONFUSION_PATH)
    final_cm_df.to_csv(CLASSIFICATION_CONFUSION_PATH)

    importance = permutation_importance(
        final_model,
        X_test,
        y_test,
        n_repeats=10,
        random_state=RANDOM_STATE,
        scoring="average_precision",
        n_jobs=-1,
    )
    importance_df = (
        pd.DataFrame(
            {
                "feature": X.columns,
                "importance_mean": importance.importances_mean,
                "importance_std": importance.importances_std,
            }
        )
        .sort_values("importance_mean", ascending=False)
        .reset_index(drop=True)
    )
    importance_df.to_csv(CLASSIFICATION_FEATURE_IMPORTANCE_PATH, index=False)

    final_test_row = pd.DataFrame(test_rows)
    selected_test_row = final_test_row[final_test_row["threshold_policy"] == final_policy].iloc[0]
    summary = (
        "分类模型选择与阈值调优摘要\n"
        "==============================\n\n"
        f"候选模型: {', '.join(classification_models().keys())}\n"
        "调参方式: Logistic Regression 使用 GridSearchCV；Random Forest 和 Gradient Boosting 使用 RandomizedSearchCV；"
        "内部验证使用 StratifiedKFold(cv=5)。\n"
        f"验证集按 PR-AUC 与 F1 选择的概率模型: {selected_model_name}\n"
        f"最终阈值策略: {final_policy}, threshold={final_threshold:.2f}\n"
        f"测试集 Recall={selected_test_row['recall']:.4f}, F1={selected_test_row['f1']:.4f}, "
        f"PR-AUC={selected_test_row['pr_auc']:.4f}, ROC-AUC={selected_test_row['roc_auc']:.4f}\n\n"
        "说明: high_risk_flag 是高风险筛查任务，不能只看 Accuracy。类别不均衡时，Accuracy 可能主要反映多数类识别，"
        "而高风险样本漏判会直接降低筛查价值，因此报告中应同时关注 Recall、F1、PR-AUC 和混淆矩阵。"
        "若某模型 ROC-AUC 较高但默认阈值下 Recall 较低，不能简单称为最优筛查模型，需要结合阈值调优后的表现解释。\n"
    )
    CLASSIFICATION_MODEL_SELECTION_SUMMARY_PATH.write_text(summary, encoding="utf-8")

    return {
        "cv_results": cv_results,
        "validation_metrics": validation_metrics,
        "threshold_tuning": selected_thresholds,
        "tuned_metrics": tuned_metrics,
        "best_model_name": selected_model_name,
        "best_pipeline": final_model,
        "final_policy": final_policy,
        "final_threshold": final_threshold,
        "confusion_matrix": final_cm,
        "feature_importance": importance_df,
        "X_test": X_test,
        "y_test": y_test,
        "y_score": test_score,
        "y_pred": final_pred,
    }


def _target_slug(target_column: str) -> str:
    if target_column == REGRESSION_TARGET:
        return "productivity"
    if target_column == REGRESSION_BACKUP_TARGET:
        return "digital_dependence"
    return target_column.replace("_score", "").replace("_", "-")


def _regression_paths(target_column: str) -> dict[str, Path]:
    slug = _target_slug(target_column)
    if target_column == REGRESSION_TARGET:
        return {
            "cv": RESULTS_DIR / "regression_productivity_cv_results.csv",
            "metrics": REGRESSION_METRICS_PATH,
            "predictions": REGRESSION_PREDICTIONS_PATH,
            "importance": REGRESSION_FEATURE_IMPORTANCE_PATH,
        }
    return {
        "cv": RESULTS_DIR / f"regression_{slug}_cv_results.csv",
        "metrics": RESULTS_DIR / f"regression_{slug}_metrics.csv",
        "predictions": RESULTS_DIR / f"regression_{slug}_predictions.csv",
        "importance": RESULTS_DIR / f"regression_{slug}_permutation_importance.csv",
    }


def _make_regression_search(model_name: str, pipeline: Pipeline, param_grid: dict[str, list[Any]], cv) -> Any:
    scoring = {
        "r2": "r2",
        "neg_mse": "neg_mean_squared_error",
        "neg_mae": "neg_mean_absolute_error",
    }
    if model_name in {"linear_regression", "ridge"}:
        return GridSearchCV(
            pipeline,
            param_grid=param_grid,
            scoring=scoring,
            refit="r2",
            cv=cv,
            n_jobs=-1,
            return_train_score=False,
        )
    return RandomizedSearchCV(
        pipeline,
        param_distributions=param_grid,
        n_iter=_search_iterations(param_grid, cap=16),
        scoring=scoring,
        refit="r2",
        cv=cv,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        return_train_score=False,
    )


def _regression_metrics(
    y_true: pd.Series | np.ndarray,
    y_pred: np.ndarray,
    prefix: dict[str, Any] | None = None,
) -> dict[str, Any]:
    mse = mean_squared_error(y_true, y_pred)
    row = dict(prefix or {})
    row.update(
        {
            "mae": mean_absolute_error(y_true, y_pred),
            "mse": mse,
            "rmse": float(np.sqrt(mse)),
            "r2": r2_score(y_true, y_pred),
        }
    )
    return row


def run_regression_experiment(df: pd.DataFrame, target_column: str = REGRESSION_TARGET) -> dict[str, object]:
    """Tune CPU-only regression baselines and save target-specific metrics/results."""
    _ensure_results_dir()
    paths = _regression_paths(target_column)
    X, y = make_feature_target(df, task="regression", target_column=target_column)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=MODEL_TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_tables = []
    metric_rows = []
    trained = {}

    for name, estimator in regression_models().items():
        search = _make_regression_search(name, build_pipeline(X_train, estimator), regression_param_grids()[name], cv)
        search.fit(X_train, y_train)
        search_type = "grid" if isinstance(search, GridSearchCV) else "randomized"
        cv_tables.append(_flatten_cv_results(search, name, search_type))

        y_pred = search.best_estimator_.predict(X_test)
        cv_best = pd.DataFrame(search.cv_results_).iloc[search.best_index_]
        metric_rows.append(
            _regression_metrics(
                y_test,
                y_pred,
                prefix={
                    "model": name,
                    "target": target_column,
                    "cv_best_r2": cv_best.get("mean_test_r2", np.nan),
                    "cv_best_mse": -cv_best.get("mean_test_neg_mse", np.nan),
                    "cv_best_mae": -cv_best.get("mean_test_neg_mae", np.nan),
                    "n_train": len(X_train),
                    "n_test": len(X_test),
                    "feature_count": X.shape[1],
                    "best_params": str(search.best_params_),
                },
            )
        )
        trained[name] = {"pipeline": search.best_estimator_, "y_pred": y_pred, "cv_r2": cv_best.get("mean_test_r2", np.nan)}

    cv_results = pd.concat(cv_tables, ignore_index=True)
    cv_results.to_csv(paths["cv"], index=False)

    metrics = pd.DataFrame(metric_rows).sort_values(["cv_best_r2", "r2"], ascending=False).reset_index(drop=True)
    metrics.to_csv(paths["metrics"], index=False)

    best_name = str(metrics.loc[0, "model"])
    best = trained[best_name]
    predictions = pd.DataFrame(
        {
            "actual": y_test.values,
            "predicted": best["y_pred"],
            "residual": y_test.values - best["y_pred"],
            "model": best_name,
            "target": target_column,
        },
        index=y_test.index,
    )
    predictions.index.name = "row_index"
    predictions.to_csv(paths["predictions"])

    importance = permutation_importance(
        best["pipeline"],
        X_test,
        y_test,
        n_repeats=10,
        random_state=RANDOM_STATE,
        scoring="r2",
        n_jobs=-1,
    )
    importance_df = (
        pd.DataFrame(
            {
                "feature": X.columns,
                "importance_mean": importance.importances_mean,
                "importance_std": importance.importances_std,
            }
        )
        .sort_values("importance_mean", ascending=False)
        .reset_index(drop=True)
    )
    importance_df.to_csv(paths["importance"], index=False)

    return {
        "cv_results": cv_results,
        "metrics": metrics,
        "best_model_name": best_name,
        "best_pipeline": best["pipeline"],
        "feature_importance": importance_df,
        "X_test": X_test,
        "y_test": y_test,
        "y_pred": best["y_pred"],
        "predictions": predictions,
        "paths": paths,
    }


def run_regression_suite(df: pd.DataFrame) -> dict[str, object]:
    """Run both requested regression targets and save comparison/summary files."""
    productivity = run_regression_experiment(df, target_column=REGRESSION_TARGET)
    digital_dependence = run_regression_experiment(df, target_column=REGRESSION_BACKUP_TARGET)

    best_rows = []
    for result in [productivity, digital_dependence]:
        best = result["metrics"].iloc[0].copy()
        best_rows.append(best)
    comparison = pd.DataFrame(best_rows).reset_index(drop=True)
    comparison.to_csv(REGRESSION_TARGET_COMPARISON_PATH, index=False)

    productivity_best = productivity["metrics"].iloc[0]
    dependence_best = digital_dependence["metrics"].iloc[0]
    weak_productivity = float(productivity_best["r2"]) <= 0.05
    better_dependence = float(dependence_best["r2"]) > float(productivity_best["r2"])
    summary = (
        "回归模型选择摘要\n"
        "================\n\n"
        f"productivity_score 最佳模型: {productivity_best['model']}, "
        f"R2={productivity_best['r2']:.4f}, MSE={productivity_best['mse']:.4f}, "
        f"RMSE={productivity_best['rmse']:.4f}, MAE={productivity_best['mae']:.4f}\n"
        f"digital_dependence_score 最佳模型: {dependence_best['model']}, "
        f"R2={dependence_best['r2']:.4f}, MSE={dependence_best['mse']:.4f}, "
        f"RMSE={dependence_best['rmse']:.4f}, MAE={dependence_best['mae']:.4f}\n\n"
    )
    if weak_productivity:
        summary += (
            "productivity_score 说明: 在当前可观测行为与生活习惯特征下，productivity_score 的可预测性较弱，"
            "不能据此得出强预测结论。\n"
        )
    if better_dependence:
        summary += (
            "digital_dependence_score 说明: 该目标相对更贴近设备使用、通知、解锁和社交媒体变量，"
            "若指标明显优于 productivity_score，正式报告可考虑将回归主线调整为数字依赖程度预测。\n"
        )
    REGRESSION_MODEL_SELECTION_SUMMARY_PATH.write_text(summary, encoding="utf-8")

    return {
        "productivity": productivity,
        "digital_dependence": digital_dependence,
        "comparison": comparison,
    }


def _cluster_preprocessor() -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )


def _cluster_scores(algorithm: str, k: int, labels: np.ndarray, X_processed: np.ndarray, inertia: float | None = None) -> dict:
    unique_labels = np.unique(labels)
    if len(unique_labels) < 2:
        return {
            "algorithm": algorithm,
            "k": k,
            "inertia": inertia,
            "silhouette": np.nan,
            "calinski_harabasz": np.nan,
            "davies_bouldin": np.nan,
        }
    return {
        "algorithm": algorithm,
        "k": k,
        "inertia": inertia,
        "silhouette": silhouette_score(X_processed, labels),
        "calinski_harabasz": calinski_harabasz_score(X_processed, labels),
        "davies_bouldin": davies_bouldin_score(X_processed, labels),
    }


def _suggest_cluster_labels(profile: pd.DataFrame) -> pd.Series:
    labels = {}
    max_social_cluster = profile.sort_values("social_media_mins", ascending=False).iloc[0]["cluster"]
    max_dependence_cluster = profile.sort_values("digital_dependence_score", ascending=False).iloc[0]["cluster"]
    min_risk_cluster = profile.sort_values(["high_risk_flag", "device_hours_per_day"]).iloc[0]["cluster"]
    for _, row in profile.iterrows():
        cluster = row["cluster"]
        if cluster == max_dependence_cluster:
            labels[cluster] = "high_device_dependence_profile"
        elif cluster == max_social_cluster:
            labels[cluster] = "high_social_media_profile"
        elif cluster == min_risk_cluster:
            labels[cluster] = "balanced_low_load_profile"
        else:
            labels[cluster] = "mixed_lifestyle_profile"
    return profile["cluster"].map(labels)


def _cluster_profile(df: pd.DataFrame, labels: np.ndarray, algorithm: str) -> pd.DataFrame:
    data = add_behavior_features(df).copy()
    data["cluster"] = labels
    data["cluster_algorithm"] = algorithm
    profile_columns = [
        "device_hours_per_day",
        "phone_unlocks",
        "notifications_per_day",
        "social_media_mins",
        "study_mins",
        "physical_activity_days",
        "sleep_hours",
        "sleep_quality",
        "social_media_hours",
        "study_hours",
        "notifications_per_device_hour",
        "unlocks_per_device_hour",
        "device_to_sleep_ratio",
        "activity_sleep_interaction",
        "social_to_study_ratio",
        "high_risk_flag",
        "productivity_score",
        "digital_dependence_score",
        "anxiety_score",
        "depression_score",
        "stress_level",
        "happiness_score",
        "focus_score",
    ]
    numeric_columns = [column for column in profile_columns if column in data.columns]
    profile = data.groupby("cluster")[numeric_columns].mean().reset_index()
    sizes = data.groupby("cluster").size().rename("cluster_size").reset_index()
    profile = sizes.merge(profile, on="cluster", how="left")
    profile.insert(1, "cluster_algorithm", algorithm)

    categorical_columns = [column for column in CLUSTER_PROFILE_CONTEXT_COLUMNS if column in data.columns]
    for column in categorical_columns:
        modes = data.groupby("cluster")[column].agg(lambda x: x.mode().iloc[0] if not x.mode().empty else "")
        profile[f"{column}_mode"] = profile["cluster"].map(modes)

    profile["suggested_cluster_label"] = _suggest_cluster_labels(profile)
    return profile


def run_clustering_experiment(df: pd.DataFrame, k_values: range = range(2, 9)) -> dict[str, object]:
    """Compare clustering algorithms using only behavior/lifestyle numeric features."""
    _ensure_results_dir()
    X, _ = make_feature_target(df, task="clustering")
    preprocessor = _cluster_preprocessor()
    X_processed = preprocessor.fit_transform(X)

    score_rows = []
    fitted_labels: dict[tuple[str, int], np.ndarray] = {}
    fitted_models: dict[tuple[str, int], object] = {}

    for k in k_values:
        kmeans = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=20)
        kmeans_labels = kmeans.fit_predict(X_processed)
        score_rows.append(_cluster_scores("kmeans", k, kmeans_labels, X_processed, inertia=kmeans.inertia_))
        fitted_labels[("kmeans", k)] = kmeans_labels
        fitted_models[("kmeans", k)] = kmeans

        agg = AgglomerativeClustering(n_clusters=k)
        agg_labels = agg.fit_predict(X_processed)
        score_rows.append(_cluster_scores("agglomerative", k, agg_labels, X_processed))
        fitted_labels[("agglomerative", k)] = agg_labels
        fitted_models[("agglomerative", k)] = agg

        gmm = GaussianMixture(n_components=k, random_state=RANDOM_STATE, covariance_type="full")
        gmm_labels = gmm.fit_predict(X_processed)
        score_rows.append(_cluster_scores("gaussian_mixture", k, gmm_labels, X_processed))
        fitted_labels[("gaussian_mixture", k)] = gmm_labels
        fitted_models[("gaussian_mixture", k)] = gmm

    comparison = pd.DataFrame(score_rows).sort_values(["algorithm", "k"]).reset_index(drop=True)
    comparison.to_csv(CLUSTERING_MODEL_COMPARISON_PATH, index=False)
    kmeans_scores = comparison[comparison["algorithm"] == "kmeans"].drop(columns=["algorithm"]).reset_index(drop=True)
    kmeans_scores.to_csv(CLUSTERING_SCORES_PATH, index=False)

    best_row = comparison.dropna(subset=["silhouette"]).sort_values("silhouette", ascending=False).iloc[0]
    best_algorithm = str(best_row["algorithm"])
    best_k = int(best_row["k"])
    labels = fitted_labels[(best_algorithm, best_k)]

    assignments = pd.DataFrame(
        {
            "row_index": df.index,
            "cluster_algorithm": best_algorithm,
            "k": best_k,
            "cluster": labels,
        }
    )
    if "id" in df.columns:
        assignments.insert(0, "id", df["id"].values)
    assignments.to_csv(CLUSTERING_ASSIGNMENTS_PATH, index=False)

    profile = _cluster_profile(df, labels, best_algorithm)
    profile.to_csv(CLUSTERING_PROFILE_PATH, index=False)

    compact_columns = [
        "cluster",
        "cluster_algorithm",
        "cluster_size",
        "device_hours_per_day",
        "social_media_mins",
        "sleep_hours",
        "sleep_quality",
        "high_risk_flag",
        "productivity_score",
        "digital_dependence_score",
        "suggested_cluster_label",
    ]
    profile[[column for column in compact_columns if column in profile.columns]].to_csv(
        RESULTS_DIR / "clustering_lifestyle_profiles_compact.csv",
        index=False,
    )

    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    coords = pca.fit_transform(X_processed)
    coords_df = pd.DataFrame(
        {
            "pc1": coords[:, 0],
            "pc2": coords[:, 1],
            "cluster_algorithm": best_algorithm,
            "k": best_k,
            "cluster": labels,
        }
    )
    if "id" in df.columns:
        coords_df.insert(0, "id", df["id"].values)
    coords_df.to_csv(CLUSTERING_PCA_PATH, index=False)

    best_silhouette = float(best_row["silhouette"])
    interpretation = (
        "聚类画像解释摘要\n"
        "================\n\n"
        f"聚类输入特征数: {X.shape[1]}\n"
        f"聚类输入字段: {', '.join(X.columns)}\n"
        "未用于聚类训练的背景/结果字段包括 id、gender、region、income_level、education_level、daily_role、device_type "
        "以及 anxiety_score、depression_score、stress_level、happiness_score、focus_score、high_risk_flag、"
        "productivity_score、digital_dependence_score。\n"
        f"按 Silhouette 选择的探索性画像模型: {best_algorithm}, k={best_k}, silhouette={best_silhouette:.4f}\n"
    )
    if best_silhouette < 0.20:
        interpretation += "Silhouette 较低，聚类结构较弱，因此聚类结果主要用于探索性画像，不作为严格人群边界。\n"
    interpretation += "\n建议簇名称见 results/clustering_lifestyle_profiles_compact.csv。\n"
    CLUSTERING_PROFILE_INTERPRETATION_PATH.write_text(interpretation, encoding="utf-8")

    return {
        "scores": kmeans_scores,
        "model_comparison": comparison,
        "best_algorithm": best_algorithm,
        "best_k": best_k,
        "labels": labels,
        "assignments": assignments,
        "profile": profile,
        "pca_coordinates": coords_df,
        "preprocessor": preprocessor,
        "model": fitted_models[(best_algorithm, best_k)],
        "X_cluster": X,
        "X_processed": X_processed,
    }
