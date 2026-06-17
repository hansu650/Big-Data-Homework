# What Changed

This revision is a full rewrite of the final Word report structure, not a small wording polish.

## Main Report Changes

- Removed Abstract, Keywords, References, Appendix B, Appendix C, and Appendix D.
- Removed "Chapter" style headings.
- Rebuilt the report as a standard data-analysis workflow:
  Objective -> Dataset -> Preprocessing -> EDA -> Modeling -> Conclusion -> Appendix A.
- Kept the school course-exam cover and blank personal-information placeholders.
- Rewrote the English body in a shorter, more student-like course-report style.
- Added clear Purpose / Interpretation / Conclusion explanations under every figure and table screenshot placeholder.
- Kept only Appendix A as the place for complete runnable code.

## Figure Changes

- Generated a new final figure set under `figures/final_report/`.
- Kept exactly 10 useful figures:
  - Fig1 High Risk and No Risk Distribution
  - Fig2 Core Numeric Feature Distributions
  - Fig3 Correlation Heatmap
  - Fig4 High Risk vs No Risk Behavioral Differences
  - Fig5 Classification Threshold Tuning
  - Fig6 Confusion Matrix
  - Fig7 Precision-Recall Curve
  - Fig8 Digital Dependence Observed vs Predicted
  - Fig9 K Selection for KMeans
  - Fig10 Cluster Profile Heatmap
- Removed meaningless old visual content from the Word body, including id-style or static showcase material.
- Multi-line figures use different markers where applicable.
- High Risk / No Risk labels are used instead of raw 0/1 labels in final report figures.

## Excel Screenshot Tables

- Created `screenshot_tables/` with 10 screenshot-ready Excel workbooks.
- These workbooks are intended for manual screenshots by the student.
- Word contains clear placeholders such as:
  `[INSERT TABLE1 SCREENSHOT HERE: screenshot_tables/table1_raw_dataset_preview.xlsx]`

## Code Materials

- Created `report_code_snippets.md` with 8 short code blocks for the main text.
- Created `appendix_A_complete_code.py` as the complete runnable code source for Appendix A.
- Created `screenshot_todo.md` to tell the student where to paste screenshots and code.

## Metrics Kept Unchanged

- Classification: Gradient Boosting, threshold=0.14, Recall=0.6420, F1=0.5355, PR-AUC=0.5084.
- Main regression target: digital_dependence_score, R²=0.9839, MSE=3.1471, MAE=0.9982.
- Weak regression target: productivity_score, R²=-0.0041.
- Clustering: KMeans, k=3, Silhouette=0.1860.

## Scripts Added

- `scripts/generate_final_report_figures.py`
- `scripts/export_screenshot_tables.py`
- `scripts/build_workflow_word_report.py`

