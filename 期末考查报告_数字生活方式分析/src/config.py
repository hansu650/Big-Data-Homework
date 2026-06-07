from pathlib import Path

RANDOM_STATE = 42

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
FIGURES_DIR = PROJECT_ROOT / "figures"
RESULTS_DIR = PROJECT_ROOT / "results"
REPORT_DIR = PROJECT_ROOT / "report"
REPORT_TABLES_DIR = REPORT_DIR / "tables"

DATASET_NAME = "2025 Digital Lifestyle Benchmark Dataset"
DATASET_PAGE_URL = "https://huggingface.co/datasets/tarekmasryo/digital-lifestyle-benchmark-dataset"
DATASET_URL = (
    "https://huggingface.co/datasets/tarekmasryo/"
    "digital-lifestyle-benchmark-dataset/resolve/main/data/"
    "digital_lifestyle_benchmark_2025.csv"
)
RAW_DATA_PATH = RAW_DATA_DIR / "digital_lifestyle_benchmark_2025.csv"
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "digital_lifestyle_benchmark_2025_processed.csv"

CLASSIFICATION_TARGET = "high_risk_flag"
REGRESSION_TARGET = "productivity_score"
REGRESSION_BACKUP_TARGET = "digital_dependence_score"

ID_COLUMNS = ["id"]

HIGH_RISK_LEAKAGE_COLUMNS = [
    "anxiety_score",
    "depression_score",
    "stress_level",
    "happiness_score",
    "focus_score",
    "productivity_score",
    "digital_dependence_score",
]

OUTCOME_COLUMNS = [
    "anxiety_score",
    "depression_score",
    "stress_level",
    "happiness_score",
    "focus_score",
    "high_risk_flag",
    "productivity_score",
    "digital_dependence_score",
]

REQUIRED_COLUMNS = [
    "id",
    "age",
    "gender",
    "region",
    "income_level",
    "education_level",
    "daily_role",
    "device_hours_per_day",
    "phone_unlocks",
    "notifications_per_day",
    "social_media_mins",
    "study_mins",
    "physical_activity_days",
    "sleep_hours",
    "sleep_quality",
    "anxiety_score",
    "depression_score",
    "stress_level",
    "happiness_score",
    "focus_score",
    "high_risk_flag",
    "device_type",
    "productivity_score",
    "digital_dependence_score",
]

BEHAVIOR_LIFESTYLE_COLUMNS = [
    "age",
    "gender",
    "region",
    "income_level",
    "education_level",
    "daily_role",
    "device_hours_per_day",
    "phone_unlocks",
    "notifications_per_day",
    "social_media_mins",
    "study_mins",
    "physical_activity_days",
    "sleep_hours",
    "sleep_quality",
    "device_type",
]

CLUSTERING_INPUT_COLUMNS = [
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

CLUSTER_PROFILE_CONTEXT_COLUMNS = [
    "gender",
    "region",
    "income_level",
    "education_level",
    "daily_role",
    "device_type",
]

MODEL_TEST_SIZE = 0.25
CV_SPLITS = 5
DEFAULT_FIGURE_DPI = 160

CLASSIFICATION_METRICS_PATH = RESULTS_DIR / "classification_high_risk_metrics.csv"
CLASSIFICATION_CONFUSION_PATH = RESULTS_DIR / "classification_best_confusion_matrix.csv"
CLASSIFICATION_FEATURE_IMPORTANCE_PATH = RESULTS_DIR / "classification_permutation_importance.csv"
CLASSIFICATION_CV_RESULTS_PATH = RESULTS_DIR / "classification_cv_results.csv"
CLASSIFICATION_TUNED_METRICS_PATH = RESULTS_DIR / "classification_tuned_metrics.csv"
CLASSIFICATION_THRESHOLD_TUNING_PATH = RESULTS_DIR / "classification_threshold_tuning.csv"
CLASSIFICATION_FINAL_CONFUSION_PATH = RESULTS_DIR / "classification_final_confusion_matrix.csv"
CLASSIFICATION_MODEL_SELECTION_SUMMARY_PATH = RESULTS_DIR / "classification_model_selection_summary.txt"

REGRESSION_METRICS_PATH = RESULTS_DIR / "regression_productivity_metrics.csv"
REGRESSION_PREDICTIONS_PATH = RESULTS_DIR / "regression_productivity_predictions.csv"
REGRESSION_FEATURE_IMPORTANCE_PATH = RESULTS_DIR / "regression_productivity_permutation_importance.csv"
REGRESSION_TARGET_COMPARISON_PATH = RESULTS_DIR / "regression_target_comparison.csv"
REGRESSION_MODEL_SELECTION_SUMMARY_PATH = RESULTS_DIR / "regression_model_selection_summary.txt"

CLUSTERING_SCORES_PATH = RESULTS_DIR / "clustering_kmeans_scores.csv"
CLUSTERING_ASSIGNMENTS_PATH = RESULTS_DIR / "clustering_lifestyle_assignments.csv"
CLUSTERING_PROFILE_PATH = RESULTS_DIR / "clustering_lifestyle_profiles.csv"
CLUSTERING_PCA_PATH = RESULTS_DIR / "clustering_lifestyle_pca_coordinates.csv"
CLUSTERING_MODEL_COMPARISON_PATH = RESULTS_DIR / "clustering_model_comparison.csv"
CLUSTERING_PROFILE_INTERPRETATION_PATH = RESULTS_DIR / "clustering_profile_interpretation.txt"
