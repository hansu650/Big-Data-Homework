from __future__ import annotations

import shutil
import time
import warnings
import zipfile
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    completeness_score,
    davies_bouldin_score,
    homogeneity_score,
    normalized_mutual_info_score,
    silhouette_score,
    v_measure_score,
)
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


RANDOM_STATE = 42
FIGURE_DPI = 300

WINE_COLUMNS = [
    "class",
    "Alcohol",
    "Malic acid",
    "Ash",
    "Alcalinity of ash",
    "Magnesium",
    "Total phenols",
    "Flavanoids",
    "Nonflavanoid phenols",
    "Proanthocyanins",
    "Color intensity",
    "Hue",
    "OD280/OD315 of diluted wines",
    "Proline",
]
FEATURE_COLUMNS = WINE_COLUMNS[1:]

KMEANS_K_VALUES = list(range(2, 11))
AGGLOMERATIVE_LINKAGES = ["ward", "complete", "average", "single"]
DBSCAN_EPS_VALUES = np.round(np.arange(0.3, 5.01, 0.1), 2)
DBSCAN_MIN_SAMPLES_VALUES = [3, 4, 5, 6, 8, 10]
DBSCAN_REASONABLE_NOISE_RATIO = 0.40

REQUIRED_RESULT_FILES = [
    "data_basic_info.csv",
    "feature_descriptive_statistics.csv",
    "missing_duplicate_check.csv",
    "kmeans_k_selection_results.csv",
    "agglomerative_grid_results.csv",
    "dbscan_grid_search_results.csv",
    "final_model_comparison.csv",
    "model_ranking_summary.csv",
    "cluster_profile_summary.csv",
    "cluster_profile_scaled_mean.csv",
    "cluster_profile_interpretation.txt",
    "final_cluster_assignments.csv",
    "optional_external_label_comparison.csv",
    "optional_kmeans_class_crosstab.csv",
    "optional_agglomerative_class_crosstab.csv",
    "optional_dbscan_class_crosstab.csv",
]

REQUIRED_FIGURE_FILES = [
    "01_feature_boxplots_before_scaling.png",
    "02_feature_boxplots_after_scaling.png",
    "03_feature_correlation_heatmap.png",
    "04_pca_original_labels_optional.png",
    "05_kmeans_elbow_curve.png",
    "06_kmeans_silhouette_by_k.png",
    "07_kmeans_ch_by_k.png",
    "08_kmeans_db_by_k.png",
    "09_pca_kmeans_k3_clusters.png",
    "10_pca_best_kmeans_clusters.png",
    "11_agglomerative_silhouette_comparison.png",
    "12_agglomerative_ch_comparison.png",
    "13_agglomerative_db_comparison.png",
    "14_agglomerative_dendrogram.png",
    "15_pca_agglomerative_ward_k3_clusters.png",
    "16_dbscan_k_distance_curve.png",
    "17_dbscan_silhouette_heatmap.png",
    "18_dbscan_noise_ratio_heatmap.png",
    "19_dbscan_cluster_count_heatmap.png",
    "20_pca_best_dbscan_clusters.png",
    "21_final_model_metrics_comparison.png",
    "22_cluster_size_comparison.png",
    "23_cluster_profile_heatmap.png",
    "24_optional_external_metric_comparison.png",
]


def resolve_paths(exp4_dir: str | Path | None = None) -> dict[str, Path]:
    """Resolve paths so the script works from the repo root or Experiment 4."""
    if exp4_dir is None:
        exp4_dir = Path(__file__).resolve().parent
    else:
        exp4_dir = Path(exp4_dir).resolve()
        if exp4_dir.name != "实验四" and (exp4_dir / "实验四").exists():
            exp4_dir = exp4_dir / "实验四"

    project_root = exp4_dir.parent
    data_dir = exp4_dir / "data"
    return {
        "project_root": project_root,
        "exp4_dir": exp4_dir,
        "data_dir": data_dir,
        "results_dir": exp4_dir / "results",
        "figures_dir": exp4_dir / "figures",
        "wine_data": data_dir / "wine.data",
        "wine_names": data_dir / "wine.names",
        "wine_index": data_dir / "Index",
    }


def ensure_output_dirs(paths: dict[str, Path]) -> None:
    paths["data_dir"].mkdir(parents=True, exist_ok=True)
    paths["results_dir"].mkdir(parents=True, exist_ok=True)
    paths["figures_dir"].mkdir(parents=True, exist_ok=True)


def extract_wine_zip_if_needed(paths: dict[str, Path]) -> Path | None:
    """Extract wine.data, wine.names, and Index from wine.zip when needed."""
    if paths["wine_data"].exists():
        return None

    zip_candidates = [
        paths["data_dir"] / "wine.zip",
        paths["exp4_dir"] / "wine.zip",
        paths["project_root"] / "wine.zip",
    ]
    allowed_names = {"wine.data", "wine.names", "Index"}

    for zip_path in zip_candidates:
        if not zip_path.exists():
            continue

        with zipfile.ZipFile(zip_path) as archive:
            for member in archive.infolist():
                member_name = Path(member.filename).name
                if member.is_dir() or member_name not in allowed_names:
                    continue
                target_path = paths["data_dir"] / member_name
                with archive.open(member) as source, target_path.open("wb") as target:
                    shutil.copyfileobj(source, target)

        if paths["wine_data"].exists():
            return zip_path

    return None


def check_wine_data(paths: dict[str, Path]) -> None:
    extract_wine_zip_if_needed(paths)
    if not paths["wine_data"].exists():
        raise FileNotFoundError(
            "wine.data was not found. Please put the file at "
            f"{paths['wine_data']}.\n"
            "If you have wine.zip, place it in the repository root, "
            "Experiment 4 directory, or Experiment 4/data, then run again."
        )


def load_wine_data(paths: dict[str, Path]) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    """Load wine.data and remove the class label from the clustering features."""
    check_wine_data(paths)

    df = pd.read_csv(paths["wine_data"], header=None)
    if df.shape[1] != len(WINE_COLUMNS):
        raise ValueError(
            f"Expected {len(WINE_COLUMNS)} columns in wine.data, got {df.shape[1]}."
        )

    df.columns = WINE_COLUMNS
    df = df.apply(pd.to_numeric, errors="coerce")

    y_true_optional = df["class"].copy()
    X = df.drop(columns=["class"]).copy()

    if "class" in X.columns:
        raise RuntimeError("The class label was not removed from X.")

    return df, X, y_true_optional


def standardize_and_project(
    X: pd.DataFrame,
) -> tuple[StandardScaler, pd.DataFrame, pd.DataFrame, PCA]:
    """Standardize feature matrix and build a two-dimensional PCA view."""
    scaler = StandardScaler()
    X_scaled_array = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled_array, columns=X.columns, index=X.index)

    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    X_pca_2d = pca.fit_transform(X_scaled)
    X_pca_2d = pd.DataFrame(X_pca_2d, columns=["PC1", "PC2"], index=X.index)

    return scaler, X_scaled, X_pca_2d, pca


def save_data_check_outputs(
    df: pd.DataFrame,
    X: pd.DataFrame,
    y_true_optional: pd.Series,
    X_scaled: pd.DataFrame,
    paths: dict[str, Path],
) -> list[Path]:
    """Save shape, missing value, duplicate, dtype, and feature statistics."""
    class_distribution = y_true_optional.value_counts().sort_index()

    info_rows = [
        {"item": "dataset_file", "value": str(paths["wine_data"])},
        {"item": "n_samples", "value": len(df)},
        {"item": "n_original_columns", "value": df.shape[1]},
        {"item": "n_features_used_for_clustering", "value": X.shape[1]},
        {"item": "removed_label_column", "value": "class"},
        {
            "item": "feature_columns_used_for_clustering",
            "value": "; ".join(X.columns),
        },
        {
            "item": "optional_original_class_distribution_note",
            "value": (
                "Original class labels are optional information only and are not "
                "used for clustering training, parameter selection, or main evaluation."
            ),
        },
    ]
    for label, count in class_distribution.items():
        info_rows.append(
            {
                "item": f"optional_original_class_{int(label)}_count",
                "value": int(count),
            }
        )
    for column, dtype in df.dtypes.items():
        info_rows.append({"item": f"dtype_{column}", "value": str(dtype)})

    data_basic_info = pd.DataFrame(info_rows)
    data_basic_info_path = paths["results_dir"] / "data_basic_info.csv"
    data_basic_info.to_csv(data_basic_info_path, index=False)

    missing_rows = [
        {"item": "total_missing_values_in_original_data", "value": int(df.isna().sum().sum())},
        {"item": "total_missing_values_in_X", "value": int(X.isna().sum().sum())},
        {"item": "duplicate_rows_in_original_data", "value": int(df.duplicated().sum())},
        {"item": "duplicate_rows_in_X", "value": int(X.duplicated().sum())},
    ]
    for column in df.columns:
        missing_rows.append(
            {"item": f"missing_values_{column}", "value": int(df[column].isna().sum())}
        )
    missing_duplicate_check = pd.DataFrame(missing_rows)
    missing_duplicate_path = paths["results_dir"] / "missing_duplicate_check.csv"
    missing_duplicate_check.to_csv(missing_duplicate_path, index=False)

    before_stats = X.describe().T.reset_index().rename(columns={"index": "feature"})
    before_stats.insert(0, "data_version", "before_scaling")
    after_stats = X_scaled.describe().T.reset_index().rename(columns={"index": "feature"})
    after_stats.insert(0, "data_version", "after_scaling")
    descriptive_statistics = pd.concat([before_stats, after_stats], ignore_index=True)
    descriptive_statistics_path = paths["results_dir"] / "feature_descriptive_statistics.csv"
    descriptive_statistics.to_csv(descriptive_statistics_path, index=False)

    return [
        data_basic_info_path,
        descriptive_statistics_path,
        missing_duplicate_path,
    ]


def save_figure(fig: plt.Figure, output_path: Path) -> Path:
    fig.tight_layout()
    fig.savefig(output_path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_feature_boxplots(
    frame: pd.DataFrame,
    title: str,
    ylabel: str,
    output_path: Path,
) -> Path:
    fig, ax = plt.subplots(figsize=(11, 6))
    box = ax.boxplot(
        frame.to_numpy(),
        labels=frame.columns,
        patch_artist=True,
        showfliers=False,
    )
    for patch in box["boxes"]:
        patch.set_facecolor("#7AA6C2")
        patch.set_alpha(0.75)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", labelrotation=70, labelsize=8)
    ax.grid(axis="y", alpha=0.25)
    return save_figure(fig, output_path)


def plot_feature_correlation_heatmap(X: pd.DataFrame, paths: dict[str, Path]) -> Path:
    correlation = X.corr(numeric_only=True)

    fig, ax = plt.subplots(figsize=(9, 7.5))
    image = ax.imshow(correlation, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_title("Feature Correlation Heatmap")
    ax.set_xticks(np.arange(len(correlation.columns)))
    ax.set_yticks(np.arange(len(correlation.index)))
    ax.set_xticklabels(correlation.columns, rotation=70, ha="right", fontsize=7)
    ax.set_yticklabels(correlation.index, fontsize=7)
    cbar = fig.colorbar(image, ax=ax, shrink=0.85)
    cbar.set_label("Correlation")

    return save_figure(
        fig,
        paths["figures_dir"] / "03_feature_correlation_heatmap.png",
    )


def plot_pca_labels(
    X_pca_2d: pd.DataFrame,
    labels: np.ndarray | pd.Series,
    title: str,
    output_path: Path,
    xlabel: str = "Principal Component 1",
    ylabel: str = "Principal Component 2",
) -> Path:
    fig, ax = plt.subplots(figsize=(7.5, 5.8))
    label_series = pd.Series(labels, index=X_pca_2d.index, name="label")
    unique_labels = sorted(label_series.dropna().unique())
    cmap = plt.get_cmap("tab10")

    for index, label in enumerate(unique_labels):
        mask = label_series == label
        display_label = "Noise" if int(label) == -1 else f"Cluster {int(label)}"
        if "original" in output_path.name:
            display_label = f"Class {int(label)}"
        color = "#808080" if int(label) == -1 else cmap(index % 10)
        ax.scatter(
            X_pca_2d.loc[mask, "PC1"],
            X_pca_2d.loc[mask, "PC2"],
            s=38,
            alpha=0.82,
            label=display_label,
            color=color,
            edgecolors="white",
            linewidths=0.35,
        )

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.2)
    ax.legend(loc="best", fontsize=8, frameon=True)
    return save_figure(fig, output_path)


def plot_data_overview_figures(
    X: pd.DataFrame,
    X_scaled: pd.DataFrame,
    X_pca_2d: pd.DataFrame,
    y_true_optional: pd.Series,
    paths: dict[str, Path],
) -> list[Path]:
    figure_paths = [
        plot_feature_boxplots(
            X,
            "Feature Boxplots Before Scaling",
            "Original Feature Value",
            paths["figures_dir"] / "01_feature_boxplots_before_scaling.png",
        ),
        plot_feature_boxplots(
            X_scaled,
            "Feature Boxplots After Standard Scaling",
            "Standardized Feature Value",
            paths["figures_dir"] / "02_feature_boxplots_after_scaling.png",
        ),
        plot_feature_correlation_heatmap(X, paths),
        plot_pca_labels(
            X_pca_2d,
            y_true_optional,
            "PCA Projection Colored by Original Labels (Optional)",
            paths["figures_dir"] / "04_pca_original_labels_optional.png",
        ),
    ]
    return figure_paths


def prepare_data(paths: dict[str, Path]) -> dict[str, Any]:
    """Read data, remove class labels, standardize features, and save checks."""
    ensure_output_dirs(paths)
    df, X, y_true_optional = load_wine_data(paths)
    scaler, X_scaled, X_pca_2d, pca = standardize_and_project(X)

    result_paths = save_data_check_outputs(df, X, y_true_optional, X_scaled, paths)
    figure_paths = plot_data_overview_figures(
        X,
        X_scaled,
        X_pca_2d,
        y_true_optional,
        paths,
    )

    return {
        "data": {
            "df": df,
            "X": X,
            "y_true_optional": y_true_optional,
            "scaler": scaler,
            "X_scaled": X_scaled,
            "X_pca_2d": X_pca_2d,
            "pca": pca,
        },
        "result_paths": result_paths,
        "figure_paths": figure_paths,
    }


def format_cluster_size_summary(labels: np.ndarray) -> str:
    counts = pd.Series(labels).value_counts().sort_index()
    return "; ".join(f"{int(cluster)}:{int(count)}" for cluster, count in counts.items())


def count_clusters_excluding_noise(labels: np.ndarray) -> int:
    return len([label for label in np.unique(labels) if int(label) != -1])


def compute_internal_metrics(
    X_scaled_array: np.ndarray,
    labels: np.ndarray,
    exclude_noise: bool = False,
) -> dict[str, float]:
    """Compute internal clustering metrics; optionally ignore DBSCAN noise."""
    labels = np.asarray(labels)
    if exclude_noise:
        mask = labels != -1
        X_eval = X_scaled_array[mask]
        labels_eval = labels[mask]
    else:
        X_eval = X_scaled_array
        labels_eval = labels

    unique_labels = np.unique(labels_eval)
    if len(unique_labels) < 2 or len(unique_labels) >= len(labels_eval):
        return {
            "silhouette_score": np.nan,
            "calinski_harabasz_score": np.nan,
            "davies_bouldin_score": np.nan,
        }

    return {
        "silhouette_score": float(silhouette_score(X_eval, labels_eval)),
        "calinski_harabasz_score": float(calinski_harabasz_score(X_eval, labels_eval)),
        "davies_bouldin_score": float(davies_bouldin_score(X_eval, labels_eval)),
    }


def select_best_by_internal_metrics(
    results_df: pd.DataFrame,
    extra_sort_columns: list[str] | None = None,
) -> pd.Series:
    sort_columns = [
        "silhouette_score",
        "calinski_harabasz_score",
        "davies_bouldin_score",
    ]
    ascending = [False, False, True]
    if extra_sort_columns:
        sort_columns.extend(extra_sort_columns)
        ascending.extend([True] * len(extra_sort_columns))

    valid_df = results_df.dropna(subset=["silhouette_score"]).copy()
    if valid_df.empty:
        raise ValueError("No valid clustering result is available for model selection.")

    return valid_df.sort_values(sort_columns, ascending=ascending).iloc[0]


def plot_single_metric_by_k(
    results_df: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    output_path: Path,
) -> Path:
    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.plot(
        results_df["n_clusters"],
        results_df[metric],
        marker="o",
        linewidth=2,
        color="#4C78A8",
    )
    ax.set_title(title)
    ax.set_xlabel("Number of Clusters (k)")
    ax.set_ylabel(ylabel)
    ax.set_xticks(results_df["n_clusters"])
    ax.grid(alpha=0.25)
    return save_figure(fig, output_path)


def run_kmeans_experiment(data: dict[str, Any], paths: dict[str, Path]) -> dict[str, Any]:
    X_scaled_array = data["X_scaled"].to_numpy()
    labels_by_k: dict[int, np.ndarray] = {}
    records = []

    for k in KMEANS_K_VALUES:
        model = KMeans(n_clusters=k, n_init=50, random_state=RANDOM_STATE)
        start_time = time.perf_counter()
        labels = model.fit_predict(X_scaled_array)
        elapsed = time.perf_counter() - start_time

        labels_by_k[k] = labels
        metrics = compute_internal_metrics(X_scaled_array, labels)
        records.append(
            {
                "model": "KMeans",
                "n_clusters": k,
                "inertia": float(model.inertia_),
                **metrics,
                "training_time_seconds": elapsed,
                "cluster_size_summary": format_cluster_size_summary(labels),
            }
        )

    results_df = pd.DataFrame(records)
    result_path = paths["results_dir"] / "kmeans_k_selection_results.csv"
    results_df.to_csv(result_path, index=False)

    best_row = select_best_by_internal_metrics(results_df)
    best_k = int(best_row["n_clusters"])

    figure_paths = [
        plot_single_metric_by_k(
            results_df,
            "inertia",
            "KMeans Elbow Curve",
            "Inertia",
            paths["figures_dir"] / "05_kmeans_elbow_curve.png",
        ),
        plot_single_metric_by_k(
            results_df,
            "silhouette_score",
            "KMeans Silhouette Score by k",
            "Silhouette Coefficient",
            paths["figures_dir"] / "06_kmeans_silhouette_by_k.png",
        ),
        plot_single_metric_by_k(
            results_df,
            "calinski_harabasz_score",
            "KMeans Calinski-Harabasz Index by k",
            "Calinski-Harabasz Index",
            paths["figures_dir"] / "07_kmeans_ch_by_k.png",
        ),
        plot_single_metric_by_k(
            results_df,
            "davies_bouldin_score",
            "KMeans Davies-Bouldin Index by k",
            "Davies-Bouldin Index",
            paths["figures_dir"] / "08_kmeans_db_by_k.png",
        ),
        plot_pca_labels(
            data["X_pca_2d"],
            labels_by_k[3],
            "PCA Projection of KMeans Clusters (k=3)",
            paths["figures_dir"] / "09_pca_kmeans_k3_clusters.png",
        ),
        plot_pca_labels(
            data["X_pca_2d"],
            labels_by_k[best_k],
            f"PCA Projection of Best KMeans Clusters (k={best_k})",
            paths["figures_dir"] / "10_pca_best_kmeans_clusters.png",
        ),
    ]

    return {
        "results": results_df,
        "labels_by_k": labels_by_k,
        "best_k": best_k,
        "best_row": best_row,
        "k3_labels": labels_by_k[3],
        "best_labels": labels_by_k[best_k],
        "result_paths": [result_path],
        "figure_paths": figure_paths,
    }


def plot_agglomerative_metric_comparison(
    results_df: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    output_path: Path,
) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5.5))
    for linkage in AGGLOMERATIVE_LINKAGES:
        subset = results_df[results_df["linkage"] == linkage]
        ax.plot(
            subset["n_clusters"],
            subset[metric],
            marker="o",
            linewidth=2,
            label=linkage,
        )
    ax.set_title(title)
    ax.set_xlabel("Number of Clusters (k)")
    ax.set_ylabel(ylabel)
    ax.set_xticks(KMEANS_K_VALUES)
    ax.grid(alpha=0.25)
    ax.legend(title="Linkage")
    return save_figure(fig, output_path)


def plot_agglomerative_dendrogram(data: dict[str, Any], paths: dict[str, Path]) -> Path:
    from scipy.cluster.hierarchy import dendrogram, linkage

    linked = linkage(data["X_scaled"].to_numpy(), method="ward")

    fig, ax = plt.subplots(figsize=(10, 5.5))
    dendrogram(
        linked,
        truncate_mode="level",
        p=5,
        no_labels=True,
        color_threshold=None,
        ax=ax,
    )
    ax.set_title("Agglomerative Clustering Dendrogram (Ward Linkage)")
    ax.set_xlabel("Samples")
    ax.set_ylabel("Distance")
    ax.grid(axis="y", alpha=0.2)
    return save_figure(fig, paths["figures_dir"] / "14_agglomerative_dendrogram.png")


def run_agglomerative_experiment(
    data: dict[str, Any],
    paths: dict[str, Path],
) -> dict[str, Any]:
    X_scaled_array = data["X_scaled"].to_numpy()
    labels_by_setting: dict[tuple[str, int], np.ndarray] = {}
    records = []

    for linkage in AGGLOMERATIVE_LINKAGES:
        for k in KMEANS_K_VALUES:
            model = AgglomerativeClustering(n_clusters=k, linkage=linkage)
            start_time = time.perf_counter()
            labels = model.fit_predict(X_scaled_array)
            elapsed = time.perf_counter() - start_time

            labels_by_setting[(linkage, k)] = labels
            metrics = compute_internal_metrics(X_scaled_array, labels)
            records.append(
                {
                    "model": "AgglomerativeClustering",
                    "linkage": linkage,
                    "n_clusters": k,
                    **metrics,
                    "training_time_seconds": elapsed,
                    "cluster_size_summary": format_cluster_size_summary(labels),
                }
            )

    results_df = pd.DataFrame(records)
    result_path = paths["results_dir"] / "agglomerative_grid_results.csv"
    results_df.to_csv(result_path, index=False)

    best_row = select_best_by_internal_metrics(results_df)
    best_linkage = str(best_row["linkage"])
    best_k = int(best_row["n_clusters"])

    figure_paths = [
        plot_agglomerative_metric_comparison(
            results_df,
            "silhouette_score",
            "Agglomerative Silhouette Score Comparison",
            "Silhouette Coefficient",
            paths["figures_dir"] / "11_agglomerative_silhouette_comparison.png",
        ),
        plot_agglomerative_metric_comparison(
            results_df,
            "calinski_harabasz_score",
            "Agglomerative Calinski-Harabasz Index Comparison",
            "Calinski-Harabasz Index",
            paths["figures_dir"] / "12_agglomerative_ch_comparison.png",
        ),
        plot_agglomerative_metric_comparison(
            results_df,
            "davies_bouldin_score",
            "Agglomerative Davies-Bouldin Index Comparison",
            "Davies-Bouldin Index",
            paths["figures_dir"] / "13_agglomerative_db_comparison.png",
        ),
        plot_agglomerative_dendrogram(data, paths),
        plot_pca_labels(
            data["X_pca_2d"],
            labels_by_setting[("ward", 3)],
            "PCA Projection of Agglomerative Clusters (Ward, k=3)",
            paths["figures_dir"] / "15_pca_agglomerative_ward_k3_clusters.png",
        ),
    ]

    return {
        "results": results_df,
        "labels_by_setting": labels_by_setting,
        "best_linkage": best_linkage,
        "best_k": best_k,
        "best_row": best_row,
        "ward_k3_labels": labels_by_setting[("ward", 3)],
        "best_labels": labels_by_setting[(best_linkage, best_k)],
        "result_paths": [result_path],
        "figure_paths": figure_paths,
    }


def plot_dbscan_k_distance_curve(data: dict[str, Any], paths: dict[str, Path]) -> Path:
    neighbors = NearestNeighbors(n_neighbors=5)
    neighbors.fit(data["X_scaled"].to_numpy())
    distances, _ = neighbors.kneighbors(data["X_scaled"].to_numpy())
    kth_distances = np.sort(distances[:, -1])

    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.plot(np.arange(1, len(kth_distances) + 1), kth_distances, color="#4C78A8")
    ax.set_title("DBSCAN k-Distance Curve (5th Nearest Neighbor)")
    ax.set_xlabel("Samples Sorted by Distance")
    ax.set_ylabel("5th Nearest Neighbor Distance")
    ax.grid(alpha=0.25)
    return save_figure(fig, paths["figures_dir"] / "16_dbscan_k_distance_curve.png")


def plot_dbscan_heatmap(
    results_df: pd.DataFrame,
    value_column: str,
    title: str,
    colorbar_label: str,
    output_path: Path,
    cmap_name: str = "viridis",
) -> Path:
    pivot = results_df.pivot(
        index="min_samples",
        columns="eps",
        values=value_column,
    ).sort_index()
    matrix = pivot.to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=(10, 4.8))
    cmap = plt.get_cmap(cmap_name).copy()
    cmap.set_bad("#EFEFEF")
    image = ax.imshow(matrix, aspect="auto", cmap=cmap, origin="lower")

    x_positions = np.arange(len(pivot.columns))
    shown_x_positions = x_positions[::5]
    if x_positions[-1] not in shown_x_positions:
        shown_x_positions = np.append(shown_x_positions, x_positions[-1])
    ax.set_xticks(shown_x_positions)
    ax.set_xticklabels([f"{pivot.columns[i]:.1f}" for i in shown_x_positions])
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels([str(value) for value in pivot.index])
    ax.set_title(title)
    ax.set_xlabel("eps")
    ax.set_ylabel("min_samples")
    cbar = fig.colorbar(image, ax=ax, shrink=0.9)
    cbar.set_label(colorbar_label)
    return save_figure(fig, output_path)


def select_best_dbscan(results_df: pd.DataFrame) -> pd.Series:
    valid_df = results_df.dropna(subset=["silhouette_score"]).copy()
    reasonable_df = valid_df[
        valid_df["noise_ratio"] <= DBSCAN_REASONABLE_NOISE_RATIO
    ].copy()
    selection_df = reasonable_df if not reasonable_df.empty else valid_df

    if selection_df.empty:
        return results_df.sort_values(
            ["cluster_count_excluding_noise", "noise_ratio"],
            ascending=[False, True],
        ).iloc[0]

    return selection_df.sort_values(
        [
            "silhouette_score",
            "calinski_harabasz_score",
            "davies_bouldin_score",
            "noise_ratio",
        ],
        ascending=[False, False, True, True],
    ).iloc[0]


def run_dbscan_experiment(data: dict[str, Any], paths: dict[str, Path]) -> dict[str, Any]:
    X_scaled_array = data["X_scaled"].to_numpy()
    labels_by_setting: dict[tuple[float, int], np.ndarray] = {}
    records = []

    for eps in DBSCAN_EPS_VALUES:
        for min_samples in DBSCAN_MIN_SAMPLES_VALUES:
            model = DBSCAN(eps=float(eps), min_samples=int(min_samples))
            start_time = time.perf_counter()
            labels = model.fit_predict(X_scaled_array)
            elapsed = time.perf_counter() - start_time

            cluster_count = count_clusters_excluding_noise(labels)
            noise_count = int(np.sum(labels == -1))
            noise_ratio = noise_count / len(labels)

            if cluster_count < 2:
                metrics = {
                    "silhouette_score": np.nan,
                    "calinski_harabasz_score": np.nan,
                    "davies_bouldin_score": np.nan,
                }
            else:
                metrics = compute_internal_metrics(
                    X_scaled_array,
                    labels,
                    exclude_noise=True,
                )

            labels_by_setting[(float(eps), int(min_samples))] = labels
            records.append(
                {
                    "model": "DBSCAN",
                    "eps": float(eps),
                    "min_samples": int(min_samples),
                    "cluster_count_excluding_noise": cluster_count,
                    "noise_count": noise_count,
                    "noise_ratio": noise_ratio,
                    **metrics,
                    "training_time_seconds": elapsed,
                }
            )

    results_df = pd.DataFrame(records)
    result_path = paths["results_dir"] / "dbscan_grid_search_results.csv"
    results_df.to_csv(result_path, index=False)

    best_row = select_best_dbscan(results_df)
    best_eps = float(best_row["eps"])
    best_min_samples = int(best_row["min_samples"])

    figure_paths = [
        plot_dbscan_k_distance_curve(data, paths),
        plot_dbscan_heatmap(
            results_df,
            "silhouette_score",
            "DBSCAN Silhouette Score Heatmap",
            "Silhouette Coefficient",
            paths["figures_dir"] / "17_dbscan_silhouette_heatmap.png",
        ),
        plot_dbscan_heatmap(
            results_df,
            "noise_ratio",
            "DBSCAN Noise Ratio Heatmap",
            "Noise Ratio",
            paths["figures_dir"] / "18_dbscan_noise_ratio_heatmap.png",
            cmap_name="magma",
        ),
        plot_dbscan_heatmap(
            results_df,
            "cluster_count_excluding_noise",
            "DBSCAN Cluster Count Heatmap",
            "Cluster Count Excluding Noise",
            paths["figures_dir"] / "19_dbscan_cluster_count_heatmap.png",
            cmap_name="plasma",
        ),
        plot_pca_labels(
            data["X_pca_2d"],
            labels_by_setting[(best_eps, best_min_samples)],
            f"PCA Projection of Best DBSCAN Clusters (eps={best_eps:.2f}, min_samples={best_min_samples})",
            paths["figures_dir"] / "20_pca_best_dbscan_clusters.png",
        ),
    ]

    return {
        "results": results_df,
        "labels_by_setting": labels_by_setting,
        "best_eps": best_eps,
        "best_min_samples": best_min_samples,
        "best_row": best_row,
        "best_labels": labels_by_setting[(best_eps, best_min_samples)],
        "result_paths": [result_path],
        "figure_paths": figure_paths,
    }


def make_final_model_comparison(
    kmeans_outputs: dict[str, Any],
    agglomerative_outputs: dict[str, Any],
    dbscan_outputs: dict[str, Any],
) -> pd.DataFrame:
    kmeans_results = kmeans_outputs["results"]
    agglomerative_results = agglomerative_outputs["results"]
    dbscan_best = dbscan_outputs["best_row"]

    kmeans_k3 = kmeans_results[kmeans_results["n_clusters"] == 3].iloc[0]
    best_kmeans = kmeans_outputs["best_row"]
    agglomerative_ward_k3 = agglomerative_results[
        (agglomerative_results["linkage"] == "ward")
        & (agglomerative_results["n_clusters"] == 3)
    ].iloc[0]
    best_agglomerative = agglomerative_outputs["best_row"]

    rows = [
        {
            "model": "KMeans",
            "setting": "k=3",
            "n_clusters": int(kmeans_k3["n_clusters"]),
            "noise_ratio": 0.0,
            "silhouette_score": kmeans_k3["silhouette_score"],
            "calinski_harabasz_score": kmeans_k3["calinski_harabasz_score"],
            "davies_bouldin_score": kmeans_k3["davies_bouldin_score"],
            "training_time_seconds": kmeans_k3["training_time_seconds"],
            "notes": "Fixed k=3 retained for cluster interpretation.",
        },
        {
            "model": "KMeans",
            "setting": f"best by silhouette, k={int(best_kmeans['n_clusters'])}",
            "n_clusters": int(best_kmeans["n_clusters"]),
            "noise_ratio": 0.0,
            "silhouette_score": best_kmeans["silhouette_score"],
            "calinski_harabasz_score": best_kmeans["calinski_harabasz_score"],
            "davies_bouldin_score": best_kmeans["davies_bouldin_score"],
            "training_time_seconds": best_kmeans["training_time_seconds"],
            "notes": "Selected by internal clustering metrics only.",
        },
        {
            "model": "AgglomerativeClustering",
            "setting": "linkage=ward, k=3",
            "n_clusters": int(agglomerative_ward_k3["n_clusters"]),
            "noise_ratio": 0.0,
            "silhouette_score": agglomerative_ward_k3["silhouette_score"],
            "calinski_harabasz_score": agglomerative_ward_k3[
                "calinski_harabasz_score"
            ],
            "davies_bouldin_score": agglomerative_ward_k3["davies_bouldin_score"],
            "training_time_seconds": agglomerative_ward_k3["training_time_seconds"],
            "notes": "Ward linkage with k=3 retained as a hierarchical baseline.",
        },
        {
            "model": "AgglomerativeClustering",
            "setting": (
                "best by silhouette, "
                f"linkage={best_agglomerative['linkage']}, "
                f"k={int(best_agglomerative['n_clusters'])}"
            ),
            "n_clusters": int(best_agglomerative["n_clusters"]),
            "noise_ratio": 0.0,
            "silhouette_score": best_agglomerative["silhouette_score"],
            "calinski_harabasz_score": best_agglomerative[
                "calinski_harabasz_score"
            ],
            "davies_bouldin_score": best_agglomerative["davies_bouldin_score"],
            "training_time_seconds": best_agglomerative["training_time_seconds"],
            "notes": "Selected by internal clustering metrics only.",
        },
        {
            "model": "DBSCAN",
            "setting": (
                f"eps={float(dbscan_best['eps']):.2f}, "
                f"min_samples={int(dbscan_best['min_samples'])}"
            ),
            "n_clusters": int(dbscan_best["cluster_count_excluding_noise"]),
            "noise_ratio": float(dbscan_best["noise_ratio"]),
            "silhouette_score": dbscan_best["silhouette_score"],
            "calinski_harabasz_score": dbscan_best["calinski_harabasz_score"],
            "davies_bouldin_score": dbscan_best["davies_bouldin_score"],
            "training_time_seconds": dbscan_best["training_time_seconds"],
            "notes": (
                "Best valid DBSCAN setting; noise ratio is considered because "
                "DBSCAN is sensitive to eps and min_samples."
            ),
        },
    ]
    final_df = pd.DataFrame(rows)
    return sort_final_models(final_df)


def sort_final_models(final_df: pd.DataFrame) -> pd.DataFrame:
    working_df = final_df.copy()
    dbscan_high_noise = (
        (working_df["model"] == "DBSCAN")
        & (working_df["noise_ratio"] > DBSCAN_REASONABLE_NOISE_RATIO)
    )
    working_df["_recommendation_candidate"] = ~dbscan_high_noise
    working_df["_silhouette_sort"] = working_df["silhouette_score"].fillna(-np.inf)
    working_df["_ch_sort"] = working_df["calinski_harabasz_score"].fillna(-np.inf)
    working_df["_db_sort"] = working_df["davies_bouldin_score"].fillna(np.inf)

    sorted_df = working_df.sort_values(
        [
            "_recommendation_candidate",
            "_silhouette_sort",
            "_ch_sort",
            "_db_sort",
            "noise_ratio",
        ],
        ascending=[False, False, False, True, True],
    )
    return sorted_df[final_df.columns].reset_index(drop=True)


def make_model_ranking_summary(final_df: pd.DataFrame) -> pd.DataFrame:
    ranking_df = final_df.copy()
    ranking_df.insert(0, "rank", np.arange(1, len(ranking_df) + 1))
    ranking_df["recommendation_candidate"] = ~(
        (ranking_df["model"] == "DBSCAN")
        & (ranking_df["noise_ratio"] > DBSCAN_REASONABLE_NOISE_RATIO)
    )
    ranking_df["ranking_rule"] = (
        "Prefer higher Silhouette, then higher Calinski-Harabasz, then lower "
        "Davies-Bouldin. DBSCAN settings with high noise ratio are not preferred."
    )
    ranking_df["recommended"] = ranking_df["rank"] == 1
    return ranking_df


def save_final_cluster_assignments(
    kmeans_outputs: dict[str, Any],
    agglomerative_outputs: dict[str, Any],
    dbscan_outputs: dict[str, Any],
    paths: dict[str, Path],
) -> Path:
    n_samples = len(kmeans_outputs["k3_labels"])
    assignments = pd.DataFrame(
        {
            "sample_id": np.arange(1, n_samples + 1),
            "kmeans_k3_cluster": kmeans_outputs["k3_labels"],
            "best_kmeans_cluster": kmeans_outputs["best_labels"],
            "agglomerative_ward_k3_cluster": agglomerative_outputs["ward_k3_labels"],
            "best_agglomerative_cluster": agglomerative_outputs["best_labels"],
            "best_dbscan_cluster": dbscan_outputs["best_labels"],
        }
    )
    output_path = paths["results_dir"] / "final_cluster_assignments.csv"
    assignments.to_csv(output_path, index=False)
    return output_path


def save_cluster_profiles(
    data: dict[str, Any],
    kmeans_outputs: dict[str, Any],
    paths: dict[str, Path],
) -> dict[str, Any]:
    labels = kmeans_outputs["k3_labels"]
    X = data["X"]
    X_scaled = data["X_scaled"]

    profile_frame = X.copy()
    profile_frame["cluster"] = labels
    sample_counts = profile_frame.groupby("cluster").size().rename("sample_count")
    original_means = profile_frame.groupby("cluster")[X.columns].mean()
    profile_summary = pd.concat([sample_counts, original_means], axis=1).reset_index()

    profile_summary_path = paths["results_dir"] / "cluster_profile_summary.csv"
    profile_summary.to_csv(profile_summary_path, index=False)

    scaled_profile_frame = X_scaled.copy()
    scaled_profile_frame["cluster"] = labels
    scaled_means = scaled_profile_frame.groupby("cluster")[X.columns].mean().reset_index()
    scaled_mean_path = paths["results_dir"] / "cluster_profile_scaled_mean.csv"
    scaled_means.to_csv(scaled_mean_path, index=False)

    interpretation_text = build_cluster_profile_interpretation(
        profile_summary,
        scaled_means,
    )
    interpretation_path = paths["results_dir"] / "cluster_profile_interpretation.txt"
    interpretation_path.write_text(interpretation_text, encoding="utf-8")

    heatmap_path = plot_cluster_profile_heatmap(
        scaled_means,
        paths["figures_dir"] / "23_cluster_profile_heatmap.png",
    )

    return {
        "profile_summary": profile_summary,
        "scaled_means": scaled_means,
        "interpretation_text": interpretation_text,
        "result_paths": [
            profile_summary_path,
            scaled_mean_path,
            interpretation_path,
        ],
        "figure_paths": [heatmap_path],
    }


def build_cluster_profile_interpretation(
    profile_summary: pd.DataFrame,
    scaled_means: pd.DataFrame,
) -> str:
    lines = [
        "Cluster profile interpretation based on KMeans k=3.",
        "The values are interpreted from standardized feature means; positive values are above the overall average and negative values are below the overall average.",
    ]
    scaled_indexed = scaled_means.set_index("cluster")
    profile_indexed = profile_summary.set_index("cluster")

    for cluster_id, row in scaled_indexed.iterrows():
        feature_values = row.drop(labels=[], errors="ignore").astype(float)
        high_features = feature_values.sort_values(ascending=False).head(3)
        low_features = feature_values.sort_values(ascending=True).head(3)
        sample_count = int(profile_indexed.loc[cluster_id, "sample_count"])
        high_text = ", ".join(
            f"{feature} ({value:+.2f})" for feature, value in high_features.items()
        )
        low_text = ", ".join(
            f"{feature} ({value:+.2f})" for feature, value in low_features.items()
        )
        lines.append(
            f"Cluster {int(cluster_id)} contains {sample_count} samples. "
            f"It is relatively high in {high_text}, and relatively low in {low_text}."
        )

    return "\n".join(lines)


def plot_cluster_profile_heatmap(scaled_means: pd.DataFrame, output_path: Path) -> Path:
    heatmap_data = scaled_means.set_index("cluster")
    values = heatmap_data.to_numpy(dtype=float)
    max_abs = max(1.0, float(np.nanmax(np.abs(values))))

    fig, ax = plt.subplots(figsize=(11, 4.6))
    image = ax.imshow(values, aspect="auto", cmap="coolwarm", vmin=-max_abs, vmax=max_abs)
    ax.set_title("KMeans k=3 Cluster Profile Heatmap")
    ax.set_xlabel("Feature")
    ax.set_ylabel("Cluster")
    ax.set_xticks(np.arange(len(heatmap_data.columns)))
    ax.set_xticklabels(heatmap_data.columns, rotation=70, ha="right", fontsize=8)
    ax.set_yticks(np.arange(len(heatmap_data.index)))
    ax.set_yticklabels([f"Cluster {int(value)}" for value in heatmap_data.index])
    cbar = fig.colorbar(image, ax=ax, shrink=0.9)
    cbar.set_label("Standardized Mean")
    return save_figure(fig, output_path)


def save_optional_external_label_comparison(
    data: dict[str, Any],
    kmeans_outputs: dict[str, Any],
    agglomerative_outputs: dict[str, Any],
    dbscan_outputs: dict[str, Any],
    paths: dict[str, Path],
) -> list[Path]:
    """Use original labels only after clustering as optional external comparison."""
    y_true_optional = data["y_true_optional"].to_numpy()
    label_sets = {
        "KMeans k=3": kmeans_outputs["k3_labels"],
        "Best KMeans": kmeans_outputs["best_labels"],
        "Agglomerative ward k=3": agglomerative_outputs["ward_k3_labels"],
        "Best Agglomerative": agglomerative_outputs["best_labels"],
        "Best DBSCAN": dbscan_outputs["best_labels"],
    }

    rows = []
    for model_name, labels in label_sets.items():
        rows.append(
            {
                "model": model_name,
                "adjusted_rand_index_optional": adjusted_rand_score(
                    y_true_optional,
                    labels,
                ),
                "normalized_mutual_info_optional": normalized_mutual_info_score(
                    y_true_optional,
                    labels,
                ),
                "homogeneity_optional": homogeneity_score(y_true_optional, labels),
                "completeness_optional": completeness_score(y_true_optional, labels),
                "v_measure_optional": v_measure_score(y_true_optional, labels),
                "note": (
                    "Optional external comparison only; original labels were not "
                    "used in clustering training, parameter selection, or main evaluation."
                ),
            }
        )

    comparison_df = pd.DataFrame(rows)
    comparison_path = paths["results_dir"] / "optional_external_label_comparison.csv"
    comparison_df.to_csv(comparison_path, index=False)

    optional_paths = [comparison_path]
    crosstab_specs = [
        (
            "optional_kmeans_class_crosstab.csv",
            kmeans_outputs["k3_labels"],
        ),
        (
            "optional_agglomerative_class_crosstab.csv",
            agglomerative_outputs["ward_k3_labels"],
        ),
        (
            "optional_dbscan_class_crosstab.csv",
            dbscan_outputs["best_labels"],
        ),
    ]
    for file_name, labels in crosstab_specs:
        crosstab = pd.crosstab(
            pd.Series(labels, name="cluster"),
            pd.Series(y_true_optional, name="class"),
        )
        crosstab_path = paths["results_dir"] / file_name
        crosstab.to_csv(crosstab_path)
        optional_paths.append(crosstab_path)

    return optional_paths


def plot_optional_external_metric_comparison(
    optional_comparison: pd.DataFrame,
    output_path: Path,
) -> Path:
    metric_columns = [
        "adjusted_rand_index_optional",
        "normalized_mutual_info_optional",
        "homogeneity_optional",
        "completeness_optional",
        "v_measure_optional",
    ]
    display_metrics = ["ARI", "NMI", "Homogeneity", "Completeness", "V-measure"]
    model_labels = optional_comparison["model"].tolist()
    x_positions = np.arange(len(model_labels))
    bar_width = 0.15

    fig, ax = plt.subplots(figsize=(10, 5.5))
    for metric_index, metric in enumerate(metric_columns):
        offset = (metric_index - 2) * bar_width
        ax.bar(
            x_positions + offset,
            optional_comparison[metric],
            width=bar_width,
            label=display_metrics[metric_index],
        )

    ax.set_title("Optional External Label Comparison Metrics")
    ax.set_xlabel("Model")
    ax.set_ylabel("Score")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(model_labels, rotation=25, ha="right")
    ax.set_ylim(0, 1.05)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncol=3, fontsize=8)
    return save_figure(fig, output_path)


def plot_final_model_metrics_comparison(
    final_df: pd.DataFrame,
    output_path: Path,
) -> Path:
    model_labels = [
        f"{row.model}\n{row.setting}" for row in final_df.itertuples(index=False)
    ]
    x_positions = np.arange(len(model_labels))

    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    metric_specs = [
        ("silhouette_score", "Silhouette Coefficient", "Higher is better"),
        ("calinski_harabasz_score", "Calinski-Harabasz Index", "Higher is better"),
        ("davies_bouldin_score", "Davies-Bouldin Index", "Lower is better"),
    ]
    colors = ["#4C78A8", "#59A14F", "#F58518"]

    for ax, (metric, ylabel, subtitle), color in zip(axes, metric_specs, colors):
        ax.bar(x_positions, final_df[metric], color=color, alpha=0.85)
        ax.set_ylabel(ylabel)
        ax.set_title(subtitle, fontsize=10)
        ax.grid(axis="y", alpha=0.25)

    axes[0].set_title("Final Model Internal Metrics Comparison", fontsize=13)
    axes[-1].set_xticks(x_positions)
    axes[-1].set_xticklabels(model_labels, rotation=20, ha="right", fontsize=8)
    return save_figure(fig, output_path)


def plot_cluster_size_comparison(
    labels_map: dict[str, np.ndarray],
    output_path: Path,
) -> Path:
    all_cluster_labels = sorted(
        {int(label) for labels in labels_map.values() for label in np.unique(labels)}
    )
    colors = plt.get_cmap("tab20")(np.linspace(0, 1, max(1, len(all_cluster_labels))))
    color_map = {
        cluster_label: colors[index]
        for index, cluster_label in enumerate(all_cluster_labels)
    }

    fig, ax = plt.subplots(figsize=(10, 5.4))
    y_positions = np.arange(len(labels_map))
    for y_position, (model_name, labels) in zip(y_positions, labels_map.items()):
        counts = pd.Series(labels).value_counts().sort_index()
        left = 0
        for cluster_label in all_cluster_labels:
            count = int(counts.get(cluster_label, 0))
            if count == 0:
                continue
            legend_label = "Noise" if cluster_label == -1 else f"Cluster {cluster_label}"
            ax.barh(
                y_position,
                count,
                left=left,
                color=color_map[cluster_label],
                label=legend_label,
            )
            left += count

    handles, labels = ax.get_legend_handles_labels()
    unique_legend = dict(zip(labels, handles))
    ax.set_title("Cluster Size Comparison")
    ax.set_xlabel("Sample Count")
    ax.set_yticks(y_positions)
    ax.set_yticklabels(list(labels_map.keys()))
    ax.grid(axis="x", alpha=0.25)
    ax.legend(
        unique_legend.values(),
        unique_legend.keys(),
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
        fontsize=8,
    )
    return save_figure(fig, output_path)


def build_short_analysis_text(final_df: pd.DataFrame) -> str:
    recommended = final_df.iloc[0]
    dbscan_row = final_df[final_df["model"] == "DBSCAN"]
    dbscan_note = ""
    if not dbscan_row.empty:
        dbscan_noise_ratio = float(dbscan_row.iloc[0]["noise_ratio"])
        dbscan_note = (
            f" The selected DBSCAN setting has a noise ratio of {dbscan_noise_ratio:.2%}, "
            "so DBSCAN sensitivity to eps and min_samples should be discussed."
        )

    return (
        f"Recommended model: {recommended['model']} ({recommended['setting']}). "
        f"It has Silhouette={recommended['silhouette_score']:.4f}, "
        f"Calinski-Harabasz={recommended['calinski_harabasz_score']:.4f}, "
        f"and Davies-Bouldin={recommended['davies_bouldin_score']:.4f}. "
        "The recommendation is based only on internal clustering metrics; original "
        "class labels are used only for optional external comparison."
        f"{dbscan_note}"
    )


def run_final_analysis(
    data: dict[str, Any],
    kmeans_outputs: dict[str, Any],
    agglomerative_outputs: dict[str, Any],
    dbscan_outputs: dict[str, Any],
    paths: dict[str, Path],
) -> dict[str, Any]:
    final_df = make_final_model_comparison(
        kmeans_outputs,
        agglomerative_outputs,
        dbscan_outputs,
    )
    final_model_path = paths["results_dir"] / "final_model_comparison.csv"
    final_df.to_csv(final_model_path, index=False)

    ranking_df = make_model_ranking_summary(final_df)
    ranking_path = paths["results_dir"] / "model_ranking_summary.csv"
    ranking_df.to_csv(ranking_path, index=False)

    assignments_path = save_final_cluster_assignments(
        kmeans_outputs,
        agglomerative_outputs,
        dbscan_outputs,
        paths,
    )

    profile_outputs = save_cluster_profiles(data, kmeans_outputs, paths)
    optional_paths = save_optional_external_label_comparison(
        data,
        kmeans_outputs,
        agglomerative_outputs,
        dbscan_outputs,
        paths,
    )
    optional_comparison = pd.read_csv(
        paths["results_dir"] / "optional_external_label_comparison.csv"
    )

    labels_map = {
        "KMeans k=3": kmeans_outputs["k3_labels"],
        "Best KMeans": kmeans_outputs["best_labels"],
        "Agglomerative ward k=3": agglomerative_outputs["ward_k3_labels"],
        "Best Agglomerative": agglomerative_outputs["best_labels"],
        "Best DBSCAN": dbscan_outputs["best_labels"],
    }
    figure_paths = [
        plot_final_model_metrics_comparison(
            final_df,
            paths["figures_dir"] / "21_final_model_metrics_comparison.png",
        ),
        plot_cluster_size_comparison(
            labels_map,
            paths["figures_dir"] / "22_cluster_size_comparison.png",
        ),
    ]
    figure_paths.extend(profile_outputs["figure_paths"])
    figure_paths.append(
        plot_optional_external_metric_comparison(
            optional_comparison,
            paths["figures_dir"] / "24_optional_external_metric_comparison.png",
        )
    )

    result_paths = [
        final_model_path,
        ranking_path,
        assignments_path,
        *profile_outputs["result_paths"],
        *optional_paths,
    ]
    analysis_text = build_short_analysis_text(final_df)

    return {
        "final_model_comparison": final_df,
        "model_ranking_summary": ranking_df,
        "cluster_profile_summary": profile_outputs["profile_summary"],
        "cluster_profile_scaled_mean": profile_outputs["scaled_means"],
        "cluster_profile_interpretation": profile_outputs["interpretation_text"],
        "analysis_text": analysis_text,
        "result_paths": result_paths,
        "figure_paths": figure_paths,
    }


def run_experiment(exp4_dir: str | Path | None = None) -> dict[str, Any]:
    warnings.filterwarnings("ignore", category=UserWarning)
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.unicode_minus"] = False

    paths = resolve_paths(exp4_dir)
    ensure_output_dirs(paths)

    print("Experiment 4: Wine Clustering Model Practice")
    print(f"Experiment 4 directory: {paths['exp4_dir']}")
    print(f"Data directory: {paths['data_dir']}")
    print("Original class labels will be removed before clustering.")

    data_outputs = prepare_data(paths)
    data = data_outputs["data"]
    kmeans_outputs = run_kmeans_experiment(data, paths)
    agglomerative_outputs = run_agglomerative_experiment(data, paths)
    dbscan_outputs = run_dbscan_experiment(data, paths)
    final_outputs = run_final_analysis(
        data,
        kmeans_outputs,
        agglomerative_outputs,
        dbscan_outputs,
        paths,
    )

    result_paths = [
        *data_outputs["result_paths"],
        *kmeans_outputs["result_paths"],
        *agglomerative_outputs["result_paths"],
        *dbscan_outputs["result_paths"],
        *final_outputs["result_paths"],
    ]
    figure_paths = [
        *data_outputs["figure_paths"],
        *kmeans_outputs["figure_paths"],
        *agglomerative_outputs["figure_paths"],
        *dbscan_outputs["figure_paths"],
        *final_outputs["figure_paths"],
    ]

    recommended = final_outputs["final_model_comparison"].iloc[0]
    print("\nGenerated results files:")
    for file_name in REQUIRED_RESULT_FILES:
        print(f"- {file_name}")
    print("\nGenerated figures files:")
    for file_name in REQUIRED_FIGURE_FILES:
        print(f"- {file_name}")
    print(
        "\nRecommended model: "
        f"{recommended['model']} ({recommended['setting']})"
    )
    print("\nShort analysis text:")
    print(final_outputs["analysis_text"])

    print("\nExperiment 4 completed successfully.")
    print(f"Results directory: {paths['results_dir']}")
    print(f"Figures directory: {paths['figures_dir']}")

    return {
        "paths": paths,
        "data": data,
        "kmeans": kmeans_outputs,
        "agglomerative": agglomerative_outputs,
        "dbscan": dbscan_outputs,
        "final": final_outputs,
        "result_paths": result_paths,
        "figure_paths": figure_paths,
    }


def main() -> None:
    run_experiment()


if __name__ == "__main__":
    main()
