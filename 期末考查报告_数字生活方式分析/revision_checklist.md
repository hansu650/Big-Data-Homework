# Revision Checklist

This checklist is for the current workflow-style Word report and supporting
evidence files.

| # | Check item | Result |
|---|---|---|
| 1 | DOCX has no Abstract. | PASS |
| 2 | DOCX has no Keywords. | PASS |
| 3 | DOCX has no References. | PASS |
| 4 | DOCX has no Chapter word. | PASS |
| 5 | DOCX has only Appendix A. | PASS |
| 6 | DOCX has no Appendix B/C/D. | PASS |
| 7 | DOCX has no static showcase / web_demo / HTML preview. | PASS |
| 8 | DOCX has no project-structure screenshot or notebook screenshot placeholder. | PASS |
| 9 | Figures are numbered Fig1, Fig2, Fig3... | PASS |
| 10 | Tables are numbered Table1, Table2, Table3... in first-appearance order. | PASS |
| 11 | Every figure has Purpose / Interpretation / Conclusion. | PASS |
| 12 | Every screenshot table has Purpose / Interpretation / Conclusion. | PASS |
| 13 | High Risk and No Risk labels are used instead of 0/1 where appropriate. | PASS |
| 14 | No id distribution plot is used. | PASS |
| 15 | Table screenshot Excel files can be opened normally. | PASS |
| 16 | Excel files have clear sheet names, frozen header row, readable column widths. | PASS |
| 17 | No ~$*.xlsx or ~$*.docx temporary files remain. | PASS |
| 18 | report_code_snippets.md has real Markdown line breaks and code fences. | PASS |
| 19 | appendix_A_complete_code.py has real Python line breaks. | PASS |
| 20 | appendix_A_complete_code.py passes py_compile. | PASS |
| 21 | export_screenshot_tables.py passes py_compile. | PASS |
| 22 | generate_final_report_figures.py passes py_compile. | PASS |
| 23 | Core classification metrics unchanged: Recall=0.6420, F1=0.5355, PR-AUC=0.5084. | PASS |
| 24 | Core regression metrics unchanged: R²=0.9839, MSE=3.1471, MAE=0.9982. | PASS |
| 25 | productivity_score R²=-0.0041 is kept and explained as weak prediction. | PASS |
| 26 | KMeans k=3 and Silhouette=0.1860 are unchanged. | PASS |
| 27 | PCA first two components explain about 42.41% variance. | PASS |
| 28 | The conclusion forms a clear workflow loop from preprocessing to EDA to modeling to reflection. | PASS |
| 29 | screenshot_todo.md tells the student exactly which Excel/table/code to insert. | PASS |
| 30 | Final Word report opens normally by python-docx structural inspection. | PASS |

## Structural QA Notes

- The DOCX contains 12 inserted figures.
- The DOCX contains 12 screenshot-table placeholders.
- The DOCX contains 7 main-text code placeholders and one Appendix A complete-code placeholder.
- `appendix_A_complete_code.py` ran successfully from the repository root in the
  `qintian-DL` conda environment.
- The local environment still has no LibreOffice / converter executable, so
  final visual rendering should be checked in Word/WPS after manual screenshot
  and code insertion.
