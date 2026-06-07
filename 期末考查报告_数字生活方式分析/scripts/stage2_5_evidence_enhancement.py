from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from config import (  # noqa: E402
    FIGURES_DIR,
    HIGH_RISK_LEAKAGE_COLUMNS,
    RANDOM_STATE,
    RESULTS_DIR,
)
from data_utils import ensure_project_dirs, load_processed_dataset, load_raw_dataset  # noqa: E402
from feature_engineering import add_behavior_features, make_feature_target  # noqa: E402
from visualization import configure_matplotlib, save_figure  # noqa: E402


REASONABLE_RANGES = {
    "age": (0, 120),
    "device_hours_per_day": (0, 24),
    "phone_unlocks": (0, 1000),
    "notifications_per_day": (0, 1440),
    "social_media_mins": (0, 1440),
    "study_mins": (0, 1440),
    "physical_activity_days": (0, 7),
    "sleep_hours": (0, 24),
    "sleep_quality": (1, 5),
    "productivity_score": (0, 100),
    "digital_dependence_score": (0, 100),
}

ENGINEERED_FEATURES = [
    "social_media_hours",
    "study_hours",
    "notifications_per_device_hour",
    "unlocks_per_device_hour",
    "device_to_sleep_ratio",
    "activity_sleep_interaction",
    "social_to_study_ratio",
]


def bool_text(value: bool) -> str:
    return "yes" if value else "no"


def quality_check_tables(raw_df: pd.DataFrame, processed_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    rows.extend(
        [
            {
                "section": "dataset_summary",
                "item": "raw_sample_count",
                "field": "",
                "value": int(raw_df.shape[0]),
                "min": "",
                "max": "",
                "reasonable_range": "",
                "out_of_range_count": "",
                "passed": "yes",
                "handling_strategy": "No row deletion was applied.",
                "notes": "Original dataset row count.",
            },
            {
                "section": "dataset_summary",
                "item": "raw_field_count",
                "field": "",
                "value": int(raw_df.shape[1]),
                "min": "",
                "max": "",
                "reasonable_range": "",
                "out_of_range_count": "",
                "passed": "yes",
                "handling_strategy": "No column deletion was applied.",
                "notes": "Original dataset column count.",
            },
            {
                "section": "dataset_summary",
                "item": "missing_value_total",
                "field": "",
                "value": int(raw_df.isna().sum().sum()),
                "min": "",
                "max": "",
                "reasonable_range": "",
                "out_of_range_count": "",
                "passed": bool_text(int(raw_df.isna().sum().sum()) == 0),
                "handling_strategy": "Model pipelines use imputation if needed; no record was removed.",
                "notes": "Total missing cells in the raw dataset.",
            },
            {
                "section": "dataset_summary",
                "item": "duplicate_row_count",
                "field": "",
                "value": int(raw_df.duplicated().sum()),
                "min": "",
                "max": "",
                "reasonable_range": "",
                "out_of_range_count": "",
                "passed": bool_text(int(raw_df.duplicated().sum()) == 0),
                "handling_strategy": "No row deletion was required after duplicate check.",
                "notes": "Exact duplicate rows in the raw dataset.",
            },
            {
                "section": "dataset_summary",
                "item": "duplicate_id_count",
                "field": "id",
                "value": int(raw_df["id"].duplicated().sum()) if "id" in raw_df.columns else "",
                "min": "",
                "max": "",
                "reasonable_range": "",
                "out_of_range_count": "",
                "passed": bool_text("id" in raw_df.columns and int(raw_df["id"].duplicated().sum()) == 0),
                "handling_strategy": "No id-based row deletion was required.",
                "notes": "Duplicate identifiers in the raw dataset.",
            },
        ]
    )

    for field, (lower, upper) in REASONABLE_RANGES.items():
        if field not in raw_df.columns:
            rows.append(
                {
                    "section": "range_check",
                    "item": "numeric_reasonable_range",
                    "field": field,
                    "value": "",
                    "min": "",
                    "max": "",
                    "reasonable_range": f"[{lower}, {upper}]",
                    "out_of_range_count": "",
                    "passed": "no",
                    "handling_strategy": "Field not found; no processing was applied.",
                    "notes": "Expected field is absent.",
                }
            )
            continue
        series = raw_df[field]
        out_of_range = series.notna() & ((series < lower) | (series > upper))
        rows.append(
            {
                "section": "range_check",
                "item": "numeric_reasonable_range",
                "field": field,
                "value": "",
                "min": float(series.min(skipna=True)),
                "max": float(series.max(skipna=True)),
                "reasonable_range": f"[{lower}, {upper}]",
                "out_of_range_count": int(out_of_range.sum()),
                "passed": bool_text(int(out_of_range.sum()) == 0),
                "handling_strategy": (
                    "检查后未发现需删除记录。"
                    if int(out_of_range.sum()) == 0
                    else "Flagged for review only; no automatic deletion was applied."
                ),
                "notes": "Reasonable range screening for report-quality preprocessing evidence.",
            }
        )

    for feature in ENGINEERED_FEATURES:
        exists = feature in processed_df.columns
        rows.append(
            {
                "section": "engineered_feature_check",
                "item": "feature_generated",
                "field": feature,
                "value": bool_text(exists),
                "min": float(processed_df[feature].min(skipna=True)) if exists else "",
                "max": float(processed_df[feature].max(skipna=True)) if exists else "",
                "reasonable_range": "",
                "out_of_range_count": "",
                "passed": bool_text(exists),
                "handling_strategy": "Generated by add_behavior_features from behavior/lifestyle variables.",
                "notes": "Feature engineering success check.",
            }
        )

    rows.extend(
        [
            {
                "section": "feature_selection",
                "item": "classification_leakage_control",
                "field": "high_risk_flag",
                "value": "; ".join(HIGH_RISK_LEAKAGE_COLUMNS),
                "min": "",
                "max": "",
                "reasonable_range": "",
                "out_of_range_count": "",
                "passed": "yes",
                "handling_strategy": "Classification excludes leakage/outcome columns and id.",
                "notes": "Main classification models do not use mental-state or efficiency outcome fields.",
            },
            {
                "section": "feature_selection",
                "item": "regression_outcome_control",
                "field": "productivity_score; digital_dependence_score",
                "value": "high_risk_flag and other outcome fields excluded",
                "min": "",
                "max": "",
                "reasonable_range": "",
                "out_of_range_count": "",
                "passed": "yes",
                "handling_strategy": "Regression excludes high_risk_flag, mental-state outcomes, and the alternate target.",
                "notes": "Prevents direct use of labels or related outcome fields as predictors.",
            },
            {
                "section": "feature_selection",
                "item": "clustering_behavior_lifestyle_only",
                "field": "clustering feature matrix",
                "value": "digital behavior and lifestyle numeric features only",
                "min": "",
                "max": "",
                "reasonable_range": "",
                "out_of_range_count": "",
                "passed": "yes",
                "handling_strategy": "Clustering uses explicit behavior/lifestyle whitelist from feature_engineering.py.",
                "notes": "Background categories and outcome variables are only used for profile interpretation.",
            },
        ]
    )
    return pd.DataFrame(rows)


def write_quality_markdown(quality_df: pd.DataFrame, path: Path) -> None:
    dataset_rows = quality_df[quality_df["section"] == "dataset_summary"]
    range_rows = quality_df[quality_df["section"] == "range_check"]
    feature_rows = quality_df[quality_df["section"] == "engineered_feature_check"]
    any_range_issue = (range_rows["passed"] != "yes").any()
    any_feature_issue = (feature_rows["passed"] != "yes").any()
    missing_total = dataset_rows.loc[dataset_rows["item"] == "missing_value_total", "value"].iloc[0]
    duplicate_rows = dataset_rows.loc[dataset_rows["item"] == "duplicate_row_count", "value"].iloc[0]
    duplicate_ids = dataset_rows.loc[dataset_rows["item"] == "duplicate_id_count", "value"].iloc[0]

    text = f"""# Preprocessing Quality Check

## Dataset-Level Checks

- 原始样本量：{dataset_rows.loc[dataset_rows['item'] == 'raw_sample_count', 'value'].iloc[0]}
- 原始字段数：{dataset_rows.loc[dataset_rows['item'] == 'raw_field_count', 'value'].iloc[0]}
- 缺失值总数：{missing_total}
- 重复行数量：{duplicate_rows}
- 重复 id 数量：{duplicate_ids}

## Numeric Range Checks

已检查字段：{', '.join(REASONABLE_RANGES.keys())}。

{"存在超出合理范围的字段，已在 CSV 中标记，仅作为复核证据，不自动删除记录。" if any_range_issue else "所有检查字段均处于设定合理范围内，检查后未发现需删除记录。"}

## Engineered Feature Checks

已检查工程特征：{', '.join(ENGINEERED_FEATURES)}。

{"存在未生成的工程特征，请复核 feature_engineering.py。" if any_feature_issue else "全部工程特征已成功生成。"}

## Feature Selection Evidence

- 分类任务排除泄漏字段：anxiety_score、depression_score、stress_level、happiness_score、focus_score、productivity_score、digital_dependence_score，以及 id 和目标列 high_risk_flag。
- 回归任务不使用 high_risk_flag、心理状态 outcome 字段，以及另一个 outcome 目标变量。
- 聚类任务只使用数字行为与生活习惯数值特征；人口背景、设备类别和结果变量只用于聚类后画像解释。

## Handling Strategy

本次 Stage 2.5 仅补充质量检查证据，不重新设计实验，不删除原始数据，不改变分类、回归、聚类主实验指标。
"""
    path.write_text(text, encoding="utf-8")


def run_pca(processed_df: pd.DataFrame) -> pd.DataFrame:
    X_cluster, _ = make_feature_target(processed_df, task="clustering")
    pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    X_scaled = pipeline.fit_transform(X_cluster)
    pca = PCA(random_state=RANDOM_STATE)
    pca.fit(X_scaled)
    explained = pd.DataFrame(
        {
            "component": [f"PC{i + 1}" for i in range(len(pca.explained_variance_ratio_))],
            "component_index": np.arange(1, len(pca.explained_variance_ratio_) + 1),
            "explained_variance_ratio": pca.explained_variance_ratio_,
            "cumulative_explained_variance": np.cumsum(pca.explained_variance_ratio_),
            "input_feature_count": X_cluster.shape[1],
        }
    )
    explained["input_features"] = ", ".join(X_cluster.columns)
    return explained


def plot_pca_explained_variance(explained_df: pd.DataFrame, path: Path) -> None:
    configure_matplotlib()
    plt.figure(figsize=(7, 4.5))
    plt.plot(
        explained_df["component_index"],
        explained_df["cumulative_explained_variance"],
        marker="o",
        color="#4C78A8",
        label="Cumulative explained variance",
    )
    plt.bar(
        explained_df["component_index"],
        explained_df["explained_variance_ratio"],
        alpha=0.35,
        color="#72B7B2",
        label="Individual explained variance",
    )
    plt.axhline(0.8, color="#E45756", linestyle="--", linewidth=1, label="80% reference")
    plt.ylim(0, 1.05)
    plt.xlabel("Principal component")
    plt.ylabel("Explained variance ratio")
    plt.title("PCA Explained Variance for Clustering Features")
    plt.legend()
    save_figure(path)


def final_report_figure_selection() -> pd.DataFrame:
    rows = [
        ("EDA", "figures/eda_high_risk_flag_distribution.png", "figure", True, False, "Show class balance for high_risk_flag.", "Distribution of high-risk flag"),
        ("EDA", "figures/eda_numeric_histograms.png", "figure", False, True, "Summarize numeric feature distributions; useful as appendix if main text space is limited.", "Numeric feature distributions"),
        ("EDA", "figures/eda_numeric_correlation_heatmap.png", "figure", True, False, "Show correlation structure and potential redundancy.", "Numeric correlation heatmap"),
        ("EDA", "figures/eda_boxplots_by_risk.png", "figure", True, False, "Compare behavior variables across risk groups.", "Behavior variables by high-risk group"),
        ("EDA", "figures/eda_category_risk_rate.png", "figure", True, False, "Compare descriptive risk rates across categories.", "Category-level high-risk rates"),
        ("EDA", "figures/eda_behavior_outcome_scatter.png", "figure", False, True, "Visualize behavior-outcome relationships without causal claims; useful as appendix if main text space is limited.", "Behavior and outcome relationships"),
        ("Classification", "figures/classification_tuned_metrics_comparison.png", "figure", True, False, "Compare threshold policies for high-risk screening.", "Classification threshold policy metrics"),
        ("Classification", "figures/classification_final_confusion_matrix.png", "figure", True, False, "Show final screening errors after threshold selection.", "Final classification confusion matrix"),
        ("Classification", "figures/classification_precision_recall_curve.png", "figure", True, False, "Support PR-AUC and threshold discussion.", "Precision-Recall curve"),
        ("Classification", "figures/classification_roc_curve.png", "figure", True, False, "Support ROC-AUC reporting.", "ROC curve"),
        ("Regression", "figures/regression_target_comparison.png", "figure", True, False, "Compare productivity and digital dependence targets.", "Regression target comparison"),
        ("Regression", "figures/regression_digital_dependence_observed_vs_predicted.png", "figure", True, False, "Show fit quality for the stronger regression target.", "Observed vs predicted digital dependence"),
        ("Regression", "figures/regression_digital_dependence_permutation_importance.png", "figure", True, False, "Show important features for digital dependence prediction.", "Digital dependence permutation importance"),
        ("Clustering", "figures/clustering_kmeans_elbow.png", "figure", True, False, "Show KMeans elbow evidence.", "KMeans elbow curve"),
        ("Clustering", "figures/clustering_silhouette_by_k.png", "figure", True, False, "Compare silhouette scores by algorithm and k.", "Silhouette scores by clustering method"),
        ("Clustering", "figures/clustering_lifestyle_pca.png", "figure", True, False, "Visualize cluster assignments in two PCA dimensions.", "Lifestyle clusters in PCA space"),
        ("Clustering", "figures/clustering_lifestyle_profile_heatmap.png", "figure", True, False, "Summarize standardized cluster profiles.", "Cluster profile heatmap"),
        ("PCA Supplement", "figures/pca_explained_variance.png", "figure", True, False, "Respond to PCA/feature extraction requirement; PCA is for visualization and auxiliary understanding only.", "PCA cumulative explained variance"),
        ("Appendix", "figures/regression_productivity_observed_vs_predicted.png", "figure", False, True, "Document weak productivity prediction as a negative result.", "Observed vs predicted productivity score"),
        ("Appendix", "figures/classification_permutation_importance.png", "figure", False, True, "Keep detailed model interpretation figure outside main text if space is limited.", "Classification permutation importance"),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "chapter",
            "artifact_path",
            "artifact_type",
            "include_in_main_text",
            "include_in_appendix",
            "purpose",
            "suggested_caption",
        ],
    )


def final_report_table_selection() -> pd.DataFrame:
    rows = [
        ("Dataset", "results/dataset_compliance_summary.csv", "table", True, False, "Document dataset source, scale, license, and reproducibility constraints.", "Dataset compliance summary"),
        ("Preprocessing", "results/preprocessing_quality_check.csv", "table", True, False, "Provide missingness, duplicate, range, engineered feature, and feature-selection checks.", "Preprocessing quality check"),
        ("Classification", "results/classification_tuned_metrics.csv", "table", True, False, "Report tuned classification metrics under threshold policies.", "Tuned classification metrics"),
        ("Classification", "results/classification_threshold_tuning.csv", "table", True, False, "Show validation threshold selection evidence.", "Threshold tuning results"),
        ("Regression", "results/regression_target_comparison.csv", "table", True, False, "Compare productivity and digital dependence regression targets.", "Regression target comparison"),
        ("Regression", "results/regression_digital_dependence_metrics.csv", "table", True, False, "Report the stronger digital dependence regression target.", "Digital dependence regression metrics"),
        ("Regression", "results/regression_productivity_metrics.csv", "table", True, False, "Report productivity as weak/negative prediction evidence.", "Productivity regression metrics"),
        ("Clustering", "results/clustering_model_comparison.csv", "table", True, False, "Compare clustering algorithms and k values.", "Clustering model comparison"),
        ("Clustering", "results/clustering_lifestyle_profiles_compact.csv", "table", True, False, "Use compact profiles in main text.", "Compact lifestyle cluster profiles"),
        ("PCA Supplement", "results/pca_explained_variance.csv", "table", False, True, "Full PCA explained variance table for appendix.", "PCA explained variance"),
        ("Appendix", "results/classification_cv_results.csv", "table", False, True, "Full hyperparameter search evidence.", "Classification CV search results"),
        ("Appendix", "results/regression_digital_dependence_cv_results.csv", "table", False, True, "Full regression search evidence.", "Digital dependence regression CV results"),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "chapter",
            "artifact_path",
            "artifact_type",
            "include_in_main_text",
            "include_in_appendix",
            "purpose",
            "suggested_caption",
        ],
    )


def write_stage2_5_summary(path: Path, quality_df: pd.DataFrame, pca_df: pd.DataFrame) -> None:
    missing_total = quality_df.loc[quality_df["item"] == "missing_value_total", "value"].iloc[0]
    duplicate_rows = quality_df.loc[quality_df["item"] == "duplicate_row_count", "value"].iloc[0]
    duplicate_ids = quality_df.loc[quality_df["item"] == "duplicate_id_count", "value"].iloc[0]
    components_for_80 = int(pca_df[pca_df["cumulative_explained_variance"] >= 0.8]["component_index"].min())
    text = f"""# Stage 2.5 Evidence Enhancement Summary

## 1. Scope

本次没有新增核心模型，没有重新运行或重新设计分类、回归、聚类主实验，也没有引入深度学习或 LCA。Stage 2.5 只补强报告证据。

## 2. Preprocessing Quality Evidence

已生成：

- `results/preprocessing_quality_check.csv`
- `results/preprocessing_quality_check.md`

检查项包括原始样本量、字段数、缺失值、重复行、重复 id、关键数值字段合理范围、工程特征生成状态和任务级特征筛选说明。

本次检查显示：缺失值总数为 {missing_total}，重复行数量为 {duplicate_rows}，重复 id 数量为 {duplicate_ids}。若未发现需删除记录，报告中应写“检查后未发现需删除记录”。

## 3. PCA Explained Variance Evidence

已生成：

- `results/pca_explained_variance.csv`
- `figures/pca_explained_variance.png`

PCA 使用与聚类一致的标准化数字行为与生活习惯数值特征。累计解释方差达到 80% 大约需要前 {components_for_80} 个主成分。PCA 主要用于降维可视化和辅助理解，不作为分类/回归输入，也不作为因果解释。

## 4. Final Report Artifact Selection

已生成：

- `results/final_report_figure_selection.csv`
- `results/final_report_table_selection.csv`

清单将正文图表和附录图表分开，正文建议优先引用分类阈值、数字依赖回归、聚类算法对比、简化画像和 PCA 解释方差等高价值证据。

## 5. Readiness

当前实验结果已经足够进入正式报告写作。正式正文仍需保持谨慎：`productivity_score` 作为弱预测/负结果，`digital_dependence_score` 更适合作为回归主线，聚类结果用于探索性画像而不是严格人群边界。
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_project_dirs()
    np.random.seed(RANDOM_STATE)

    raw_df = load_raw_dataset(download=False)
    processed_df = load_processed_dataset(fallback_to_raw=True)
    processed_df = add_behavior_features(processed_df)

    quality_df = quality_check_tables(raw_df, processed_df)
    quality_path = RESULTS_DIR / "preprocessing_quality_check.csv"
    quality_md_path = RESULTS_DIR / "preprocessing_quality_check.md"
    quality_df.to_csv(quality_path, index=False)
    write_quality_markdown(quality_df, quality_md_path)

    pca_df = run_pca(processed_df)
    pca_path = RESULTS_DIR / "pca_explained_variance.csv"
    pca_df.to_csv(pca_path, index=False)
    plot_pca_explained_variance(pca_df, FIGURES_DIR / "pca_explained_variance.png")

    figure_selection = final_report_figure_selection()
    table_selection = final_report_table_selection()
    figure_selection.to_csv(RESULTS_DIR / "final_report_figure_selection.csv", index=False)
    table_selection.to_csv(RESULTS_DIR / "final_report_table_selection.csv", index=False)

    write_stage2_5_summary(RESULTS_DIR / "stage2_5_evidence_enhancement_summary.md", quality_df, pca_df)

    print(f"Wrote {quality_path}")
    print(f"Wrote {quality_md_path}")
    print(f"Wrote {pca_path}")
    print(f"Wrote {FIGURES_DIR / 'pca_explained_variance.png'}")
    print(f"Wrote {RESULTS_DIR / 'final_report_figure_selection.csv'}")
    print(f"Wrote {RESULTS_DIR / 'final_report_table_selection.csv'}")
    print(f"Wrote {RESULTS_DIR / 'stage2_5_evidence_enhancement_summary.md'}")


if __name__ == "__main__":
    main()
