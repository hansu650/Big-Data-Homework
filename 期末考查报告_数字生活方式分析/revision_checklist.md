# Revision Checklist

All checks below refer to the current workflow-style Word report and supporting
files generated after the small fix pass.

| # | Check item | Result |
|---|---|---|
| 1 | DOCX has no Abstract. | PASS |
| 2 | DOCX has no Keywords. | PASS |
| 3 | DOCX has no References. | PASS |
| 4 | DOCX has only Appendix A. | PASS |
| 5 | DOCX has no Appendix B/C/D. | PASS |
| 6 | DOCX has no Chapter word. | PASS |
| 7 | DOCX has no static showcase / web_demo / HTML preview. | PASS |
| 8 | DOCX has no project-structure screenshot placeholder. | PASS |
| 9 | DOCX has no notebook screenshot placeholder. | PASS |
| 10 | Figure numbering is Fig1, Fig2, Fig3... | PASS |
| 11 | Table numbering is Table1, Table2, Table3... | PASS |
| 12 | No Figure 4-1 / Figure 5-10 / Table C-1 remains. | PASS |
| 13 | High Risk and No Risk labels are used instead of 0/1 wherever appropriate. | PASS |
| 14 | ID distribution plot is not used. | PASS |
| 15 | Every figure has Purpose / Interpretation / Conclusion. | PASS |
| 16 | Every screenshot table has Purpose / Interpretation / Conclusion. | PASS |
| 17 | report_code_snippets.md has real Markdown line breaks and code fences. | PASS |
| 18 | appendix_A_complete_code.py has real Python line breaks and passes py_compile. | PASS |
| 19 | generate_final_report_figures.py passes py_compile. | PASS |
| 20 | export_screenshot_tables.py passes py_compile. | PASS |
| 21 | appendix_A_complete_code.py can run from the repository root. | PASS |
| 22 | Excel screenshot tables are generated successfully. | PASS |
| 23 | Final figures are generated successfully. | PASS |
| 24 | No ~$*.xlsx or ~$*.docx temporary files remain. | PASS |
| 25 | Core classification metrics unchanged: Recall=0.6420, F1=0.5355, PR-AUC=0.5084. | PASS |
| 26 | Core regression metrics unchanged: R²=0.9839, MSE=3.1471, MAE=0.9982. | PASS |
| 27 | productivity_score R²=-0.0041 is kept and explained as weak prediction. | PASS |
| 28 | KMeans k=3 and Silhouette=0.1860 are unchanged. | PASS |
| 29 | PCA first two components explain about 42.41% variance. | PASS |
| 30 | The final Word report can be opened by python-docx structural inspection. | PASS |
| 31 | DOCX contains 12 inserted figures and 11 screenshot-table placeholders. | PASS |
| 32 | Visual DOCX rendering was attempted. | PASS WITH NOTE: local converter / LibreOffice is unavailable in this environment. |

## Notes

- The report remains in the standard workflow order: Research Objective and Task
  Design -> Dataset Description and Task Feasibility -> Data Preprocessing and
  Feature Construction -> Statistical Exploration and Visualization -> Modeling,
  Tuning, and Evaluation -> Findings, Limitations, and Reflection -> Appendix A.
- The core results CSV files were not redesigned or replaced.
- Final visual layout should still be opened once in Word/WPS after manual
  screenshot and code insertion.
