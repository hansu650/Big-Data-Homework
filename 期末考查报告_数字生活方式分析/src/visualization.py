from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import RocCurveDisplay

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
    plt.title("Best Classification Model ROC Curve")
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
    plt.xlabel("Observed productivity_score")
    plt.ylabel("Predicted productivity_score")
    plt.title("Observed vs Predicted Productivity")
    return save_figure(path)


def plot_regression_residuals(y_true: pd.Series, y_pred: np.ndarray, path: Path) -> Path:
    configure_matplotlib()
    residuals = y_true - y_pred
    plt.figure(figsize=(6, 4))
    plt.scatter(y_pred, residuals, s=18, alpha=0.65, color="#72B7B2")
    plt.axhline(0, color="#E45756", linewidth=1.5)
    plt.xlabel("Predicted productivity_score")
    plt.ylabel("Residual")
    plt.title("Regression Residual Plot")
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


def figure_path(filename: str) -> Path:
    return FIGURES_DIR / filename

