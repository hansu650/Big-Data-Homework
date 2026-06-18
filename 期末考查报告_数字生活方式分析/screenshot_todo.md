# Screenshot and Manual Insert TODO

This file records what still needs manual insertion after the teacher-feedback
revision. The revised Word report already contains all Python-generated figures.
Only the data-process tables are left as screenshot placeholders, because the
student should open the Excel/CSV evidence files and paste clean screenshots
manually.

## 1. Table Screenshots to Insert Manually

Open each workbook in Excel or WPS, take a readable screenshot of the suggested
area, and paste it into the matching red placeholder in the Word report.

| Word placeholder | Source workbook | Suggested screenshot area |
|---|---|---|
| Table1 Raw Dataset Preview | `screenshot_tables/table1_raw_dataset_preview.xlsx` | `raw_preview`, first 20 rows |
| Table2 Dataset Fields | `screenshot_tables/table2_dataset_fields.xlsx` | `fields`; split into two screenshots if all fields are too small |
| Table3 Missing Value Check | `screenshot_tables/table3_missing_value_check.xlsx` | `missing_values`, all fields |
| Table4 Duplicate Check | `screenshot_tables/table4_duplicate_check.xlsx` | `duplicate_check`, full sheet |
| Table5 Range and Rationality Check | `screenshot_tables/table5_range_and_rationality_check.xlsx` | `range_rationality`, all checked numeric fields |
| Table6 Engineered Features Preview | `screenshot_tables/table6_engineered_features_preview.xlsx` | `engineered_preview`, first 10-20 rows |
| Table7 Feature Selection and Leakage Control | `screenshot_tables/table7_feature_selection_and_leakage_control.xlsx` | key sheets for dropped columns, input features, and clustering features |
| Table8 PCA Explained Variance | `screenshot_tables/table8_pca_explained_variance.xlsx` | `pca_variance`, first 8-12 components |
| Table9 Descriptive Statistical Summary | `screenshot_tables/table9_descriptive_statistical_summary.xlsx` | `descriptive_summary`, full visible sheet |

Table10, Table11, and Table12 are not used in the Word body anymore. Their
machine-learning comparison information has been converted into formal Python
figures:

- Fig5 Classification Model Comparison at the Default Threshold.
- Fig11 Regression R2 Comparison by Target.
- Fig12 K Selection by Inertia and Silhouette.

## 2. Figures Already Inserted

The Word report already contains these Python-generated figures. You do not
need to screenshot them manually unless you want to replace an image later.

| Figure | Source file |
|---|---|
| Fig1 High Risk vs No Risk Sample Structure | `figures/final_report/fig1_high_risk_no_risk_distribution.png` |
| Fig2 Core Digital Lifestyle Feature Distributions | `figures/final_report/fig2_core_numeric_distributions.png` |
| Fig3 Correlation Structure of Digital Lifestyle Variables | `figures/final_report/fig3_correlation_heatmap.png` |
| Fig4 Behavioral Difference Between High Risk and No Risk Groups | `figures/final_report/fig4_high_vs_no_risk_boxplots.png` |
| Fig5 Classification Model Comparison at the Default Threshold | `figures/final_report/fig5_classification_model_comparison.png` |
| Fig6 Threshold Tuning for Recall-Oriented Screening | `figures/final_report/fig6_threshold_tuning.png` |
| Fig7 Confusion Matrix of the Final High Risk Classifier | `figures/final_report/fig7_confusion_matrix.png` |
| Fig8 Precision-Recall Curve under Class Imbalance | `figures/final_report/fig8_precision_recall_curve.png` |
| Fig9 Digital Dependence Observed vs Predicted Scores | `figures/final_report/fig9_digital_dependence_observed_predicted.png` |
| Fig10 Productivity Weak Prediction Observed vs Predicted Scores | `figures/final_report/fig10_productivity_observed_predicted.png` |
| Fig11 Regression R2 Comparison by Target | `figures/final_report/fig11_regression_r2_comparison.png` |
| Fig12 K Selection by Inertia and Silhouette | `figures/final_report/fig12_clustering_k_selection_comparison.png` |
| Fig13 Three Digital Lifestyle Cluster Profiles | `figures/final_report/fig13_cluster_profile_heatmap.png` |
| Fig14 PCA Explained Variance for Dimensionality Reduction | `figures/final_report/fig14_pca_explained_variance.png` |

## 3. Manual Checks Before Submission

1. Fill only the blank personal fields on the cover.
2. Replace the red Table1-Table9 placeholders with screenshots from the listed
   workbooks.
3. Keep the Python-generated figures as they are unless a layout issue appears.
4. Open the DOCX in Word/WPS and check whether any inserted screenshot is too
   small, blurred, or outside the page margin.
5. Export to PDF only after the table screenshots have been inserted.
