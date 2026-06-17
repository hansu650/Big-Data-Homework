# What Changed in This Small Fix Pass

This pass keeps the workflow-style report created in commit `61f68b3`. It does
not redesign the experiments and does not change the validated core metrics.

## Report Structure

- Kept the main workflow: Report Workflow -> Research Objective and Task Design
  -> Dataset Description and Task Feasibility -> Data Preprocessing and Feature
  Construction -> Statistical Exploration and Visualization -> Modeling, Tuning,
  and Evaluation -> Findings, Limitations, and Reflection -> Appendix A.
- Did not restore Abstract, Keywords, References, Chapter wording, or Appendix
  B/C/D.
- Made section titles more formal while keeping them short and easy for the
  teacher to scan.
- Removed the strong comparison with `pfm_train` / `pfm_test`; the dataset
  section now lightly states that other candidate materials were reviewed.

## Figures

- Regenerated final report figures in `figures/final_report/`.
- Kept useful figures only and added two meaningful evidence figures:
  - Fig9 Productivity Weak Prediction: Observed vs Predicted Scores.
  - Fig12 PCA Variance and Two-Dimensional Structure.
- Final report now contains 12 figures, not a hard-coded 10-figure limit.
- Multi-line plots use different markers where needed:
  - Precision: circle.
  - Recall: triangle.
  - F1: square.
  - Inertia / SSE: x.
  - Silhouette: diamond.
- High Risk / No Risk labels are used instead of raw 0/1 labels where appropriate.

## Screenshot Tables

- Kept the Excel screenshot-table workflow.
- Generated 11 screenshot-ready workbooks in `screenshot_tables/`.
- Added `table11_pca_explained_variance.xlsx` for PCA evidence.
- Word keeps table screenshot placeholders instead of large handwritten tables.

## Code Files

- Rechecked and reformatted the report code support files:
  - `report_code_snippets.md`
  - `appendix_A_complete_code.py`
  - `scripts/generate_final_report_figures.py`
  - `scripts/export_screenshot_tables.py`
- Fixed copyable code snippets so they use normal Markdown code fences and
  readable Python formatting.
- Confirmed the feature engineering formula is consistent:
  `activity_sleep_interaction = physical_activity_days * sleep_hours`.
- `appendix_A_complete_code.py` now runs from the repository root and regenerates
  final figures plus screenshot tables.

## Checks

- `py_compile` passed for the appendix code and generation scripts.
- `appendix_A_complete_code.py` ran successfully in the `qintian-DL` conda
  environment.
- The final DOCX was rebuilt successfully.
- Structural DOCX inspection passed:
  - 12 inserted images.
  - 11 table screenshot placeholders.
  - 8 core code placeholders.
  - No Abstract / Keywords / References / Chapter / static showcase / web_demo.
- Visual rendering was attempted, but this local environment has no LibreOffice
  / converter executable. Open the DOCX once in Word/WPS for final visual QA
  after inserting screenshots and code.
