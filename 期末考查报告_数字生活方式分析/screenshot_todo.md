# Screenshot and Code Paste TODO

This file tells you exactly what to insert manually before final submission.
The Word report already contains placeholders, captions, and Purpose /
Interpretation / Conclusion text.

## 1. Excel Screenshot Tables

Open each workbook in Excel or WPS, take a clean screenshot of the suggested
sheet area, and paste it into the matching Word placeholder.

| Word table | Source workbook | Suggested sheet / screenshot area |
|---|---|---|
| Table1 Raw Dataset Preview | `screenshot_tables/table1_raw_dataset_preview.xlsx` | `raw_preview`, first 20 rows |
| Table2 Dataset Fields | `screenshot_tables/table2_dataset_fields.xlsx` | `fields`, all visible rows or split into two screenshots if needed |
| Table3 Missing Value Check | `screenshot_tables/table3_missing_value_check.xlsx` | `missing_values`, all fields |
| Table4 Duplicate Check | `screenshot_tables/table4_duplicate_check.xlsx` | `duplicate_check`, full sheet |
| Table5 Range and Rationality Check | `screenshot_tables/table5_range_and_rationality_check.xlsx` | `range_rationality`, all checked numeric fields |
| Table6 Engineered Features Preview | `screenshot_tables/table6_engineered_features_preview.xlsx` | `engineered_preview`, first 10-20 rows |
| Table7 Feature Selection and Leakage Control | `screenshot_tables/table7_feature_selection_and_leakage_control.xlsx` | Screenshot the drop-column sheets and `clustering_features`; do not force the entire workbook into one screenshot |
| Table8 PCA Explained Variance | `screenshot_tables/table8_pca_explained_variance.xlsx` | `pca_variance`, first 8-12 components are enough |
| Table9 Descriptive Statistical Summary | `screenshot_tables/table9_descriptive_statistical_summary.xlsx` | `descriptive_summary`, full visible sheet |
| Table10 Classification Model Comparison and Threshold Results | `screenshot_tables/table10_classification_model_comparison_and_threshold_results.xlsx` | Use `classification_model_comparison`, `threshold_strategy_comparison`, and `final_test_metrics`; screenshot the most relevant part of each |
| Table11 Regression Model Comparison | `screenshot_tables/table11_regression_model_comparison.xlsx` | Use `target_comparison`, `digital_dependence_models`, and `productivity_models`; screenshot model rows and metrics |
| Table12 Clustering Model Comparison and Cluster Profiles | `screenshot_tables/table12_clustering_model_comparison_and_cluster_profiles.xlsx` | Use `model_comparison`, `kmeans_k_scores`, and `cluster_profiles`; screenshot the rows around k=3 and the final profiles |

Tips:
- Keep each screenshot readable. It is better to use two small screenshots than
  one unreadable full-workbook screenshot.
- Do not screenshot WPS/Excel grid decorations if they make the table unclear.
- Do not change the metric values.

## 2. Final Figures

The figures are already inserted by the Word generation script. If any image
needs to be replaced manually, use these files:

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
| Fig12 PCA Explained Variance for Dimensionality Reduction | `figures/final_report/fig12_pca_explained_variance.png` |

## 3. Core Code Snippets

Copy each code block from `report_code_snippets.md` into the matching Word
placeholder:

| Word placeholder | Code source |
|---|---|
| `[PASTE CODE1 HERE FROM report_code_snippets.md: Code1 Data Loading and Basic Inspection]` | Code1 |
| `[PASTE CODE2 HERE FROM report_code_snippets.md: Code2 Missing, Duplicate, and Range Check]` | Code2 |
| `[PASTE CODE3 HERE FROM report_code_snippets.md: Code3 Feature Engineering]` | Code3 |
| `[PASTE CODE4 HERE FROM report_code_snippets.md: Code4 Leakage Control and Task-Specific Feature Selection]` | Code4 |
| `[PASTE CODE5 HERE FROM report_code_snippets.md: Code5 Classification Model Comparison and Threshold Tuning]` | Code5 |
| `[PASTE CODE6 HERE FROM report_code_snippets.md: Code6 Regression Model Evaluation]` | Code6 |
| `[PASTE CODE7 HERE FROM report_code_snippets.md: Code7 Clustering Model Comparison and k Selection]` | Code7 |

## 4. Appendix A

In Appendix A, replace:

`[PASTE COMPLETE RUNNABLE CODE HERE]`

with the full content of:

`appendix_A_complete_code.py`

## 5. Final Manual Checks

Before submitting:

1. Fill only your personal blank fields on the cover.
2. Insert the required Excel screenshots.
3. Paste Code1-Code7 in the main text.
4. Paste the full `appendix_A_complete_code.py` into Appendix A.
5. Open the final DOCX once in Word/WPS to check page layout.
6. Export to PDF if the teacher asks for PDF submission.
