"""Generate final report figures and teacher-feedback evidence.

The script uses validated CSV results wherever possible. It does not overwrite
the locked core model metrics. It regenerates formal PNG figures for the Word
report and writes the group-comparison statistics used to explain Fig4.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import precision_recall_curve
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
    for old_figure in FIGURE_DIR.glob("fig*.png"):
        old_figure.unlink()
    for old_figure in FIGURE_DIR.glob("classification_model_comparison.png"):
        old_figure.unlink()


def save(fig: plt.Figure, filename: str) -> None:
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / filename, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_csv(RAW_DATA_PATH)
    processed = pd.read_csv(PROCESSED_DATA_PATH)
    return raw, processed


def pooled_cohens_d(no_risk: pd.Series, high_risk: pd.Series) -> float:
    pooled = np.sqrt(
        ((len(no_risk) - 1) * no_risk.var(ddof=1) + (len(high_risk) - 1) * high_risk.var(ddof=1))
        / (len(no_risk) + len(high_risk) - 2)
    )
    return float((high_risk.mean() - no_risk.mean()) / pooled)


def write_high_risk_group_comparison(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    rows: list[dict[str, float | str | int]] = []
    no_risk_df = df.loc[df["high_risk_flag"] == 0]
    high_risk_df = df.loc[df["high_risk_flag"] == 1]
    for feature in columns:
        no_risk = no_risk_df[feature]
        high_risk = high_risk_df[feature]
        mean_diff = high_risk.mean() - no_risk.mean()
        rows.append(
            {
                "feature": feature,
                "no_risk_count": len(no_risk),
                "high_risk_count": len(high_risk),
                "no_risk_mean": no_risk.mean(),
                "high_risk_mean": high_risk.mean(),
                "no_risk_median": no_risk.median(),
                "high_risk_median": high_risk.median(),
                "mean_difference": mean_diff,
                "median_difference": high_risk.median() - no_risk.median(),
                "relative_difference_percent": (mean_diff / no_risk.mean()) * 100,
                "cohens_d": pooled_cohens_d(no_risk, high_risk),
            }
        )
    comparison = pd.DataFrame(rows)
    comparison.to_csv(RESULTS_DIR / "high_risk_group_comparison.csv", index=False)
    return comparison


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
    ax.set_title("High Risk vs No Risk Sample Structure")
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
    ax.set_title("Correlation Structure of Digital Lifestyle Variables")
    cbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Correlation")
    save(fig, "fig3_correlation_heatmap.png")


def fig4_risk_boxplots(df: pd.DataFrame) -> pd.DataFrame:
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
    comparison = write_high_risk_group_comparison(df, columns)
    groups = [df.loc[df["high_risk_flag"] == 0], df.loc[df["high_risk_flag"] == 1]]
    fig, axes = plt.subplots(2, 3, figsize=(10.6, 6.3))
    axes = axes.ravel()
    for ax, col, title in zip(axes, columns, titles):
        box = ax.boxplot(
            [groups[0][col], groups[1][col]],
            tick_labels=["No Risk", "High Risk"],
            patch_artist=True,
            medianprops={"color": "#1F2937", "linewidth": 1.3},
        )
        for patch, color in zip(box["boxes"], ["#8FB9E3", "#E08A95"]):
            patch.set_facecolor(color)
            patch.set_alpha(0.85)
        d_value = comparison.loc[comparison["feature"].eq(col), "cohens_d"].iloc[0]
        ax.text(0.98, 0.92, f"d={d_value:.2f}", transform=ax.transAxes, ha="right", va="top", fontsize=8)
        ax.set_title(title)
        ax.tick_params(axis="x", labelrotation=12)
    save(fig, "fig4_high_vs_no_risk_boxplots.png")
    return comparison


def fig5_classification_model_comparison() -> None:
    metrics = pd.read_csv(RESULTS_DIR / "classification_tuned_metrics.csv")
    val = metrics[(metrics["dataset"] == "validation") & (metrics["threshold"].round(2) == 0.50)].copy()
    order = ["logistic_regression", "random_forest", "gradient_boosting"]
    labels = {
        "logistic_regression": "Logistic\nRegression",
        "random_forest": "Random\nForest",
        "gradient_boosting": "Gradient\nBoosting",
    }
    val["model"] = pd.Categorical(val["model"], categories=order, ordered=True)
    val = val.sort_values("model")
    metric_cols = ["recall", "f1", "pr_auc", "balanced_accuracy"]
    metric_labels = ["Recall", "F1", "PR-AUC", "Balanced Acc."]
    x = np.arange(len(val))
    width = 0.18
    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    colors = ["#4C78A8", "#F58518", "#54A24B", "#B279A2"]
    for idx, (metric, label, color) in enumerate(zip(metric_cols, metric_labels, colors)):
        values = val[metric].to_numpy()
        bars = ax.bar(x + (idx - 1.5) * width, values, width, label=label, color=color, alpha=0.9)
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, value + 0.012, f"{value:.3f}", ha="center", va="bottom", fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels([labels[m] for m in val["model"].astype(str)])
    ax.set_ylim(0, 0.75)
    ax.set_ylabel("Validation score")
    ax.set_title("Classification Model Comparison at Default Threshold")
    ax.text(0.0, 0.71, "Validation set, threshold = 0.50", fontsize=8, color="#444444")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    save(fig, "fig5_classification_model_comparison.png")


def fig6_threshold_tuning() -> None:
    tuning = pd.read_csv(RESULTS_DIR / "classification_threshold_tuning.csv").sort_values("threshold")
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    ax.plot(tuning["threshold"], tuning["precision"], marker="o", linewidth=1.8, label="Precision")
    ax.plot(tuning["threshold"], tuning["recall"], marker="^", linewidth=1.8, label="Recall")
    ax.plot(tuning["threshold"], tuning["f1"], marker="s", linewidth=1.8, label="F1")
    ax.axvline(0.14, color="#D1495B", linestyle="--", linewidth=1.4, label="Selected threshold = 0.14")
    ax.set_title("Threshold Tuning for Recall-Oriented Screening")
    ax.set_xlabel("Decision threshold")
    ax.set_ylabel("Validation score")
    ax.set_ylim(0, 1.0)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    save(fig, "fig6_threshold_tuning.png")


def fig7_confusion_matrix() -> None:
    matrix = pd.read_csv(RESULTS_DIR / "classification_final_confusion_matrix.csv", index_col=0)
    values = matrix[["predicted_0", "predicted_1"]].values
    fig, ax = plt.subplots(figsize=(4.6, 4.0))
    image = ax.imshow(values, cmap="Blues")
    ax.set_title("Confusion Matrix at Threshold 0.14")
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
    save(fig, "fig7_confusion_matrix.png")


def fig8_precision_recall_curve(raw: pd.DataFrame) -> None:
    X, y = make_feature_target(raw.copy(), task="classification")
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
    selected = pd.read_csv(RESULTS_DIR / "classification_tuned_metrics.csv")
    selected = selected[
        (selected["dataset"] == "test")
        & (selected["model"] == "gradient_boosting")
        & (selected["threshold"].round(2) == 0.14)
    ].iloc[0]
    baseline = float(y_test.mean())
    fig, ax = plt.subplots(figsize=(5.8, 4.2))
    ax.plot(recall, precision, color="#4C78A8", linewidth=2.0, label="Gradient Boosting")
    ax.axhline(baseline, color="#777777", linestyle="--", linewidth=1.2, label=f"No-skill baseline ({baseline:.3f})")
    ax.scatter(
        [selected["recall"]],
        [selected["precision"]],
        marker="s",
        s=70,
        color="#D1495B",
        label="Threshold 0.14",
        zorder=3,
    )
    ax.set_title("Precision-Recall Curve under Class Imbalance")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.02)
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    save(fig, "fig8_precision_recall_curve.png")


def fig9_digital_dependence_observed_predicted() -> None:
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
    save(fig, "fig9_digital_dependence_observed_predicted.png")


def fig10_productivity_observed_predicted() -> None:
    pred = pd.read_csv(RESULTS_DIR / "regression_productivity_predictions.csv")
    fig, ax = plt.subplots(figsize=(5.8, 4.6))
    ax.scatter(pred["actual"], pred["predicted"], s=18, alpha=0.55, color="#7A5195", edgecolors="none")
    low = min(pred["actual"].min(), pred["predicted"].min())
    high = max(pred["actual"].max(), pred["predicted"].max())
    ax.plot([low, high], [low, high], color="#D1495B", linestyle="--", linewidth=1.6, label="Perfect prediction")
    ax.set_title("Productivity: Observed vs Predicted")
    ax.set_xlabel("Observed productivity_score")
    ax.set_ylabel("Predicted productivity_score")
    ax.legend(frameon=False)
    ax.grid(alpha=0.2)
    save(fig, "fig10_productivity_observed_predicted.png")


def fig11_regression_r2_comparison() -> None:
    dd = pd.read_csv(RESULTS_DIR / "regression_digital_dependence_metrics.csv")
    prod = pd.read_csv(RESULTS_DIR / "regression_productivity_metrics.csv")
    model_order = ["linear_regression", "ridge", "random_forest", "gradient_boosting"]
    label_map = {
        "linear_regression": "Linear\nRegression",
        "ridge": "Ridge",
        "random_forest": "Random\nForest",
        "gradient_boosting": "Gradient\nBoosting",
    }
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.1), sharey=False)
    for ax, data, title in [
        (axes[0], dd, "digital_dependence_score"),
        (axes[1], prod, "productivity_score"),
    ]:
        data = data.set_index("model").loc[model_order].reset_index()
        bars = ax.bar([label_map[m] for m in data["model"]], data["r2"], color="#4C78A8", alpha=0.86)
        ax.axhline(0, color="#333333", linewidth=1.0)
        ax.set_title(title)
        ax.set_ylabel("Test R2")
        ax.grid(axis="y", alpha=0.22)
        for bar, value in zip(bars, data["r2"]):
            va = "bottom" if value >= 0 else "top"
            offset = 0.01 if value >= 0 else -0.01
            ax.text(bar.get_x() + bar.get_width() / 2, value + offset, f"{value:.3f}", ha="center", va=va, fontsize=8)
        ax.tick_params(axis="x", labelrotation=0)
    fig.suptitle("Regression R2 Comparison by Target", y=1.02)
    save(fig, "fig11_regression_r2_comparison.png")


def fig12_clustering_k_selection() -> None:
    comparison = pd.read_csv(RESULTS_DIR / "clustering_model_comparison.csv")
    kmeans = comparison[comparison["algorithm"].eq("kmeans")].sort_values("k")
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.2))
    axes[0].plot(kmeans["k"], kmeans["inertia"], marker="x", linewidth=1.9, color="#4C78A8", label="KMeans inertia")
    axes[0].axvline(3, color="#D1495B", linestyle="--", linewidth=1.2, label="Selected k=3")
    axes[0].set_title("KMeans Inertia")
    axes[0].set_xlabel("Number of clusters (k)")
    axes[0].set_ylabel("Inertia / SSE")
    axes[0].set_xticks(kmeans["k"])
    axes[0].grid(axis="y", alpha=0.25)
    axes[0].legend(frameon=False)
    markers = {"kmeans": "D", "agglomerative": "^", "gaussian_mixture": "s"}
    colors = {"kmeans": "#D1495B", "agglomerative": "#4C78A8", "gaussian_mixture": "#54A24B"}
    labels = {"kmeans": "KMeans", "agglomerative": "Agglomerative", "gaussian_mixture": "GaussianMixture"}
    for algorithm, data in comparison.groupby("algorithm"):
        data = data.sort_values("k")
        axes[1].plot(
            data["k"],
            data["silhouette"],
            marker=markers.get(algorithm, "o"),
            linewidth=1.8,
            color=colors.get(algorithm),
            label=labels.get(algorithm, algorithm),
        )
    axes[1].scatter([3], [0.18595999746385028], s=80, color="#D1495B", edgecolor="black", zorder=5)
    axes[1].annotate("k=3, silhouette=0.186", xy=(3, 0.18596), xytext=(3.25, 0.17), arrowprops={"arrowstyle": "->", "lw": 0.8}, fontsize=8)
    axes[1].set_title("Silhouette by Algorithm")
    axes[1].set_xlabel("Number of clusters (k)")
    axes[1].set_ylabel("Silhouette")
    axes[1].set_xticks(sorted(comparison["k"].dropna().unique()))
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].legend(frameon=False)
    save(fig, "fig12_clustering_k_selection_comparison.png")


def fig13_cluster_profile_heatmap() -> None:
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
    ax.set_title("Three Digital Lifestyle Cluster Profiles")
    cbar = fig.colorbar(image, ax=ax, fraction=0.03, pad=0.03)
    cbar.set_label("Normalized profile level")
    save(fig, "fig13_cluster_profile_heatmap.png")


def fig14_pca_explained_variance() -> None:
    pca = pd.read_csv(RESULTS_DIR / "pca_explained_variance.csv").sort_values("component_index")
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    ax.plot(
        pca["component_index"],
        pca["cumulative_explained_variance"],
        marker="D",
        color="#4C78A8",
        linewidth=1.9,
        label="Cumulative explained variance",
    )
    ax.bar(pca["component_index"], pca["explained_variance_ratio"], color="#A6CEE3", alpha=0.55, label="Single-component ratio")
    pc2 = pca.loc[pca["component_index"].eq(2)].iloc[0]
    ax.axhline(pc2["cumulative_explained_variance"], color="#D1495B", linestyle="--", linewidth=1.2, label="PC1 + PC2 = 42.41%")
    ax.set_title("PCA Explained Variance")
    ax.set_xlabel("Principal component")
    ax.set_ylabel("Explained variance ratio")
    ax.set_xticks(pca["component_index"])
    ax.set_ylim(0, 1.05)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, loc="lower right")
    save(fig, "fig14_pca_explained_variance.png")


def main() -> None:
    ensure_output_dir()
    raw, _processed = load_data()
    fig1_high_risk_distribution(raw)
    fig2_numeric_distributions(raw)
    fig3_correlation_heatmap(raw)
    fig4_risk_boxplots(raw)
    fig5_classification_model_comparison()
    fig6_threshold_tuning()
    fig7_confusion_matrix()
    fig8_precision_recall_curve(raw)
    fig9_digital_dependence_observed_predicted()
    fig10_productivity_observed_predicted()
    fig11_regression_r2_comparison()
    fig12_clustering_k_selection()
    fig13_cluster_profile_heatmap()
    fig14_pca_explained_variance()
    print(f"Generated 14 final report figures in {FIGURE_DIR}")
    print(f"Wrote {RESULTS_DIR / 'high_risk_group_comparison.csv'}")


if __name__ == "__main__":
    main()
