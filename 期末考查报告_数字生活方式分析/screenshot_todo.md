# Screenshot and Code Paste TODO

This file tells you exactly what to insert manually before final submission.
The Word report already contains clear placeholders and explanations.

## 1. Excel Screenshot Tables

Open each workbook in Excel or WPS, take a clean screenshot of the visible table,
and paste it into the matching placeholder in the Word report.

| Word placeholder | Source workbook |
|---|---|
| `[INSERT TABLE1 SCREENSHOT HERE: screenshot_tables/table1_raw_dataset_preview.xlsx]` | `screenshot_tables/table1_raw_dataset_preview.xlsx` |
| `[INSERT TABLE2 SCREENSHOT HERE: screenshot_tables/table2_dataset_fields.xlsx]` | `screenshot_tables/table2_dataset_fields.xlsx` |
| `[INSERT TABLE3 SCREENSHOT HERE: screenshot_tables/table3_missing_value_check.xlsx]` | `screenshot_tables/table3_missing_value_check.xlsx` |
| `[INSERT TABLE4 SCREENSHOT HERE: screenshot_tables/table4_duplicate_check.xlsx]` | `screenshot_tables/table4_duplicate_check.xlsx` |
| `[INSERT TABLE5 SCREENSHOT HERE: screenshot_tables/table5_range_check.xlsx]` | `screenshot_tables/table5_range_check.xlsx` |
| `[INSERT TABLE6 SCREENSHOT HERE: screenshot_tables/table6_engineered_features_preview.xlsx]` | `screenshot_tables/table6_engineered_features_preview.xlsx` |
| `[INSERT TABLE7 SCREENSHOT HERE: screenshot_tables/table7_feature_selection_leakage_control.xlsx]` | `screenshot_tables/table7_feature_selection_leakage_control.xlsx` |
| `[INSERT TABLE8 SCREENSHOT HERE: screenshot_tables/table8_classification_metrics.xlsx]` | `screenshot_tables/table8_classification_metrics.xlsx` |
| `[INSERT TABLE9 SCREENSHOT HERE: screenshot_tables/table9_regression_metrics.xlsx]` | `screenshot_tables/table9_regression_metrics.xlsx` |
| `[INSERT TABLE10 SCREENSHOT HERE: screenshot_tables/table10_clustering_profiles.xlsx]` | `screenshot_tables/table10_clustering_profiles.xlsx` |
| `[INSERT TABLE11 SCREENSHOT HERE: screenshot_tables/table11_pca_explained_variance.xlsx]` | `screenshot_tables/table11_pca_explained_variance.xlsx` |

Tips:
- For Table7, open each sheet and screenshot the relevant part if the sheet is wide.
- For Table9, screenshot the target comparison sheet first because it is the easiest to read.
- Keep the table screenshot readable; do not shrink it too much in Word.

## 2. Final Figures

The figures are already inserted by the Word generation script. If any image
needs to be replaced manually, use the following files:

| Figure | Source file |
|---|---|
| Fig1 High Risk vs No Risk Sample Structure | `figures/final_report/fig1_high_risk_no_risk_distribution.png` |
| Fig2 Core Digital Lifestyle Feature Distributions | `figures/final_report/fig2_core_numeric_distributions.png` |
| Fig3 Correlation Structure of Digital Lifestyle Variables | `figures/final_report/fig3_correlation_heatmap.png` |
| Fig4 Behavioral Difference Between High Risk and No Risk Groups | `figures/final_report/fig4_high_vs_no_risk_boxplots.png` |
| Fig5 Threshold Tuning for Recall-Oriented Screening | `figures/final_report/fig5_threshold_tuning.png` |
| Fig6 Confusion Matrix of the Final High Risk Classifier | `figures/final_report/fig6_confusion_matrix.png` |
| Fig7 Precision-Recall Curve under Class Imbalance | `figures/final_report/fig7_precision_recall_curve.png` |
| Fig8 Digital Dependence: Observed vs Predicted Scores | `figures/final_report/fig8_digital_dependence_observed_predicted.png` |
| Fig9 Productivity Weak Prediction: Observed vs Predicted Scores | `figures/final_report/fig9_productivity_observed_predicted.png` |
| Fig10 KMeans k Selection by Elbow and Silhouette | `figures/final_report/fig10_kmeans_k_selection.png` |
| Fig11 Three Digital Lifestyle Cluster Profiles | `figures/final_report/fig11_cluster_profile_heatmap.png` |
| Fig12 PCA Variance and Two-Dimensional Structure | `figures/final_report/fig12_pca_explained_variance.png` |

## 3. Core Code Snippets

Copy each code block from `report_code_snippets.md` into the matching Word
placeholder:

| Word placeholder | Code source |
|---|---|
| `[PASTE CODE1 HERE FROM report_code_snippets.md: Code1 Data Loading and Basic Inspection]` | Code1 |
| `[PASTE CODE2 HERE FROM report_code_snippets.md: Code2 Missing, Duplicate, and Range Check]` | Code2 |
| `[PASTE CODE3 HERE FROM report_code_snippets.md: Code3 Feature Engineering]` | Code3 |
| `[PASTE CODE4 HERE FROM report_code_snippets.md: Code4 Leakage Control and Feature Selection]` | Code4 |
| `[PASTE CODE5 HERE FROM report_code_snippets.md: Code5 Classification Training and Threshold Tuning]` | Code5 |
| `[PASTE CODE6 HERE FROM report_code_snippets.md: Code6 Regression Evaluation]` | Code6 |
| `[PASTE CODE7 HERE FROM report_code_snippets.md: Code7 Clustering and K Selection]` | Code7 |
| `[PASTE CODE8 HERE FROM report_code_snippets.md: Code8 Export Figures and Screenshot Tables]` | Code8 |

## 4. Appendix A

In Appendix A, replace:

`[PASTE COMPLETE RUNNABLE CODE HERE]`

with the full content of:

`appendix_A_complete_code.py`

## 5. Final Manual Checks

Before submitting, fill only your personal blank fields on the cover. Do not
change the validated metrics. Then export the final Word file to PDF in Word or
WPS if the teacher requests PDF submission.
