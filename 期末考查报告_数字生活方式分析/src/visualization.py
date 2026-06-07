from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import PrecisionRecallDisplay, RocCurveDisplay

try:
    from .config import DEFAULT_FIGURE_DPI, FIGURES_DIR
except ImportError:
    from config import DEFAULT_FIGURE_DPI, FIGURES_DIR


def configure_matplotlib() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": DEFAULT_FIGURE_DPI,
            "savefig.dpi": DEFAULT_FIGURE_DPI,
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 9,
        }
    )


def save_figure(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    return path


def plot_target_distribution(df: pd.DataFrame, target: str, path: Path) -> Path:
    configure_matplotlib()
    counts = df[target].value_counts().sort_index()
    plt.figure(figsize=(6, 4))
    plt.bar([str(index) for index in counts.index], counts.values, color=["#4C78A8", "#F58518"][: len(counts)])
    plt.xlabel(target)
    plt.ylabel("Count")
    plt.title(f"Distribution of {target}")
    for i, value in enumerate(counts.values):
        plt.text(i, value, str(value), ha="center", va="bottom")
    return save_figure(path)


def plot_missingness(missing_df: pd.DataFrame, path: Path, top_n: int = 24) -> Path:
    configure_matplotlib()
    subset = missing_df.head(top_n).iloc[::-1]
    plt.figure(figsize=(7, 6))
    plt.barh(subset["column"], subset["missing_rate"], color="#6B7280")
    plt.xlabel("Missing rate")
    plt.title("Missing Value Rate by Column")
    return save_figure(path)


def plot_numeric_histograms(df: pd.DataFrame, columns: list[str], path: Path, max_cols: int = 12) -> Path:
    configure_matplotlib()
    columns = [column for column in columns if column in df.columns][:max_cols]
    if not columns:
        raise ValueError("No numeric columns available for histogram plotting.")
    rows = int(np.ceil(len(columns) / 3))
    fig, axes = plt.subplots(rows, 3, figsize=(12, 3.3 * rows))
    axes = np.array(axes).reshape(-1)
    for ax, column in zip(axes, columns):
        ax.hist(df[column].dropna(), bins=30, color="#4C78A8", edgecolor="white")
        ax.set_title(column)
        ax.set_ylabel("Count")
    for ax in axes[len(columns) :]:
        ax.axis("off")
    return save_figure(path)


def plot_correlation_heatmap(df: pd.DataFrame, path: Path, columns: list[str] | None = None) -> Path:
    configure_matplotlib()
    numeric = df.select_dtypes(include=[np.number])
    if columns is not None:
        numeric = numeric[[column for column in columns if column in numeric.columns]]
    corr = numeric.corr()
    plt.figure(figsize=(10, 8))
    im = plt.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    plt.colorbar(im, fraction=0.046, pad=0.04)
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=75, ha="right")
    plt.yticks(range(len(corr.index)), corr.index)
    plt.title("Numeric Feature Correlation Heatmap")
    return save_figure(path)


def plot_confusion_matrix(cm: np.ndarray, path: Path, labels: list[str] | None = None) -> Path:
    configure_matplotlib()
    labels = labels or ["0", "1"]
    plt.figure(figsize=(5, 4))
    im = plt.imshow(cm, cmap="Blues")
    plt.colorbar(im, fraction=0.046, pad=0.04)
    plt.xticks(range(len(labels)), labels)
    plt.yticks(range(len(labels)), labels)
    plt.xlabel("Predicted label")
    plt.ylabel("True label")
    plt.title("Best Classification Model Confusion Matrix")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, str(cm[i, j]), ha="center", va="center", color="black")
    return save_figure(path)


def plot_roc_curve(y_true: pd.Series, y_score: np.ndarray, path: Path) -> Path:
    configure_matplotlib()
    plt.figure(figsize=(5, 4))
    RocCurveDisplay.from_predictions(y_true, y_score)
    plt.title("Classification ROC Curve")
    return save_figure(path)


def plot_precision_recall_curve(y_true: pd.Series, y_score: np.ndarray, path: Path) -> Path:
    configure_matplotlib()
    plt.figure(figsize=(5, 4))
    PrecisionRecallDisplay.from_predictions(y_true, y_score)
    plt.title("Classification Precision-Recall Curve")
    return save_figure(path)


def plot_classification_metrics_comparison(metrics_df: pd.DataFrame, path: Path) -> Path:
    configure_matplotlib()
    subset = metrics_df[metrics_df["dataset"] == "test"].copy()
    if subset.empty:
        subset = metrics_df.copy()
    metric_columns = [column for column in ["precision", "recall", "f1", "balanced_accuracy", "pr_auc"] if column in subset]
    labels = subset["threshold_policy"].fillna(subset["model"]).astype(str).tolist()
    x = np.arange(len(labels))
    width = 0.14
    plt.figure(figsize=(11, 5))
    for i, metric in enumerate(metric_columns):
        plt.bar(x + (i - len(metric_columns) / 2) * width, subset[metric], width=width, label=metric)
    plt.xticks(x, labels, rotation=20, ha="right")
    plt.ylim(0, 1.05)
    plt.ylabel("Metric value")
    plt.title("Classification Threshold Policy Metrics")
    plt.legend()
    return save_figure(path)


def plot_feature_importance(importance_df: pd.DataFrame, path: Path, title: str, top_n: int = 15) -> Path:
    configure_matplotlib()
    subset = importance_df.head(top_n).iloc[::-1]
    plt.figure(figsize=(8, 6))
    plt.barh(subset["feature"], subset["importance_mean"], color="#54A24B")
    plt.xlabel("Permutation importance")
    plt.title(title)
    return save_figure(path)


def plot_regression_predictions(y_true: pd.Series, y_pred: np.ndarray, path: Path) -> Path:
    configure_matplotlib()
    plt.figure(figsize=(5, 5))
    plt.scatter(y_true, y_pred, s=18, alpha=0.65, color="#4C78A8")
    lower = min(float(np.min(y_true)), float(np.min(y_pred)))
    upper = max(float(np.max(y_true)), float(np.max(y_pred)))
    plt.plot([lower, upper], [lower, upper], color="#E45756", linewidth=1.5)
    plt.xlabel("Observed value")
    plt.ylabel("Predicted value")
    plt.title("Observed vs Predicted Regression Target")
    return save_figure(path)


def plot_regression_residuals(y_true: pd.Series, y_pred: np.ndarray, path: Path) -> Path:
    configure_matplotlib()
    residuals = y_true - y_pred
    plt.figure(figsize=(6, 4))
    plt.scatter(y_pred, residuals, s=18, alpha=0.65, color="#72B7B2")
    plt.axhline(0, color="#E45756", linewidth=1.5)
    plt.xlabel("Predicted value")
    plt.ylabel("Residual")
    plt.title("Regression Residual Plot")
    return save_figure(path)


def plot_regression_target_comparison(comparison_df: pd.DataFrame, path: Path) -> Path:
    configure_matplotlib()
    targets = comparison_df["target"].astype(str).tolist()
    x = np.arange(len(targets))
    width = 0.25
    plt.figure(figsize=(8, 4.5))
    plt.bar(x - width, comparison_df["r2"], width=width, label="R2")
    plt.bar(x, comparison_df["mae"], width=width, label="MAE")
    plt.bar(x + width, comparison_df["rmse"], width=width, label="RMSE")
    plt.xticks(x, targets, rotation=15, ha="right")
    plt.title("Regression Target Comparison")
    plt.ylabel("Metric value")
    plt.legend()
    return save_figure(path)


def plot_clustering_scores(scores_df: pd.DataFrame, path: Path) -> Path:
    configure_matplotlib()
    plt.figure(figsize=(7, 4))
    plt.plot(scores_df["k"], scores_df["silhouette"], marker="o", label="Silhouette")
    plt.xlabel("Number of clusters (k)")
    plt.ylabel("Silhouette score")
    plt.title("KMeans Cluster Selection")
    plt.legend()
    return save_figure(path)


def plot_kmeans_elbow(scores_df: pd.DataFrame, path: Path) -> Path:
    configure_matplotlib()
    plt.figure(figsize=(7, 4))
    plt.plot(scores_df["k"], scores_df["inertia"], marker="o", color="#4C78A8")
    plt.xlabel("Number of clusters (k)")
    plt.ylabel("Inertia")
    plt.title("KMeans Elbow Curve")
    return save_figure(path)


def plot_silhouette_by_k(model_comparison_df: pd.DataFrame, path: Path) -> Path:
    configure_matplotlib()
    plt.figure(figsize=(7, 4))
    for algorithm, subset in model_comparison_df.groupby("algorithm"):
        plt.plot(subset["k"], subset["silhouette"], marker="o", label=algorithm)
    plt.xlabel("Number of clusters/components")
    plt.ylabel("Silhouette score")
    plt.title("Silhouette by Algorithm and k")
    plt.legend()
    return save_figure(path)


def plot_clustering_model_comparison(model_comparison_df: pd.DataFrame, path: Path) -> Path:
    configure_matplotlib()
    best_by_algorithm = (
        model_comparison_df.dropna(subset=["silhouette"])
        .sort_values(["algorithm", "silhouette"], ascending=[True, False])
        .groupby("algorithm")
        .head(1)
    )
    labels = [f"{row.algorithm}\\nk={int(row.k)}" for row in best_by_algorithm.itertuples()]
    plt.figure(figsize=(7, 4))
    plt.bar(labels, best_by_algorithm["silhouette"], color="#4C78A8")
    plt.ylabel("Best silhouette score")
    plt.title("Best Clustering Result by Algorithm")
    return save_figure(path)


def plot_cluster_pca(coords_df: pd.DataFrame, path: Path) -> Path:
    configure_matplotlib()
    plt.figure(figsize=(7, 5))
    clusters = sorted(coords_df["cluster"].unique())
    for cluster in clusters:
        subset = coords_df[coords_df["cluster"] == cluster]
        plt.scatter(subset["pc1"], subset["pc2"], s=20, alpha=0.65, label=f"Cluster {cluster}")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.title("Lifestyle Clusters Projected by PCA")
    plt.legend()
    return save_figure(path)


def plot_cluster_profile_heatmap(profile_df: pd.DataFrame, path: Path) -> Path:
    configure_matplotlib()
    columns = [
        "device_hours_per_day",
        "phone_unlocks",
        "notifications_per_day",
        "social_media_mins",
        "study_mins",
        "physical_activity_days",
        "sleep_hours",
        "sleep_quality",
        "high_risk_flag",
        "productivity_score",
        "digital_dependence_score",
    ]
    columns = [column for column in columns if column in profile_df.columns]
    data = profile_df.set_index("cluster")[columns].copy()
    scaled = (data - data.mean()) / data.std(ddof=0).replace(0, 1)
    plt.figure(figsize=(10, 4.8))
    im = plt.imshow(scaled, cmap="coolwarm", aspect="auto", vmin=-2, vmax=2)
    plt.colorbar(im, fraction=0.046, pad=0.04)
    plt.xticks(range(len(columns)), columns, rotation=45, ha="right")
    plt.yticks(range(len(scaled.index)), [f"Cluster {idx}" for idx in scaled.index])
    plt.title("Cluster Profile Heatmap (Standardized Means)")
    return save_figure(path)


def plot_eda_boxplots_by_risk(df: pd.DataFrame, target: str, columns: list[str], path: Path) -> Path:
    configure_matplotlib()
    columns = [column for column in columns if column in df.columns]
    rows = int(np.ceil(len(columns) / 4))
    fig, axes = plt.subplots(rows, 4, figsize=(14, 3.2 * rows))
    axes = np.array(axes).reshape(-1)
    for ax, column in zip(axes, columns):
        grouped = [df[df[target] == value][column].dropna() for value in sorted(df[target].dropna().unique())]
        ax.boxplot(grouped, labels=[str(value) for value in sorted(df[target].dropna().unique())], showfliers=False)
        ax.set_title(column)
        ax.set_xlabel(target)
    for ax in axes[len(columns) :]:
        ax.axis("off")
    return save_figure(path)


def category_risk_rate_table(df: pd.DataFrame, target: str, columns: list[str]) -> pd.DataFrame:
    rows = []
    for column in [column for column in columns if column in df.columns]:
        grouped = df.groupby(column)[target].agg(["count", "mean"]).reset_index()
        for _, row in grouped.iterrows():
            rows.append(
                {
                    "variable": column,
                    "category": row[column],
                    "count": int(row["count"]),
                    "risk_rate": float(row["mean"]),
                }
            )
    return pd.DataFrame(rows)


def plot_category_risk_rate(risk_rate_df: pd.DataFrame, path: Path, max_categories: int = 8) -> Path:
    configure_matplotlib()
    variables = risk_rate_df["variable"].drop_duplicates().tolist()
    rows = int(np.ceil(len(variables) / 2))
    fig, axes = plt.subplots(rows, 2, figsize=(12, 3.6 * rows))
    axes = np.array(axes).reshape(-1)
    for ax, variable in zip(axes, variables):
        subset = risk_rate_df[risk_rate_df["variable"] == variable].sort_values("risk_rate", ascending=False)
        subset = subset.head(max_categories)
        ax.bar(subset["category"].astype(str), subset["risk_rate"], color="#F58518")
        ax.set_title(variable)
        ax.set_ylabel("Risk rate")
        ax.set_ylim(0, max(0.05, min(1.0, subset["risk_rate"].max() * 1.25)))
        ax.tick_params(axis="x", rotation=30)
    for ax in axes[len(variables) :]:
        ax.axis("off")
    return save_figure(path)


def plot_behavior_outcome_scatter(df: pd.DataFrame, path: Path) -> Path:
    configure_matplotlib()
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    axes = axes.reshape(-1)

    pairs = [
        ("device_hours_per_day", "digital_dependence_score"),
        ("sleep_hours", "productivity_score"),
        ("social_media_mins", "digital_dependence_score"),
    ]
    for ax, (x_col, y_col) in zip(axes[:3], pairs):
        ax.scatter(df[x_col], df[y_col], s=12, alpha=0.45, color="#4C78A8")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"{x_col} vs {y_col}")

    ax = axes[3]
    if {"notifications_per_day", "high_risk_flag"}.issubset(df.columns):
        binned = pd.DataFrame(
            {
                "bin": pd.qcut(df["notifications_per_day"], q=10, duplicates="drop"),
                "high_risk_flag": df["high_risk_flag"],
            }
        )
        rate = binned.groupby("bin", observed=True)["high_risk_flag"].mean().reset_index()
        ax.plot(range(len(rate)), rate["high_risk_flag"], marker="o", color="#E45756")
        ax.set_xticks(range(len(rate)))
        ax.set_xticklabels([str(item) for item in rate["bin"]], rotation=45, ha="right")
        ax.set_xlabel("notifications_per_day bins")
        ax.set_ylabel("Mean high_risk_flag")
        ax.set_title("Notifications vs High-Risk Rate")
    return save_figure(path)


def figure_path(filename: str) -> Path:
    return FIGURES_DIR / filename
