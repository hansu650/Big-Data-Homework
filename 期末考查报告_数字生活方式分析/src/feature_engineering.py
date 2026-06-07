from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

try:
    from .config import (
        CLASSIFICATION_TARGET,
        CLUSTERING_INPUT_COLUMNS,
        HIGH_RISK_LEAKAGE_COLUMNS,
        ID_COLUMNS,
        OUTCOME_COLUMNS,
        REGRESSION_BACKUP_TARGET,
        REGRESSION_TARGET,
    )
except ImportError:
    from config import (
        CLASSIFICATION_TARGET,
        CLUSTERING_INPUT_COLUMNS,
        HIGH_RISK_LEAKAGE_COLUMNS,
        ID_COLUMNS,
        OUTCOME_COLUMNS,
        REGRESSION_BACKUP_TARGET,
        REGRESSION_TARGET,
    )


def add_behavior_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived features that only use digital behavior and lifestyle inputs."""
    out = df.copy()
    eps = 1e-6

    if {"social_media_mins"}.issubset(out.columns):
        out["social_media_hours"] = out["social_media_mins"] / 60.0
    if {"study_mins"}.issubset(out.columns):
        out["study_hours"] = out["study_mins"] / 60.0
    if {"notifications_per_day", "device_hours_per_day"}.issubset(out.columns):
        out["notifications_per_device_hour"] = out["notifications_per_day"] / (
            out["device_hours_per_day"].clip(lower=eps)
        )
    if {"phone_unlocks", "device_hours_per_day"}.issubset(out.columns):
        out["unlocks_per_device_hour"] = out["phone_unlocks"] / out["device_hours_per_day"].clip(lower=eps)
    if {"device_hours_per_day", "sleep_hours"}.issubset(out.columns):
        out["device_to_sleep_ratio"] = out["device_hours_per_day"] / out["sleep_hours"].clip(lower=eps)
    if {"physical_activity_days", "sleep_hours"}.issubset(out.columns):
        out["activity_sleep_interaction"] = out["physical_activity_days"] * out["sleep_hours"]
    if {"social_media_mins", "study_mins"}.issubset(out.columns):
        out["social_to_study_ratio"] = out["social_media_mins"] / (out["study_mins"] + 1.0)

    return out


def columns_present(df: pd.DataFrame, columns: list[str]) -> list[str]:
    return [column for column in columns if column in df.columns]


def get_excluded_columns(task: str, target_column: Optional[str] = None) -> list[str]:
    """Return columns excluded from feature matrices for each task."""
    task = task.lower()
    excluded = set(ID_COLUMNS)

    if task == "classification":
        excluded.add(CLASSIFICATION_TARGET)
        excluded.update(HIGH_RISK_LEAKAGE_COLUMNS)
    elif task == "regression":
        target = target_column or REGRESSION_TARGET
        excluded.add(target)
        excluded.update(OUTCOME_COLUMNS)
        if target == REGRESSION_TARGET:
            excluded.add(REGRESSION_BACKUP_TARGET)
        elif target == REGRESSION_BACKUP_TARGET:
            excluded.add(REGRESSION_TARGET)
    elif task == "clustering":
        excluded.update(OUTCOME_COLUMNS)
    else:
        raise ValueError(f"Unknown task: {task}")

    return sorted(excluded)


def get_clustering_feature_columns(df: pd.DataFrame) -> list[str]:
    """Return the explicit behavior/lifestyle feature whitelist for clustering."""
    return columns_present(df, CLUSTERING_INPUT_COLUMNS)


def make_feature_target(
    df: pd.DataFrame,
    task: str,
    target_column: Optional[str] = None,
    add_features: bool = True,
) -> tuple[pd.DataFrame, Optional[pd.Series]]:
    """Build a leakage-aware feature matrix and optional target series."""
    data = add_behavior_features(df) if add_features else df.copy()
    task = task.lower()

    if task == "classification":
        target = CLASSIFICATION_TARGET
    elif task == "regression":
        target = target_column or REGRESSION_TARGET
    elif task == "clustering":
        target = None
    else:
        raise ValueError(f"Unknown task: {task}")

    if task == "clustering":
        clustering_columns = get_clustering_feature_columns(data)
        if not clustering_columns:
            raise ValueError("No clustering input columns are present in the dataframe.")
        X = data[clustering_columns].copy()
    else:
        excluded = columns_present(data, get_excluded_columns(task, target))
        X = data.drop(columns=excluded)
    y = data[target].copy() if target is not None else None
    return X, y


def detect_feature_types(X: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Split feature columns into numeric and categorical columns."""
    numeric_columns = X.select_dtypes(include=[np.number, "bool"]).columns.tolist()
    categorical_columns = [column for column in X.columns if column not in numeric_columns]
    return numeric_columns, categorical_columns


def make_one_hot_encoder() -> OneHotEncoder:
    """Create an encoder compatible with older and newer scikit-learn versions."""
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def make_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    """Create a preprocessing transformer for numeric and categorical features."""
    numeric_columns, categorical_columns = detect_feature_types(X)

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", make_one_hot_encoder()),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_columns),
            ("categorical", categorical_pipeline, categorical_columns),
        ],
        remainder="drop",
        verbose_feature_names_out=True,
    )
