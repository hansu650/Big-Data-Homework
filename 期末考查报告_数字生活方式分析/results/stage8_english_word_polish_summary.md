# Stage 8 English Word Report Polish Summary

## 1. Scope

Stage 8 only updated the final Word report. It did not add experiments, rerun notebooks, modify any core results CSV files, or change the validated classification, regression, and clustering conclusions.

## 2. Template and Output

- Directly updated final DOCX: `期末考查报告_数字生活方式分析/final_submit/大数据分析与应用期末考查报告.docx`
- Word template used: `期末报告资料/课程模板/QinTian_experiment.docx`
- Additional report-generation script: `期末考查报告_数字生活方式分析/scripts/stage8_build_english_word_report.py`
- Generation stats: `期末考查报告_数字生活方式分析/results/stage8_word_generation_stats.json`

The final DOCX keeps the required Big Data course cover fields, including:

- Name: Big Data Analysis and Applications
- Content: Course Report
- Teacher: Li Jie
- Institution: blank placeholder
- Grade and major: blank placeholder
- Teacher's comments
- Total score
- Grading teacher

Student ID, Name, College, Major and Grade, Institution, and Grade and major remain blank placeholders.

## 3. English Version and Rubric Order

The final report body has been rewritten in English. The report keeps the teacher's seven grading-standard order:

1. Dataset Selection
2. Independent Research Theme and Analytical Perspective
3. Data Preprocessing
4. Exploratory Analysis and Data Visualization
5. Machine Learning Modeling, Hyperparameter Tuning, and Evaluation
6. Report Structure and Code Presentation
7. Conclusions and Personal Reflection

The report also includes References and Appendices A-D.

## 4. Teacher's Oral Requirements Explicitly Reinforced

The English version explicitly mentions and explains the following items:

- data cleaning
- feature extraction
- PCA extension
- LCA/GMM discussion
- statistical analysis from a mathematical perspective
- bar charts, histograms, line/curve plots, scatter plots, boxplots, and heatmaps
- modeling and evaluation visualization
- at least three machine learning task types: classification, regression, and clustering
- classification F1, Recall, PR-AUC, ROC-AUC, Balanced Accuracy, and confusion matrix
- clustering silhouette coefficient
- k selection with elbow method and silhouette curve
- cross-validation and GridSearchCV for supervised hyperparameter tuning
- core code snippets with explanations
- visualized conclusions and result boundaries

## 5. Core Metrics Kept Unchanged

The final English DOCX preserves the validated metrics:

- Classification: Gradient Boosting, threshold=0.14, Recall=0.6420, F1=0.5355, PR-AUC=0.5084.
- Main regression target: digital_dependence_score, R²=0.9839, MSE=3.1471, MAE=0.9982.
- Weak-prediction target: productivity_score, R²=-0.0041.
- Clustering: KMeans, k=3, Silhouette=0.1860.

The report continues to state that the classifier is a screening model rather than a medical diagnosis tool, that the high R² for digital_dependence_score is not causal evidence, that productivity_score is a weak-prediction/negative result, and that clustering is exploratory because the silhouette coefficient is low.

## 6. Inserted Artifacts

- Inserted figures by report counter: 20
- Embedded image relationships in DOCX: 20
- Inserted result/project tables by report counter: 12
- Total Word tables including cover and grading tables: 15
- Inserted code snippets: 8
- DOCX file size: 1,946,923 bytes

## 7. Automated Checks

Automated structural checks passed:

- AI course residue hits: 0
- LaTeX command residue hits: 0
- Disallowed Chinese body text snippets: 0 in the generation stats
- Required English chapter headings missing: 0
- Teacher oral requirement terms missing: 0
- Forbidden "Teacher Li", "Professor Li", or "Li Jie gave" phrasing: 0
- Personal placeholders preserved: yes
- Core metrics present: yes

The only Chinese text intentionally kept is the official course cover wording and blank personal-information field labels required by the template.

## 8. PDF and Render Check

PDF was not generated in this environment. The DOCX-to-PDF conversion and render check could not be completed because LibreOffice/soffice and a usable Microsoft Word COM backend were not available.

A render attempt with the local document renderer failed at the conversion step because the converter executable could not be found. Therefore, this stage does not claim completed visual PDF QA.

## 9. Remaining Manual Operations

Before final submission, manually complete the following:

1. Open `final_submit/大数据分析与应用期末考查报告.docx` in Word or WPS.
2. Fill in Student ID, Name, College, Major and Grade, Institution, and Grade and major.
3. Check the cover, abstract, table of contents, visualization pages, modeling-result pages, references, and appendices.
4. Confirm that figures display normally and tables do not overflow seriously.
5. Export the DOCX as PDF manually if a PDF is required.

