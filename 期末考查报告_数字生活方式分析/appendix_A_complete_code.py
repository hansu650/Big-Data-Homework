"""Complete runnable code source for Appendix A.

Run from the repository root:
    python 期末考查报告_数字生活方式分析/appendix_A_complete_code.py

This file rebuilds the final report evidence files without changing the
validated core CSV metrics. It loads the raw dataset, checks data quality,
creates engineered features, documents leakage control, regenerates the final
figures, exports screenshot Excel tables, and summarizes the validated results.
"""

from __future__ import annotations

import runpy
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "digital_lifestyle_benchmark_2025.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "digital_lifestyle_benchmark_2025_processed.csv"
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURE_DIR = PROJECT_ROOT / "figures" / "final_report"
SCREENSHOT_TABLE_DIR = PROJECT_ROOT / "screenshot_tables"
RANDOM_STATE = 42


def load_raw_data() -> pd.DataFrame:
    df = pd.read_csv(RAW_DATA_PATH)
    print("Raw dataset shape:", df.shape)
    print("Raw columns:", df.columns.tolist())
    print(df.head())
    return df


def check_missing_duplicates_and_ranges(df: pd.DataFrame) -> None:
    key_numeric = [
        "age",
        "device_hours_per_day",
        "phone_unlocks",
        "notifications_per_day",
        "social_media_mins",
        "study_mins",
        "sleep_hours",
        "sleep_quality",
        "productivity_score",
        "digital_dependence_score",
    ]
    print("\nMissing values:")
    print(df.isna().sum())
    print("\nDuplicate rows:", df.duplicated().sum())
    print("Duplicate id:", df["id"].duplicated().sum())
    print("\nRange summary:")
    print(df[key_numeric].agg(["min", "max", "mean"]).T)


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    engineered = df.copy()
    eps = 1e-6
    engineered["social_media_hours"] = engineered["social_media_mins"] / 60
    engineered["study_hours"] = engineered["study_mins"] / 60
    engineered["notifications_per_device_hour"] = (
        engineered["notifications_per_day"] / engineered["device_hours_per_day"].clip(lower=eps)
    )
    engineered["unlocks_per_device_hour"] = (
        engineered["phone_unlocks"] / engineered["device_hours_per_day"].clip(lower=eps)
    )
    engineered["device_to_sleep_ratio"] = (
        engineered["device_hours_per_day"] / engineered["sleep_hours"].clip(lower=eps)
    )
    engineered["activity_sleep_interaction"] = (
        engineered["physical_activity_days"] * engineered["sleep_hours"]
    )
    engineered["social_to_study_ratio"] = engineered["social_media_mins"] / (
        engineered["study_mins"] + 1
    )
    engineered.to_csv(PROCESSED_DATA_PATH, index=False)
    print("\nProcessed dataset saved:", PROCESSED_DATA_PATH)
    return engineered


def define_feature_sets(engineered: pd.DataFrame) -> dict[str, list[str]]:
    classification_drop = [
        "id",
        "high_risk_flag",
        "anxiety_score",
        "depression_score",
        "stress_level",
        "happiness_score",
        "focus_score",
        "productivity_score",
        "digital_dependence_score",
    ]
    regression_drop = [
        "id",
        "digital_dependence_score",
        "high_risk_flag",
        "anxiety_score",
        "depression_score",
        "stress_level",
        "happiness_score",
        "focus_score",
        "productivity_score",
    ]
    clustering_features = [
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
    ]
    classification_features = [c for c in engineered.columns if c not in classification_drop]
    regression_features = [c for c in engineered.columns if c not in regression_drop]
    print("\nClassification drop columns:", classification_drop)
    print("Classification feature count:", len(classification_features))
    print("Regression feature count:", len(regression_features))
    print("Clustering features:", clustering_features)
    return {
        "classification_drop": classification_drop,
        "classification_features": classification_features,
        "regression_drop": regression_drop,
        "regression_features": regression_features,
        "clustering_features": clustering_features,
    }


def summarize_validated_results() -> None:
    classification = pd.read_csv(RESULTS_DIR / "classification_tuned_metrics.csv")
    regression_dd = pd.read_csv(RESULTS_DIR / "regression_digital_dependence_metrics.csv")
    regression_prod = pd.read_csv(RESULTS_DIR / "regression_productivity_metrics.csv")
    clustering = pd.read_csv(RESULTS_DIR / "clustering_kmeans_scores.csv")

    final_cls = classification[
        (classification["dataset"] == "test")
        & (classification["model"] == "gradient_boosting")
        & (classification["threshold"].round(2) == 0.14)
    ].iloc[0]
    final_dd = regression_dd[regression_dd["model"] == "gradient_boosting"].iloc[0]
    final_prod = regression_prod[regression_prod["model"] == "gradient_boosting"].iloc[0]
    final_cluster = clustering[clustering["k"] == 3].iloc[0]

    summary = pd.DataFrame(
        [
            {
                "task": "classification_high_risk",
                "main_result": "Gradient Boosting threshold=0.14",
                "metric_1": f"Recall={final_cls['recall']:.4f}",
                "metric_2": f"F1={final_cls['f1']:.4f}",
                "metric_3": f"PR-AUC={final_cls['pr_auc']:.4f}",
            },
            {
                "task": "regression_digital_dependence",
                "main_result": "Gradient Boosting",
                "metric_1": f"R2={final_dd['r2']:.4f}",
                "metric_2": f"MSE={final_dd['mse']:.4f}",
                "metric_3": f"MAE={final_dd['mae']:.4f}",
            },
            {
                "task": "regression_productivity",
                "main_result": "weak prediction / negative result",
                "metric_1": f"R2={final_prod['r2']:.4f}",
                "metric_2": "",
                "metric_3": "",
            },
            {
                "task": "clustering_lifestyle_profiles",
                "main_result": "KMeans k=3",
                "metric_1": f"Silhouette={final_cluster['silhouette']:.4f}",
                "metric_2": "",
                "metric_3": "",
            },
        ]
    )
    output = RESULTS_DIR / "final_workflow_report_summary.csv"
    summary.to_csv(output, index=False)
    print("\nValidated result summary saved:", output)


def regenerate_figures_and_screenshot_tables() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    runpy.run_path(str(PROJECT_ROOT / "scripts" / "generate_final_report_figures.py"), run_name="__main__")
    runpy.run_path(str(PROJECT_ROOT / "scripts" / "export_screenshot_tables.py"), run_name="__main__")


def main() -> None:
    print("Random state:", RANDOM_STATE)
    df = load_raw_data()
    check_missing_duplicates_and_ranges(df)
    engineered = add_engineered_features(df)
    define_feature_sets(engineered)
    summarize_validated_results()
    regenerate_figures_and_screenshot_tables()
    print("\nComplete workflow evidence generation finished.")


if __name__ == "__main__":
    main()

