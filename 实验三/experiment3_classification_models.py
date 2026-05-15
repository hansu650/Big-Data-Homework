from __future__ import annotations

import time
import warnings
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier, plot_tree


RANDOM_STATE = 42
VALIDATION_SIZE = 0.2
TOP_CORRELATION_FEATURES = 25
TOP_IMPORTANCE_FEATURES = 20

MODEL_CONFIGS = {
    "entropy_tree": {
        "display_name": "Information Gain Decision Tree",
        "column_prefix": "information_gain_tree",
        "confusion_figure": "04_confusion_matrix_entropy_tree.png",
    },
    "gini_tree": {
        "display_name": "Gini Index Decision Tree",
        "column_prefix": "gini_index_tree",
        "confusion_figure": "05_confusion_matrix_gini_tree.png",
    },
    "naive_bayes": {
        "display_name": "Naive Bayes",
        "column_prefix": "naive_bayes",
        "confusion_figure": "06_confusion_matrix_naive_bayes.png",
    },
    "svm": {
        "display_name": "Support Vector Machine",
        "column_prefix": "svm",
        "confusion_figure": "07_confusion_matrix_svm.png",
    },
}

POSITIVE_KEYWORDS = {
    "1",
    "1.0",
    "yes",
    "y",
    "true",
    "t",
    "left",
    "leave",
    "leaver",
    "attrition",
    "attrited",
    "resigned",
    "quit",
    "是",
    "离职",
}

NEGATIVE_KEYWORDS = {
    "0",
    "0.0",
    "no",
    "n",
    "false",
    "f",
    "stay",
    "stayed",
    "active",
    "not left",
    "no attrition",
    "否",
    "在职",
    "未离职",
}


def resolve_paths(exp3_dir: str | Path | None = None) -> dict[str, Path]:
    """Resolve project paths so the script works from the repo root or Experiment 3."""
    if exp3_dir is None:
        exp3_dir = Path(__file__).resolve().parent
    else:
        exp3_dir = Path(exp3_dir).resolve()

    project_root = exp3_dir.parent
    exp2_dir = project_root / "实验二"
    return {
        "project_root": project_root,
        "exp3_dir": exp3_dir,
        "exp2_dir": exp2_dir,
        "results_dir": exp3_dir / "results",
        "figures_dir": exp3_dir / "figures",
        "x_train": exp2_dir / "X_train_preprocessed.csv",
        "x_test": exp2_dir / "X_test_preprocessed.csv",
        "y_train": exp2_dir / "y_train_preprocessed.csv",
    }


def ensure_output_dirs(paths: dict[str, Path]) -> None:
    paths["results_dir"].mkdir(parents=True, exist_ok=True)
    paths["figures_dir"].mkdir(parents=True, exist_ok=True)


def check_required_files(paths: dict[str, Path]) -> None:
    required_files = [paths["x_train"], paths["x_test"], paths["y_train"]]
    missing_files = [str(path) for path in required_files if not path.exists()]
    if missing_files:
        raise FileNotFoundError(
            "The following required data files were not found:\n"
            + "\n".join(missing_files)
        )


def load_data(paths: dict[str, Path]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    check_required_files(paths)
    x_train_full = pd.read_csv(paths["x_train"])
    x_test_full = pd.read_csv(paths["x_test"])
    y_train_raw = pd.read_csv(paths["y_train"])

    print("Data loaded from Experiment 2.")
    print(f"X_train shape: {x_train_full.shape}")
    print(f"X_test shape: {x_test_full.shape}")
    print(f"y_train shape: {y_train_raw.shape}")

    return x_train_full, x_test_full, y_train_raw


def count_infinite_values(frame: pd.DataFrame) -> int:
    numeric_frame = frame.select_dtypes(include=[np.number])
    if numeric_frame.empty:
        return 0
    return int(np.isinf(numeric_frame.to_numpy()).sum())


def print_basic_data_checks(
    x_train_full: pd.DataFrame,
    x_test_full: pd.DataFrame,
    y_train_raw: pd.DataFrame,
) -> None:
    print("\nBasic data checks")
    print(f"X_train missing values: {int(x_train_full.isna().sum().sum())}")
    print(f"X_test missing values: {int(x_test_full.isna().sum().sum())}")
    print(f"y_train missing values: {int(y_train_raw.isna().sum().sum())}")
    print(f"X_train infinite values: {count_infinite_values(x_train_full)}")
    print(f"X_test infinite values: {count_infinite_values(x_test_full)}")


def align_and_clean_features(
    x_train_full: pd.DataFrame,
    x_test_full: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Align test columns to train columns and use simple safe cleaning for NaN/inf."""
    train_columns = list(x_train_full.columns)
    missing_in_test = [col for col in train_columns if col not in x_test_full.columns]
    extra_in_test = [col for col in x_test_full.columns if col not in train_columns]

    if missing_in_test:
        print(f"Columns missing in X_test and filled with 0: {missing_in_test}")
    if extra_in_test:
        print(f"Extra columns in X_test dropped: {extra_in_test}")

    x_train_clean = x_train_full.copy()
    x_test_aligned = x_test_full.copy()
    for col in missing_in_test:
        x_test_aligned[col] = 0
    x_test_aligned = x_test_aligned[train_columns]

    non_numeric_columns = [
        col
        for col in train_columns
        if not pd.api.types.is_numeric_dtype(x_train_clean[col])
        or not pd.api.types.is_numeric_dtype(x_test_aligned[col])
    ]
    if non_numeric_columns:
        print(
            "Non-numeric columns were converted with pandas.to_numeric: "
            f"{non_numeric_columns}"
        )

    x_train_clean = x_train_clean.apply(pd.to_numeric, errors="coerce")
    x_test_clean = x_test_aligned.apply(pd.to_numeric, errors="coerce")

    x_train_clean = x_train_clean.replace([np.inf, -np.inf], np.nan)
    x_test_clean = x_test_clean.replace([np.inf, -np.inf], np.nan)

    medians = x_train_clean.median(numeric_only=True).replace(
        [np.inf, -np.inf], np.nan
    )
    medians = medians.fillna(0)

    train_missing_before = int(x_train_clean.isna().sum().sum())
    test_missing_before = int(x_test_clean.isna().sum().sum())
    if train_missing_before or test_missing_before:
        print(
            "NaN or infinite values were handled with train-set medians, "
            "then 0 for any remaining empty columns."
        )

    x_train_clean = x_train_clean.fillna(medians).fillna(0)
    x_test_clean = x_test_clean.fillna(medians).fillna(0)

    print(f"Cleaned X_train shape: {x_train_clean.shape}")
    print(f"Cleaned X_test shape: {x_test_clean.shape}")
    return x_train_clean, x_test_clean


def extract_label_series(y_train_raw: pd.DataFrame | pd.Series) -> pd.Series:
    if isinstance(y_train_raw, pd.DataFrame):
        if y_train_raw.shape[1] > 1:
            print("y_train has more than one column. The first column is used as label.")
        y_series = y_train_raw.iloc[:, 0]
    else:
        y_series = pd.Series(y_train_raw)

    y_series = y_series.reset_index(drop=True)
    if y_series.isna().any():
        label_mode = y_series.mode(dropna=True)
        fill_value = label_mode.iloc[0] if not label_mode.empty else 0
        print(f"Missing labels found. They were filled with the mode value: {fill_value}")
        y_series = y_series.fillna(fill_value)

    print("\nLabel distribution before encoding:")
    print(y_series.value_counts(dropna=False))
    return y_series


def _normalized_label(value: Any) -> str:
    return str(value).strip().lower()


def choose_positive_label(labels: list[Any]) -> Any:
    """Try to detect the attrition/leave class. Fall back to the largest label."""
    normalized_map = {label: _normalized_label(label) for label in labels}

    for label, text in normalized_map.items():
        if text in POSITIVE_KEYWORDS:
            return label

    strong_keywords = POSITIVE_KEYWORDS - {"1", "1.0", "y", "t"}
    for label, text in normalized_map.items():
        if text in NEGATIVE_KEYWORDS or text.startswith("no "):
            continue
        if any(keyword in text for keyword in strong_keywords):
            return label

    numeric_labels = pd.to_numeric(pd.Series(labels), errors="coerce")
    if numeric_labels.notna().all():
        if (numeric_labels == 1).any():
            return labels[int(np.where(numeric_labels.to_numpy() == 1)[0][0])]
        return labels[int(numeric_labels.to_numpy().argmax())]

    return sorted(labels, key=lambda item: str(item))[-1]


def encode_labels(y_series: pd.Series) -> tuple[np.ndarray, dict[str, Any]]:
    """Convert labels to binary 0/1 labels for sklearn metrics."""
    unique_labels = list(pd.unique(y_series))
    if len(unique_labels) < 2:
        raise ValueError("At least two label classes are required for classification.")

    numeric_labels = pd.to_numeric(y_series, errors="coerce")
    unique_numeric = sorted(pd.unique(numeric_labels.dropna()))
    is_clean_binary_numeric = (
        numeric_labels.notna().all() and set(unique_numeric).issubset({0, 1})
    )

    if is_clean_binary_numeric:
        y = numeric_labels.astype(int).to_numpy()
        positive_label = 1
        encoder_classes = None
        print("Numeric 0/1 labels detected. Positive class is 1.")
    else:
        positive_label = choose_positive_label(unique_labels)
        encoder = LabelEncoder()
        labels_as_text = y_series.astype(str)
        encoded = encoder.fit_transform(labels_as_text)
        positive_text = str(positive_label)

        if positive_text in encoder.classes_:
            positive_code = int(np.where(encoder.classes_ == positive_text)[0][0])
        else:
            positive_code = len(encoder.classes_) - 1
            positive_label = encoder.classes_[positive_code]

        y = np.where(encoded == positive_code, 1, 0).astype(int)
        encoder_classes = list(encoder.classes_)
        print("LabelEncoder was used for non-0/1 labels.")
        print(f"Encoder classes: {encoder_classes}")
        print(f"Positive class: {positive_label}")

    print("\nEncoded label distribution:")
    print(pd.Series(y).value_counts().sort_index())

    metadata = {
        "positive_label": positive_label,
        "encoder_classes": encoder_classes,
        "negative_class": 0,
        "positive_class": 1,
    }
    return y, metadata


def plot_target_distribution(y: np.ndarray, paths: dict[str, Path]) -> Path:
    counts = pd.Series(y).value_counts().sort_index()
    labels = ["Negative (0)", "Positive (1)"]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(labels, [counts.get(0, 0), counts.get(1, 0)], color=["#4C78A8", "#F58518"])
    ax.set_title("Target Distribution")
    ax.set_xlabel("Class")
    ax.set_ylabel("Number of Employees")
    for index, value in enumerate([counts.get(0, 0), counts.get(1, 0)]):
        ax.text(index, value, str(value), ha="center", va="bottom")
    fig.tight_layout()

    output_path = paths["figures_dir"] / "01_target_distribution.png"
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def plot_feature_correlation_heatmap(
    x_train_full: pd.DataFrame,
    paths: dict[str, Path],
    top_n: int = TOP_CORRELATION_FEATURES,
) -> Path:
    variances = x_train_full.var().sort_values(ascending=False)
    selected_features = list(variances.head(min(top_n, len(variances))).index)
    corr_matrix = x_train_full[selected_features].corr().fillna(0)

    fig_width = max(10, len(selected_features) * 0.45)
    fig, ax = plt.subplots(figsize=(fig_width, fig_width * 0.75))
    image = ax.imshow(corr_matrix, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_title(f"Feature Correlation Heatmap (Top {len(selected_features)} by Variance)")
    ax.set_xticks(np.arange(len(selected_features)))
    ax.set_yticks(np.arange(len(selected_features)))
    ax.set_xticklabels(selected_features, rotation=60, ha="right", fontsize=7)
    ax.set_yticklabels(selected_features, fontsize=7)
    ax.set_xlabel("Features")
    ax.set_ylabel("Features")
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04, label="Correlation")
    fig.tight_layout()

    output_path = paths["figures_dir"] / "02_feature_correlation_heatmap.png"
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def split_training_validation(
    x_train_full: pd.DataFrame,
    y: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    x_train, x_val, y_train, y_val = train_test_split(
        x_train_full,
        y,
        test_size=VALIDATION_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    print("\nTraining/validation split")
    print(f"Training set shape: {x_train.shape}")
    print(f"Validation set shape: {x_val.shape}")
    print("Training label distribution:")
    print(pd.Series(y_train).value_counts().sort_index())
    print("Validation label distribution:")
    print(pd.Series(y_val).value_counts().sort_index())
    return x_train, x_val, y_train, y_val


def define_models() -> dict[str, Any]:
    return {
        "entropy_tree": DecisionTreeClassifier(
            criterion="entropy",
            random_state=RANDOM_STATE,
        ),
        "gini_tree": DecisionTreeClassifier(
            criterion="gini",
            random_state=RANDOM_STATE,
        ),
        "naive_bayes": GaussianNB(),
        "svm": Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "svm",
                    SVC(kernel="rbf", probability=True, random_state=RANDOM_STATE),
                ),
            ]
        ),
    }


def get_positive_scores(model: Any, x_data: pd.DataFrame) -> np.ndarray:
    """Return positive class probability when available, otherwise a decision score."""
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(x_data)
        if probabilities.ndim == 2 and probabilities.shape[1] > 1:
            return probabilities[:, 1]
        return probabilities.ravel()

    if hasattr(model, "decision_function"):
        scores = model.decision_function(x_data)
        return np.asarray(scores).ravel()

    return model.predict(x_data)


def safe_auc(metric_name: str, y_true: np.ndarray, y_score: np.ndarray) -> float:
    try:
        if metric_name == "roc_auc":
            return float(roc_auc_score(y_true, y_score))
        if metric_name == "pr_auc":
            return float(average_precision_score(y_true, y_score))
    except ValueError as error:
        print(f"{metric_name} could not be calculated: {error}")
    return float("nan")


def train_and_evaluate_models(
    models: dict[str, Any],
    x_train: pd.DataFrame,
    x_val: pd.DataFrame,
    y_train: np.ndarray,
    y_val: np.ndarray,
) -> dict[str, Any]:
    evaluation_rows: list[dict[str, Any]] = []
    runtime_rows: list[dict[str, Any]] = []
    report_sections: list[str] = []
    roc_data: dict[str, tuple[np.ndarray, np.ndarray, float]] = {}
    pr_data: dict[str, tuple[np.ndarray, np.ndarray, float]] = {}
    confusion_matrices: dict[str, np.ndarray] = {}
    error_rows: list[dict[str, Any]] = []

    validation_predictions = pd.DataFrame(
        {
            "validation_index": x_val.index.to_numpy(),
            "true_label": y_val,
        }
    )

    for model_key, model in models.items():
        display_name = MODEL_CONFIGS[model_key]["display_name"]
        column_prefix = MODEL_CONFIGS[model_key]["column_prefix"]
        print(f"\nTraining {display_name}...")

        training_start = time.perf_counter()
        model.fit(x_train, y_train)
        training_time = time.perf_counter() - training_start

        prediction_start = time.perf_counter()
        y_val_pred = model.predict(x_val)
        y_val_score = get_positive_scores(model, x_val)
        prediction_time = time.perf_counter() - prediction_start

        training_score = float(model.score(x_train, y_train))
        validation_score = float(accuracy_score(y_val, y_val_pred))
        overfitting_gap = training_score - validation_score

        accuracy = float(accuracy_score(y_val, y_val_pred))
        precision = float(precision_score(y_val, y_val_pred, zero_division=0))
        recall = float(recall_score(y_val, y_val_pred, zero_division=0))
        f1 = float(f1_score(y_val, y_val_pred, zero_division=0))
        roc_auc = safe_auc("roc_auc", y_val, y_val_score)
        pr_auc = safe_auc("pr_auc", y_val, y_val_score)

        cm = confusion_matrix(y_val, y_val_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()
        confusion_matrices[model_key] = cm

        if not np.isnan(roc_auc):
            fpr, tpr, _ = roc_curve(y_val, y_val_score)
            roc_data[model_key] = (fpr, tpr, roc_auc)
        if not np.isnan(pr_auc):
            precision_curve, recall_curve, _ = precision_recall_curve(y_val, y_val_score)
            pr_data[model_key] = (recall_curve, precision_curve, pr_auc)

        evaluation_rows.append(
            {
                "model": display_name,
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "roc_auc": roc_auc,
                "pr_auc": pr_auc,
                "training_score": training_score,
                "validation_score": validation_score,
                "overfitting_gap": overfitting_gap,
                "training_time_seconds": training_time,
                "prediction_time_seconds": prediction_time,
                "true_negative": int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_positive": int(tp),
            }
        )
        runtime_rows.append(
            {
                "model": display_name,
                "training_time_seconds": training_time,
                "prediction_time_seconds": prediction_time,
            }
        )
        error_rows.extend(
            [
                {
                    "model": display_name,
                    "error_type": "False Positive",
                    "count": int(fp),
                },
                {
                    "model": display_name,
                    "error_type": "False Negative",
                    "count": int(fn),
                },
            ]
        )

        validation_predictions[f"{column_prefix}_predicted_label"] = y_val_pred
        validation_predictions[f"{column_prefix}_positive_probability"] = y_val_score

        report_sections.append(
            "\n".join(
                [
                    f"=== {display_name} ===",
                    "Confusion matrix labels: [0, 1]",
                    str(cm),
                    "",
                    classification_report(
                        y_val,
                        y_val_pred,
                        labels=[0, 1],
                        target_names=["Negative (0)", "Positive (1)"],
                        zero_division=0,
                    ),
                    "",
                ]
            )
        )

        print(
            f"{display_name}: accuracy={accuracy:.4f}, recall={recall:.4f}, "
            f"f1={f1:.4f}, roc_auc={roc_auc:.4f}, pr_auc={pr_auc:.4f}"
        )

    return {
        "models": models,
        "evaluation": pd.DataFrame(evaluation_rows),
        "runtime": pd.DataFrame(runtime_rows),
        "validation_predictions": validation_predictions,
        "classification_report_text": "\n".join(report_sections),
        "roc_data": roc_data,
        "pr_data": pr_data,
        "confusion_matrices": confusion_matrices,
        "error_counts": pd.DataFrame(error_rows),
    }


def make_model_ranking_summary(evaluation_df: pd.DataFrame) -> pd.DataFrame:
    def best_model(metric: str, prefer_min: bool = False) -> tuple[str, float]:
        series = evaluation_df[["model", metric]].replace([np.inf, -np.inf], np.nan)
        series = series.dropna(subset=[metric])
        if series.empty:
            return "N/A", float("nan")
        index = series[metric].idxmin() if prefer_min else series[metric].idxmax()
        row = evaluation_df.loc[index]
        return str(row["model"]), float(row[metric])

    best_accuracy_model, best_accuracy_value = best_model("accuracy")
    best_precision_model, best_precision_value = best_model("precision")
    best_recall_model, best_recall_value = best_model("recall")
    best_f1_model, best_f1_value = best_model("f1_score")
    best_roc_auc_model, best_roc_auc_value = best_model("roc_auc")
    best_pr_auc_model, best_pr_auc_value = best_model("pr_auc")
    fastest_training_model, fastest_training_value = best_model(
        "training_time_seconds", prefer_min=True
    )
    largest_gap_model, largest_gap_value = best_model("overfitting_gap")

    return pd.DataFrame(
        [
            {
                "best_accuracy_model": best_accuracy_model,
                "best_accuracy_value": best_accuracy_value,
                "best_precision_model": best_precision_model,
                "best_precision_value": best_precision_value,
                "best_recall_model": best_recall_model,
                "best_recall_value": best_recall_value,
                "best_f1_model": best_f1_model,
                "best_f1_value": best_f1_value,
                "best_roc_auc_model": best_roc_auc_model,
                "best_roc_auc_value": best_roc_auc_value,
                "best_pr_auc_model": best_pr_auc_model,
                "best_pr_auc_value": best_pr_auc_value,
                "fastest_training_model": fastest_training_model,
                "fastest_training_seconds": fastest_training_value,
                "largest_overfitting_gap_model": largest_gap_model,
                "largest_overfitting_gap_value": largest_gap_value,
            }
        ]
    )


def save_evaluation_outputs(outputs: dict[str, Any], paths: dict[str, Path]) -> pd.DataFrame:
    evaluation_df = outputs["evaluation"]
    runtime_df = outputs["runtime"]
    validation_predictions = outputs["validation_predictions"]
    ranking_df = make_model_ranking_summary(evaluation_df)

    evaluation_df.to_csv(paths["results_dir"] / "model_evaluation_results.csv", index=False)
    runtime_df.to_csv(paths["results_dir"] / "model_runtime_results.csv", index=False)
    validation_predictions.to_csv(
        paths["results_dir"] / "validation_predictions_all_models.csv",
        index=False,
    )
    ranking_df.to_csv(paths["results_dir"] / "model_ranking_summary.csv", index=False)

    report_path = paths["results_dir"] / "classification_report_all_models.txt"
    report_path.write_text(outputs["classification_report_text"], encoding="utf-8")

    return ranking_df


def plot_model_metrics_comparison(
    evaluation_df: pd.DataFrame,
    paths: dict[str, Path],
) -> Path:
    metrics = ["accuracy", "precision", "recall", "f1_score", "roc_auc", "pr_auc"]
    metric_labels = ["Accuracy", "Precision", "Recall", "F1-score", "ROC-AUC", "PR-AUC"]
    models = evaluation_df["model"].tolist()
    x_positions = np.arange(len(metrics))
    bar_width = 0.18

    fig, ax = plt.subplots(figsize=(12, 6))
    for index, model_name in enumerate(models):
        values = evaluation_df.loc[evaluation_df["model"] == model_name, metrics]
        values = values.iloc[0].replace([np.inf, -np.inf], np.nan).fillna(0).to_numpy()
        ax.bar(
            x_positions + (index - 1.5) * bar_width,
            values,
            width=bar_width,
            label=model_name,
        )

    ax.set_title("Model Metrics Comparison")
    ax.set_xlabel("Evaluation Metric")
    ax.set_ylabel("Score")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(metric_labels)
    ax.set_ylim(0, 1.05)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.35), ncol=2)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()

    output_path = paths["figures_dir"] / "03_model_metrics_comparison.png"
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def plot_confusion_matrix_figure(
    cm: np.ndarray,
    title: str,
    output_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(5.5, 4.8))
    image = ax.imshow(cm, cmap="Blues")
    ax.set_title(title)
    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("True Label")
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["Negative (0)", "Positive (1)"])
    ax.set_yticklabels(["Negative (0)", "Positive (1)"])

    threshold = cm.max() / 2 if cm.max() else 0
    for row in range(cm.shape[0]):
        for col in range(cm.shape[1]):
            color = "white" if cm[row, col] > threshold else "black"
            ax.text(col, row, int(cm[row, col]), ha="center", va="center", color=color)

    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04, label="Count")
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def plot_all_confusion_matrices(outputs: dict[str, Any], paths: dict[str, Path]) -> list[Path]:
    saved_paths = []
    for model_key, cm in outputs["confusion_matrices"].items():
        display_name = MODEL_CONFIGS[model_key]["display_name"]
        output_path = paths["figures_dir"] / MODEL_CONFIGS[model_key]["confusion_figure"]
        plot_confusion_matrix_figure(cm, f"{display_name} Confusion Matrix", output_path)
        saved_paths.append(output_path)
    return saved_paths


def plot_roc_curves(outputs: dict[str, Any], paths: dict[str, Path]) -> Path:
    fig, ax = plt.subplots(figsize=(7, 6))
    if outputs["roc_data"]:
        for model_key, (fpr, tpr, auc_value) in outputs["roc_data"].items():
            display_name = MODEL_CONFIGS[model_key]["display_name"]
            ax.plot(fpr, tpr, label=f"{display_name} (AUC = {auc_value:.3f})")
        ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Random Guess")
        ax.legend(loc="lower right", fontsize=8)
    else:
        ax.text(0.5, 0.5, "ROC curve unavailable", ha="center", va="center")

    ax.set_title("ROC Curves for All Models")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.grid(alpha=0.25)
    fig.tight_layout()

    output_path = paths["figures_dir"] / "08_roc_curves_all_models.png"
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def plot_pr_curves(outputs: dict[str, Any], paths: dict[str, Path]) -> Path:
    fig, ax = plt.subplots(figsize=(7, 6))
    if outputs["pr_data"]:
        for model_key, (recall_curve, precision_curve, auc_value) in outputs[
            "pr_data"
        ].items():
            display_name = MODEL_CONFIGS[model_key]["display_name"]
            ax.plot(
                recall_curve,
                precision_curve,
                label=f"{display_name} (PR-AUC = {auc_value:.3f})",
            )
        ax.legend(loc="lower left", fontsize=8)
    else:
        ax.text(0.5, 0.5, "PR curve unavailable", ha="center", va="center")

    ax.set_title("Precision-Recall Curves for All Models")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.grid(alpha=0.25)
    fig.tight_layout()

    output_path = paths["figures_dir"] / "09_pr_curves_all_models.png"
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def plot_tree_structures(
    models: dict[str, Any],
    feature_names: list[str],
    paths: dict[str, Path],
    max_depth: int = 3,
) -> list[Path]:
    saved_paths = []
    tree_figures = {
        "entropy_tree": "10_entropy_tree_structure.png",
        "gini_tree": "11_gini_tree_structure.png",
    }

    for model_key, filename in tree_figures.items():
        display_name = MODEL_CONFIGS[model_key]["display_name"]
        fig, ax = plt.subplots(figsize=(24, 12))
        plot_tree(
            models[model_key],
            feature_names=feature_names,
            class_names=["Negative (0)", "Positive (1)"],
            filled=True,
            rounded=True,
            max_depth=max_depth,
            fontsize=7,
            ax=ax,
        )
        ax.set_title(f"{display_name} Structure (Max Depth = {max_depth})")
        fig.tight_layout()

        output_path = paths["figures_dir"] / filename
        fig.savefig(output_path, dpi=300)
        plt.close(fig)
        saved_paths.append(output_path)

    return saved_paths


def plot_tree_feature_importance(
    models: dict[str, Any],
    feature_names: list[str],
    paths: dict[str, Path],
    top_n: int = TOP_IMPORTANCE_FEATURES,
) -> list[Path]:
    saved_paths = []
    importance_figures = {
        "entropy_tree": "12_entropy_tree_feature_importance.png",
        "gini_tree": "13_gini_tree_feature_importance.png",
    }

    feature_array = np.asarray(feature_names)
    for model_key, filename in importance_figures.items():
        display_name = MODEL_CONFIGS[model_key]["display_name"]
        importances = models[model_key].feature_importances_
        top_count = min(top_n, len(importances))
        top_indices = np.argsort(importances)[::-1][:top_count][::-1]

        fig, ax = plt.subplots(figsize=(10, 7))
        ax.barh(feature_array[top_indices], importances[top_indices], color="#4C78A8")
        ax.set_title(f"{display_name} Top {top_count} Feature Importances")
        ax.set_xlabel("Feature Importance")
        ax.set_ylabel("Feature")
        ax.grid(axis="x", alpha=0.25)
        fig.tight_layout()

        output_path = paths["figures_dir"] / filename
        fig.savefig(output_path, dpi=300)
        plt.close(fig)
        saved_paths.append(output_path)

    return saved_paths


def plot_prediction_probability_distribution(
    validation_predictions: pd.DataFrame,
    paths: dict[str, Path],
) -> Path:
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.ravel()

    for index, (model_key, config) in enumerate(MODEL_CONFIGS.items()):
        column = f"{config['column_prefix']}_positive_probability"
        axes[index].hist(
            validation_predictions[column],
            bins=20,
            color="#4C78A8",
            alpha=0.78,
            edgecolor="white",
        )
        axes[index].set_title(f"{config['display_name']} Positive Probability")
        axes[index].set_xlabel("Positive Class Probability / Score")
        axes[index].set_ylabel("Frequency")
        axes[index].grid(axis="y", alpha=0.25)

    fig.suptitle("Prediction Probability Distribution on Validation Set", y=1.02)
    fig.tight_layout()

    output_path = paths["figures_dir"] / "14_prediction_probability_distribution.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_error_analysis(error_counts: pd.DataFrame, paths: dict[str, Path]) -> Path:
    models = error_counts["model"].drop_duplicates().tolist()
    false_positive_counts = []
    false_negative_counts = []
    for model_name in models:
        model_errors = error_counts[error_counts["model"] == model_name]
        false_positive_counts.append(
            int(
                model_errors.loc[
                    model_errors["error_type"] == "False Positive", "count"
                ].iloc[0]
            )
        )
        false_negative_counts.append(
            int(
                model_errors.loc[
                    model_errors["error_type"] == "False Negative", "count"
                ].iloc[0]
            )
        )

    x_positions = np.arange(len(models))
    bar_width = 0.36
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar(
        x_positions - bar_width / 2,
        false_positive_counts,
        width=bar_width,
        label="False Positive",
        color="#72B7B2",
    )
    ax.bar(
        x_positions + bar_width / 2,
        false_negative_counts,
        width=bar_width,
        label="False Negative",
        color="#E45756",
    )
    ax.set_title("Error Analysis: False Positives and False Negatives")
    ax.set_xlabel("Model")
    ax.set_ylabel("Number of Validation Samples")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(models, rotation=15, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()

    output_path = paths["figures_dir"] / "15_error_analysis_fp_fn.png"
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def plot_runtime_comparison(runtime_df: pd.DataFrame, paths: dict[str, Path]) -> Path:
    models = runtime_df["model"].tolist()
    x_positions = np.arange(len(models))
    bar_width = 0.36

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar(
        x_positions - bar_width / 2,
        runtime_df["training_time_seconds"],
        width=bar_width,
        label="Training Time",
        color="#4C78A8",
    )
    ax.bar(
        x_positions + bar_width / 2,
        runtime_df["prediction_time_seconds"],
        width=bar_width,
        label="Prediction Time",
        color="#F58518",
    )
    ax.set_title("Model Training and Prediction Time Comparison")
    ax.set_xlabel("Model")
    ax.set_ylabel("Time (seconds)")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(models, rotation=15, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()

    output_path = paths["figures_dir"] / "16_model_training_time_comparison.png"
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def generate_all_figures(
    outputs: dict[str, Any],
    x_train_full: pd.DataFrame,
    y: np.ndarray,
    paths: dict[str, Path],
) -> list[Path]:
    figure_paths = [
        plot_target_distribution(y, paths),
        plot_feature_correlation_heatmap(x_train_full, paths),
        plot_model_metrics_comparison(outputs["evaluation"], paths),
    ]
    figure_paths.extend(plot_all_confusion_matrices(outputs, paths))
    figure_paths.append(plot_roc_curves(outputs, paths))
    figure_paths.append(plot_pr_curves(outputs, paths))
    figure_paths.extend(
        plot_tree_structures(outputs["models"], list(x_train_full.columns), paths)
    )
    figure_paths.extend(
        plot_tree_feature_importance(outputs["models"], list(x_train_full.columns), paths)
    )
    figure_paths.append(
        plot_prediction_probability_distribution(outputs["validation_predictions"], paths)
    )
    figure_paths.append(plot_error_analysis(outputs["error_counts"], paths))
    figure_paths.append(plot_runtime_comparison(outputs["runtime"], paths))
    return figure_paths


def predict_test_set(
    models: dict[str, Any],
    x_test_full: pd.DataFrame,
    paths: dict[str, Path] | None = None,
) -> pd.DataFrame:
    test_predictions = pd.DataFrame({"test_index": x_test_full.index.to_numpy()})

    for model_key, model in models.items():
        column_prefix = MODEL_CONFIGS[model_key]["column_prefix"]
        test_predictions[f"{column_prefix}_predicted_label"] = model.predict(x_test_full)
        test_predictions[f"{column_prefix}_positive_probability"] = get_positive_scores(
            model,
            x_test_full,
        )

    if paths is not None:
        output_path = paths["results_dir"] / "test_predictions.csv"
        test_predictions.to_csv(output_path, index=False)
        print(f"Test predictions saved to: {output_path}")

    return test_predictions


def make_analysis_text(evaluation_df: pd.DataFrame) -> str:
    def row_for(metric: str, prefer_min: bool = False) -> pd.Series:
        clean_df = evaluation_df.replace([np.inf, -np.inf], np.nan).dropna(
            subset=[metric]
        )
        index = clean_df[metric].idxmin() if prefer_min else clean_df[metric].idxmax()
        return evaluation_df.loc[index]

    best_accuracy = row_for("accuracy")
    best_recall = row_for("recall")
    best_f1 = row_for("f1_score")
    largest_gap = row_for("overfitting_gap")
    fastest = row_for("training_time_seconds", prefer_min=True)

    recommended = best_recall
    if best_f1["recall"] >= best_recall["recall"] * 0.95 and best_f1["f1_score"] > best_recall["f1_score"]:
        recommended = best_f1

    return "\n".join(
        [
            "Detailed model evaluation analysis:",
            f"1. Highest accuracy: {best_accuracy['model']} ({best_accuracy['accuracy']:.4f}).",
            f"2. Highest recall: {best_recall['model']} ({best_recall['recall']:.4f}).",
            f"3. Highest F1-score: {best_f1['model']} ({best_f1['f1_score']:.4f}).",
            f"4. Largest overfitting gap: {largest_gap['model']} ({largest_gap['overfitting_gap']:.4f}).",
            f"5. Fastest training: {fastest['model']} ({fastest['training_time_seconds']:.6f} seconds).",
            f"6. Suggested model for employee attrition prediction: {recommended['model']}. "
            "This choice gives priority to recall while still considering F1-score.",
            "7. Accuracy alone is not enough for attrition prediction because the positive class "
            "is usually smaller and false negatives are costly. Recall, F1-score, PR-AUC, "
            "and the false-negative count show whether the model can find employees who may leave.",
        ]
    )


def run_experiment(exp3_dir: str | Path | None = None) -> dict[str, Any]:
    warnings.filterwarnings("ignore", category=UserWarning)
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.unicode_minus"] = False

    paths = resolve_paths(exp3_dir)
    ensure_output_dirs(paths)

    print("Experiment 3: Classification Models for Employee Attrition")
    print(f"Experiment 3 directory: {paths['exp3_dir']}")
    print(f"Experiment 2 data directory: {paths['exp2_dir']}")

    x_train_raw, x_test_raw, y_train_raw = load_data(paths)
    print_basic_data_checks(x_train_raw, x_test_raw, y_train_raw)

    y_series = extract_label_series(y_train_raw)
    y, label_metadata = encode_labels(y_series)
    x_train_full, x_test_full = align_and_clean_features(x_train_raw, x_test_raw)

    if len(x_train_full) != len(y):
        raise ValueError(
            f"X_train rows ({len(x_train_full)}) and y_train rows ({len(y)}) do not match."
        )

    x_train, x_val, y_train, y_val = split_training_validation(x_train_full, y)
    models = define_models()
    outputs = train_and_evaluate_models(models, x_train, x_val, y_train, y_val)
    ranking_df = save_evaluation_outputs(outputs, paths)
    figure_paths = generate_all_figures(outputs, x_train_full, y, paths)
    test_predictions = predict_test_set(outputs["models"], x_test_full, paths)
    analysis_text = make_analysis_text(outputs["evaluation"])

    print("\nModel evaluation results:")
    print(outputs["evaluation"])
    print("\nModel ranking summary:")
    print(ranking_df)
    print("\n" + analysis_text)
    print("\nGenerated figures:")
    for figure_path in figure_paths:
        print(f"- {figure_path.name}")

    print("\nExperiment 3 completed successfully.")
    print(f"Results directory: {paths['results_dir']}")
    print(f"Figures directory: {paths['figures_dir']}")

    outputs.update(
        {
            "paths": paths,
            "label_metadata": label_metadata,
            "x_train_full": x_train_full,
            "x_test_full": x_test_full,
            "y": y,
            "x_train": x_train,
            "x_val": x_val,
            "y_train": y_train,
            "y_val": y_val,
            "ranking": ranking_df,
            "figure_paths": figure_paths,
            "test_predictions": test_predictions,
            "analysis_text": analysis_text,
        }
    )
    return outputs


def main() -> None:
    run_experiment()


if __name__ == "__main__":
    main()
