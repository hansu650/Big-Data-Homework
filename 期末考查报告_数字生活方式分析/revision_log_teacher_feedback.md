# Teacher Feedback Revision Log

## Source DOCX

- Actual source DOCX: `C:\Users\qintian\Downloads\EEE大数据分析与应用期末考查报告.docx`
- Project backup: `C:\Users\qintian\Desktop\大数据\Big-Data-Homework\期末考查报告_数字生活方式分析\final_submit\EEE大数据分析与应用期末考查报告_源文件备份.docx`
- Pre-edit backup: `C:\Users\qintian\Desktop\大数据\Big-Data-Homework\期末考查报告_数字生活方式分析\final_submit\大数据分析与应用期末考查报告_修改前备份.docx`
- Final revised DOCX: `C:\Users\qintian\Desktop\大数据\Big-Data-Homework\期末考查报告_数字生活方式分析\final_submit\大数据分析与应用期末考查报告_老师反馈修改版.docx`

## Deleted or Replaced Items

- Removed the model-comparison Excel screenshots from the formal body.
- Table10 Classification Model Comparison and Threshold Results was replaced by Fig5.
- Table11 Regression Model Comparison was replaced by Fig11.
- Table12 Clustering Model Comparison and Cluster Profiles was replaced by Fig12 and Fig13.
- Removed the mechanical Summary / Purpose / Observation / Meaning blocks and rewrote figure/table interpretations as continuous English analysis paragraphs.

## New or Replaced Formal Analysis Figures

- Fig5 Classification Model Comparison at the Default Threshold.
- Fig11 Regression R2 Comparison by Target.
- Fig12 K Selection by Inertia and Silhouette.
- Fig4 was regenerated with Cohen's d annotations and is supported by `results/high_risk_group_comparison.csv`.
- Fig8 Precision-Recall Curve now includes a no-skill baseline.

## Numbering Changes

- Final tables are Table1-Table9 only.
- Final figures are Fig1-Fig14.
- Old Table10, Table11, and Table12 no longer appear in the revised DOCX body.

## Fig4 Evidence

- Variables used: device_hours_per_day, phone_unlocks, notifications_per_day, social_media_mins, sleep_hours, digital_dependence_score.
- Strongest standardized difference: device_hours_per_day, followed by digital_dependence_score and sleep_hours.
- Full group statistics are saved in `results/high_risk_group_comparison.csv`.

## QA

- Visual audit CSV: `results/report_visual_audit.csv`.
- Structural check: `{'forbidden_hits': {}, 'figure_count': 14, 'table_count': 9, 'visible_inline_shapes': 14, 'metrics_ok': True, 'has_high_no_risk': True}`.
- Render status: PDF render not available in this environment: Command '['powershell', '-NoProfile', '-Command', "$word = New-Object -ComObject Word.Application; $word.Visible = $false; $doc = $word.Documents.Open('C:\\Users\\qintian\\Desktop\\大数据\\Big-Data-Homework\\期末考查报告_数字生活方式分析\\final_submit\\大数据分析与应用期末考查报告_老师反馈修改版.docx'); $doc.SaveAs([ref] 'C:\\Users\\qintian\\Desktop\\大数据\\Big-Data-Homework\\期末考查报告_数字生活方式分析\\final_submit\\大数据分析与应用期末考查报告_老师反馈修改版.pdf', [ref] 17); $doc.Close(); $word.Quit();"]' returned non-zero exit status 1.

## Core Metrics

- Classification: Gradient Boosting, threshold=0.14, Recall=0.6420, F1=0.5355, PR-AUC=0.5084, ROC-AUC=0.7531, Balanced Accuracy=0.7259, TN=566, FP=133, FN=63, TP=113.
- digital_dependence_score regression: Gradient Boosting, R2=0.9839, MSE=3.1471, MAE=0.9982.
- productivity_score: R2=-0.0041, kept as weak prediction.
- Clustering: KMeans k=3, Silhouette=0.1860, exploratory lifestyle profiles only.
- PCA: PC1+PC2 cumulative explained variance = 42.41%.
