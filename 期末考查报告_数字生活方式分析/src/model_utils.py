from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
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
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

try:
    from .config import (
        CLASSIFICATION_CONFUSION_PATH,
        CLASSIFICATION_FEATURE_IMPORTANCE_PATH,
        CLASSIFICATION_METRICS_PATH,
        CLASSIFICATION_TARGET,
        CLUSTERING_ASSIGNMENTS_PATH,
        CLUSTERING_PCA_PATH,
        CLUSTERING_PROFILE_PATH,
        CLUSTERING_SCORES_PATH,
        MODEL_TEST_SIZE,
        RANDOM_STATE,
        REGRESSION_FEATURE_IMPORTANCE_PATH,
        REGRESSION_METRICS_PATH,
        REGRESSION_PREDICTIONS_PATH,
        REGRESSION_TARGET,
    )
    from .feature_engineering import add_behavior_features, make_feature_target, make_preprocessor
except ImportError:
    from config import (
        CLASSIFICATION_CONFUSION_PATH,
        CLASSIFICATION_FEATURE_IMPORTANCE_PATH,
        CLASSIFICATION_METRICS_PATH,
        CLASSIFICATION_TARGET,
        CLUSTERING_ASSIGNMENTS_PATH,
        CLUSTERING_PCA_PATH,
        CLUSTERING_PROFILE_PATH,
        CLUSTERING_SCORES_PATH,
        MODEL_TEST_SIZE,
        RANDOM_STATE,
        REGRESSION_FEATURE_IMPORTANCE_PATH,
        REGRESSION_METRICS_PATH,
        REGRESSION_PREDICTIONS_PATH,
        REGRESSION_TARGET,
    )
    from feature_engineering import add_behavior_features, make_feature_target, make_preprocessor


def classification_models() -> dict[str, object]:
    return {
        "logistic_regression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingClassifier(random_state=RANDOM_STATE),
    }


def regression_models() -> dict[str, object]:
    return {
        "linear_regression": LinearRegression(),
        "ridge": Ridge(alpha=1.0, random_state=RANDOM_STATE),
        "random_forest": RandomForestRegressor(
            n_estimators=300,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingRegressor(random_state=RANDOM_STATE),
    }


def build_pipeline(X: pd.DataFrame, model: object) -> Pipeline:
    return Pipeline(
        steps=[
            ("preprocess", make_preprocessor(X)),
            ("model", model),
        ]
    )


def _safe_roc_auc(y_true: pd.Series, y_score: np.ndarray | None) -> float:
    if y_score is None:
        return np.nan
    try:
        return float(roc_auc_score(y_true, y_score))
    except ValueError:
        return np.nan


def _get_probability_or_score(model: Pipeline, X: pd.DataFrame) -> np.ndarray | None:
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X)
        if probabilities.shape[1] > 1:
            return probabilities[:, 1]
    if hasattr(model, "decision_function"):
        return model.decision_function(X)
    return None


def run_classification_experiment(df: pd.DataFrame) -> dict[str, object]:
    """Train CPU-only classification baselines and save metrics/results."""
    X, y = make_feature_target(df, task="classification")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=MODEL_TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    rows = []
    trained = {}
    for name, estimator in classification_models().items():
        pipeline = build_pipeline(X_train, estimator)
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_score = _get_probability_or_score(pipeline, X_test)
        rows.append(
            {
                "model": name,
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, zero_division=0),
                "recall": recall_score(y_test, y_pred, zero_division=0),
                "f1": f1_score(y_test, y_pred, zero_division=0),
                "roc_auc": _safe_roc_auc(y_test, y_score),
                "n_train": len(X_train),
                "n_test": len(X_test),
                "feature_count": X.shape[1],
            }
        )
        trained[name] = {"pipeline": pipeline, "y_pred": y_pred, "y_score": y_score}

    metrics = pd.DataFrame(rows).sort_values(["roc_auc", "f1"], ascending=False).reset_index(drop=True)
    CLASSIFICATION_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(CLASSIFICATION_METRICS_PATH, index=False)

    best_name = metrics.loc[0, "model"]
    best = trained[best_name]
    cm = confusion_matrix(y_test, best["y_pred"])
    pd.DataFrame(cm, index=["actual_0", "actual_1"], columns=["predicted_0", "predicted_1"]).to_csv(
        CLASSIFICATION_CONFUSION_PATH
    )

    importance = permutation_importance(
        best["pipeline"],
        X_test,
        y_test,
        n_repeats=10,
        random_state=RANDOM_STATE,
        scoring="roc_auc",
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

    return {
        "metrics": metrics,
        "best_model_name": best_name,
        "best_pipeline": best["pipeline"],
        "confusion_matrix": cm,
        "feature_importance": importance_df,
        "X_test": X_test,
        "y_test": y_test,
        "y_score": best["y_score"],
        "y_pred": best["y_pred"],
    }


def run_regression_experiment(df: pd.DataFrame, target_column: str = REGRESSION_TARGET) -> dict[str, object]:
    """Train CPU-only regression baselines and save metrics/results."""
    X, y = make_feature_target(df, task="regression", target_column=target_column)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=MODEL_TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    rows = []
    trained = {}
    for name, estimator in regression_models().items():
        pipeline = build_pipeline(X_train, estimator)
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        rows.append(
            {
                "model": name,
                "mae": mean_absolute_error(y_test, y_pred),
                "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
                "r2": r2_score(y_test, y_pred),
                "n_train": len(X_train),
                "n_test": len(X_test),
                "feature_count": X.shape[1],
                "target": target_column,
            }
        )
        trained[name] = {"pipeline": pipeline, "y_pred": y_pred}

    metrics = pd.DataFrame(rows).sort_values(["r2", "rmse"], ascending=[False, True]).reset_index(drop=True)
    REGRESSION_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(REGRESSION_METRICS_PATH, index=False)

    best_name = metrics.loc[0, "model"]
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
    predictions.to_csv(REGRESSION_PREDICTIONS_PATH)

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
    importance_df.to_csv(REGRESSION_FEATURE_IMPORTANCE_PATH, index=False)

    return {
        "metrics": metrics,
        "best_model_name": best_name,
        "best_pipeline": best["pipeline"],
        "feature_importance": importance_df,
        "X_test": X_test,
        "y_test": y_test,
        "y_pred": best["y_pred"],
        "predictions": predictions,
    }


def _cluster_profile(df: pd.DataFrame, labels: np.ndarray) -> pd.DataFrame:
    data = add_behavior_features(df).copy()
    data["cluster"] = labels
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

    categorical_columns = [
        column
        for column in ["gender", "region", "income_level", "education_level", "daily_role", "device_type"]
        if column in data.columns
    ]
    for column in categorical_columns:
        modes = data.groupby("cluster")[column].agg(lambda x: x.mode().iloc[0] if not x.mode().empty else "")
        profile[f"{column}_mode"] = profile["cluster"].map(modes)
    return profile


def run_clustering_experiment(df: pd.DataFrame, k_values: range = range(2, 7)) -> dict[str, object]:
    """Fit KMeans profiles using behavior/lifestyle features only."""
    X, _ = make_feature_target(df, task="clustering")
    preprocessor = make_preprocessor(X)
    X_processed = preprocessor.fit_transform(X)

    score_rows = []
    models = {}
    for k in k_values:
        model = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=20)
        labels = model.fit_predict(X_processed)
        score_rows.append(
            {
                "k": k,
                "inertia": model.inertia_,
                "silhouette": silhouette_score(X_processed, labels),
                "calinski_harabasz": calinski_harabasz_score(X_processed, labels),
                "davies_bouldin": davies_bouldin_score(X_processed, labels),
            }
        )
        models[k] = {"model": model, "labels": labels}

    scores = pd.DataFrame(score_rows).sort_values("k").reset_index(drop=True)
    scores.to_csv(CLUSTERING_SCORES_PATH, index=False)
    best_k = int(scores.sort_values("silhouette", ascending=False).iloc[0]["k"])
    labels = models[best_k]["labels"]

    assignments = pd.DataFrame(
        {
            "row_index": df.index,
            "cluster": labels,
        }
    )
    if "id" in df.columns:
        assignments.insert(0, "id", df["id"].values)
    assignments.to_csv(CLUSTERING_ASSIGNMENTS_PATH, index=False)

    profile = _cluster_profile(df, labels)
    profile.to_csv(CLUSTERING_PROFILE_PATH, index=False)

    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    coords = pca.fit_transform(X_processed)
    coords_df = pd.DataFrame(
        {
            "pc1": coords[:, 0],
            "pc2": coords[:, 1],
            "cluster": labels,
        }
    )
    if "id" in df.columns:
        coords_df.insert(0, "id", df["id"].values)
    coords_df.to_csv(CLUSTERING_PCA_PATH, index=False)

    return {
        "scores": scores,
        "best_k": best_k,
        "labels": labels,
        "assignments": assignments,
        "profile": profile,
        "pca_coordinates": coords_df,
        "preprocessor": preprocessor,
        "model": models[best_k]["model"],
    }

