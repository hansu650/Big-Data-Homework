"""Generate the final 10 report figures for the workflow-style Word report.

The script regenerates presentation figures from the validated data/results.
It does not modify experiment CSV metrics or change the reported model scores.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import PrecisionRecallDisplay, precision_recall_curve
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from feature_engineering import make_feature_target, make_preprocessor  # noqa: E402


RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "digital_lifestyle_benchmark_2025.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "digital_lifestyle_benchmark_2025_processed.csv"
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURE_DIR = PROJECT_ROOT / "figures" / "final_report"
RANDOM_STATE = 42
DPI = 300


plt.rcParams.update(
    {
        "figure.dpi": DPI,
        "savefig.dpi": DPI,
        "font.size": 9,
        "axes.titlesize": 11,
        "axes.labelsize": 9,
        "legend.fontsize": 8,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)


def ensure_output_dir() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def save(fig: plt.Figure, filename: str) -> None:
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / filename, bbox_inches="tight")
    plt.close(fig)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_csv(RAW_DATA_PATH)
    processed = pd.read_csv(PROCESSED_DATA_PATH)
    return raw, processed


def fig1_high_risk_distribution(df: pd.DataFrame) -> None:
    counts = df["high_risk_flag"].map({0: "No Risk", 1: "High Risk"}).value_counts().reindex(
        ["No Risk", "High Risk"]
    )
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    colors = ["#4C78A8", "#D1495B"]
    bars = ax.bar(counts.index, counts.values, color=colors, edgecolor="#333333", linewidth=0.6)
    total = counts.sum()
    for bar, value in zip(bars, counts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + total * 0.01,
            f"{value}\n({value / total:.1%})",
            ha="center",
            va="bottom",
        )
    ax.set_title("High Risk and No Risk Distribution")
    ax.set_ylabel("Number of samples")
    ax.set_ylim(0, max(counts.values) * 1.18)
    save(fig, "fig1_high_risk_no_risk_distribution.png")


def fig2_numeric_distributions(df: pd.DataFrame) -> None:
    columns = [
        "device_hours_per_day",
        "phone_unlocks",
        "notifications_per_day",
        "social_media_mins",
        "sleep_hours",
        "digital_dependence_score",
    ]
    titles = [
        "Device hours/day",
        "Phone unlocks",
        "Notifications/day",
        "Social media minutes",
        "Sleep hours",
        "Digital dependence",
    ]
    fig, axes = plt.subplots(2, 3, figsize=(10.5, 6.2))
    axes = axes.ravel()
    for ax, col, title in zip(axes, columns, titles):
        ax.hist(df[col], bins=28, color="#4C78A8", alpha=0.82, edgecolor="white")
        ax.axvline(df[col].mean(), color="#D1495B", linestyle="--", linewidth=1.4, label="Mean")
        ax.set_title(title)
        ax.set_ylabel("Count")
        ax.legend(frameon=False)
    save(fig, "fig2_core_numeric_distributions.png")


def fig3_correlation_heatmap(df: pd.DataFrame) -> None:
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
    corr = df[columns].corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(8.8, 7.2))
    image = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(columns)))
    ax.set_yticks(range(len(columns)))
    ax.set_xticklabels(columns, rotation=45, ha="right", fontsize=7)
    ax.set_yticklabels(columns, fontsize=7)
    for i in range(len(columns)):
        for j in range(len(columns)):
            value = corr.values[i, j]
            color = "white" if abs(value) > 0.55 else "#222222"
            ax.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=6, color=color)
    ax.set_title("Correlation Heatmap")
    cbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Correlation")
    save(fig, "fig3_correlation_heatmap.png")


def fig4_risk_boxplots(df: pd.DataFrame) -> None:
    columns = [
        "device_hours_per_day",
        "phone_unlocks",
        "notifications_per_day",
        "social_media_mins",
        "sleep_hours",
        "digital_dependence_score",
    ]
    titles = [
        "Device hours/day",
        "Phone unlocks",
        "Notifications/day",
        "Social media minutes",
        "Sleep hours",
        "Digital dependence",
    ]
    groups = [
        df.loc[df["high_risk_flag"] == 0],
        df.loc[df["high_risk_flag"] == 1],
    ]
    fig, axes = plt.subplots(2, 3, figsize=(10.6, 6.3))
    axes = axes.ravel()
    for ax, col, title in zip(axes, columns, titles):
        box = ax.boxplot(
            [groups[0][col], groups[1][col]],
            labels=["No Risk", "High Risk"],
            patch_artist=True,
            medianprops={"color": "#1F2937", "linewidth": 1.3},
        )
        for patch, color in zip(box["boxes"], ["#8FB9E3", "#E08A95"]):
            patch.set_facecolor(color)
            patch.set_alpha(0.85)
        ax.set_title(title)
        ax.tick_params(axis="x", labelrotation=12)
    save(fig, "fig4_high_vs_no_risk_boxplots.png")


def fig5_threshold_tuning() -> None:
    tuning = pd.read_csv(RESULTS_DIR / "classification_threshold_tuning.csv")
    tuning = tuning.sort_values("threshold")
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    ax.plot(tuning["threshold"], tuning["precision"], marker="o", linewidth=1.8, label="Precision")
    ax.plot(tuning["threshold"], tuning["recall"], marker="^", linewidth=1.8, label="Recall")
    ax.plot(tuning["threshold"], tuning["f1"], marker="s", linewidth=1.8, label="F1")
    ax.axvline(0.14, color="#D1495B", linestyle="--", linewidth=1.4, label="Selected threshold = 0.14")
    ax.set_title("Classification Threshold Tuning")
    ax.set_xlabel("Decision threshold")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.0)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    save(fig, "fig5_threshold_tuning.png")


def fig6_confusion_matrix() -> None:
    matrix = pd.read_csv(RESULTS_DIR / "classification_final_confusion_matrix.csv", index_col=0)
    values = matrix[["predicted_0", "predicted_1"]].values
    fig, ax = plt.subplots(figsize=(4.6, 4.0))
    image = ax.imshow(values, cmap="Blues")
    ax.set_title("Confusion Matrix")
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["Predicted\nNo Risk", "Predicted\nHigh Risk"])
    ax.set_yticklabels(["Actual\nNo Risk", "Actual\nHigh Risk"])
    max_value = values.max()
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            color = "white" if values[i, j] > max_value * 0.55 else "#1F2937"
            ax.text(j, i, f"{values[i, j]}", ha="center", va="center", fontsize=12, color=color)
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    save(fig, "fig6_confusion_matrix.png")


def fig7_precision_recall_curve(raw: pd.DataFrame) -> None:
    data = raw.copy()
    X, y = make_feature_target(data, task="classification")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    model = Pipeline(
        steps=[
            ("preprocessor", make_preprocessor(X_train)),
            (
                "model",
                GradientBoostingClassifier(
                    n_estimators=100,
                    max_depth=2,
                    learning_rate=0.03,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )
    model.fit(X_train, y_train)
    proba = model.predict_proba(X_test)[:, 1]
    precision, recall, _ = precision_recall_curve(y_test, proba)
    fig, ax = plt.subplots(figsize=(5.8, 4.2))
    ax.plot(recall, precision, color="#4C78A8", linewidth=2.0)
    selected = pd.read_csv(RESULTS_DIR / "classification_tuned_metrics.csv")
    selected = selected[
        (selected["dataset"] == "test")
        & (selected["model"] == "gradient_boosting")
        & (selected["threshold"].round(2) == 0.14)
    ].iloc[0]
    ax.scatter(
        [selected["recall"]],
        [selected["precision"]],
        marker="s",
        s=70,
        color="#D1495B",
        label="Threshold 0.14",
        zorder=3,
    )
    ax.set_title("Precision-Recall Curve")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.02)
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    save(fig, "fig7_precision_recall_curve.png")


def fig8_observed_predicted() -> None:
    pred = pd.read_csv(RESULTS_DIR / "regression_digital_dependence_predictions.csv")
    fig, ax = plt.subplots(figsize=(5.8, 4.6))
    ax.scatter(pred["actual"], pred["predicted"], s=18, alpha=0.55, color="#4C78A8", edgecolors="none")
    low = min(pred["actual"].min(), pred["predicted"].min())
    high = max(pred["actual"].max(), pred["predicted"].max())
    ax.plot([low, high], [low, high], color="#D1495B", linestyle="--", linewidth=1.6, label="Perfect prediction")
    ax.set_title("Digital Dependence: Observed vs Predicted")
    ax.set_xlabel("Observed digital_dependence_score")
    ax.set_ylabel("Predicted digital_dependence_score")
    ax.legend(frameon=False)
    ax.grid(alpha=0.2)
    save(fig, "fig8_digital_dependence_observed_predicted.png")


def fig9_kmeans_k_selection() -> None:
    scores = pd.read_csv(RESULTS_DIR / "clustering_kmeans_scores.csv")
    fig, ax1 = plt.subplots(figsize=(6.8, 4.2))
    ax1.plot(
        scores["k"],
        scores["inertia"],
        marker="x",
        color="#4C78A8",
        linewidth=1.9,
        label="Inertia / SSE",
    )
    ax1.set_xlabel("Number of clusters (k)")
    ax1.set_ylabel("Inertia / SSE", color="#4C78A8")
    ax1.tick_params(axis="y", labelcolor="#4C78A8")
    ax1.set_xticks(scores["k"])
    ax2 = ax1.twinx()
    ax2.plot(
        scores["k"],
        scores["silhouette"],
        marker="D",
        color="#D1495B",
        linewidth=1.9,
        label="Silhouette",
    )
    ax2.set_ylabel("Silhouette", color="#D1495B")
    ax2.tick_params(axis="y", labelcolor="#D1495B")
    ax1.axvline(3, color="#444444", linestyle="--", linewidth=1.1)
    ax1.set_title("K Selection for KMeans")
    lines = ax1.get_lines() + ax2.get_lines()
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, frameon=False, loc="best")
    ax1.grid(axis="x", alpha=0.2)
    save(fig, "fig9_kmeans_k_selection.png")


def fig10_cluster_profile_heatmap() -> None:
    profiles = pd.read_csv(RESULTS_DIR / "clustering_lifestyle_profiles_compact.csv")
    label_map = {
        "high_social_media_profile": "High social-media-use",
        "high_device_dependence_profile": "High device-dependence",
        "balanced_low_load_profile": "Low-load balanced",
    }
    profiles["profile"] = profiles["suggested_cluster_label"].map(label_map)
    columns = [
        "device_hours_per_day",
        "social_media_mins",
        "sleep_hours",
        "sleep_quality",
        "high_risk_flag",
        "digital_dependence_score",
    ]
    values = profiles[columns].astype(float)
    normalized = (values - values.min()) / (values.max() - values.min())
    fig, ax = plt.subplots(figsize=(8.0, 3.8))
    image = ax.imshow(normalized.values, cmap="YlGnBu", vmin=0, vmax=1)
    ax.set_yticks(range(len(profiles)))
    ax.set_yticklabels([f"Cluster {c}\n{p}" for c, p in zip(profiles["cluster"], profiles["profile"])])
    ax.set_xticks(range(len(columns)))
    ax.set_xticklabels(
        [
            "Device\nhours",
            "Social\nmedia",
            "Sleep\nhours",
            "Sleep\nquality",
            "High Risk\nratio",
            "Digital\ndependence",
        ],
        rotation=0,
    )
    for i in range(normalized.shape[0]):
        for j in range(normalized.shape[1]):
            raw_value = values.iloc[i, j]
            text = f"{raw_value:.2f}" if columns[j] != "high_risk_flag" else f"{raw_value:.1%}"
            ax.text(j, i, text, ha="center", va="center", fontsize=7)
    ax.set_title("Cluster Profile Heatmap")
    cbar = fig.colorbar(image, ax=ax, fraction=0.03, pad=0.03)
    cbar.set_label("Normalized profile level")
    save(fig, "fig10_cluster_profile_heatmap.png")


def main() -> None:
    ensure_output_dir()
    raw, processed = load_data()
    fig1_high_risk_distribution(raw)
    fig2_numeric_distributions(raw)
    fig3_correlation_heatmap(raw)
    fig4_risk_boxplots(raw)
    fig5_threshold_tuning()
    fig6_confusion_matrix()
    fig7_precision_recall_curve(raw)
    fig8_observed_predicted()
    fig9_kmeans_k_selection()
    fig10_cluster_profile_heatmap()
    print(f"Generated 10 final report figures in {FIGURE_DIR}")


if __name__ == "__main__":
    main()
