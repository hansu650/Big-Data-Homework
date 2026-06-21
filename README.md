# Big Data Homework

This repository collects coursework, experiment materials, and the final course project for **Big Data Analysis and Applications**.

## Featured Final Project

> **Digital Lifestyle Analysis:**<br>
> **High-Risk Screening, Digital Dependence Prediction, and Lifestyle Profile Clustering**

The final project analyzes a 2025 Digital Lifestyle Benchmark Dataset with a complete data-analysis workflow: dataset checking, preprocessing, feature engineering, EDA, classification, regression, clustering, and final report writing.

**Quick links**

| Item | Link |
|---|---|
| GitHub project page | [Open the final project folder on GitHub](https://github.com/hansu650/Big-Data-Homework/tree/main/%E6%9C%9F%E6%9C%AB%E8%80%83%E6%9F%A5%E6%8A%A5%E5%91%8A_%E6%95%B0%E5%AD%97%E7%94%9F%E6%B4%BB%E6%96%B9%E5%BC%8F%E5%88%86%E6%9E%90) |
| Final project folder | [期末考查报告_数字生活方式分析/](期末考查报告_数字生活方式分析/) |
| Final PDF report | [final_submit/大数据分析与应用期末考查报告.pdf](期末考查报告_数字生活方式分析/final_submit/大数据分析与应用期末考查报告.pdf) |
| Final Word report | [final_submit/大数据分析与应用期末考查报告.docx](期末考查报告_数字生活方式分析/final_submit/大数据分析与应用期末考查报告.docx) |
| Complete runnable code | [appendix_A_complete_code.py](期末考查报告_数字生活方式分析/appendix_A_complete_code.py) |

### Project Tasks

- **High Risk classification**: screen `high_risk_flag` with a recall-oriented threshold.
- **Digital dependence regression**: predict `digital_dependence_score`.
- **Lifestyle clustering**: summarize digital lifestyle profiles with clustering methods.

### Locked Key Results

| Task | Final result |
|---|---|
| Classification | Gradient Boosting, threshold=0.14, Recall=0.6420, F1=0.5355, PR-AUC=0.5084 |
| Digital dependence regression | R²=0.9839, MSE=3.1471, MAE=0.9982 |
| Productivity regression | R²=-0.0041 |
| Clustering | KMeans k=3, Silhouette=0.1860 |
| PCA | PC1+PC2=42.41% |

## Repository Layout

| Path | Description |
|---|---|
| `期末考查报告_数字生活方式分析/` | Final course project with data, notebooks, code, figures, results, and final submission files. |
| `期末报告资料/` | Course report materials, templates, references, and related datasets. |
| `实验一/`, `实验二/`, `实验三/`, `实验四/` | Course experiment folders and related materials. |
| `3-13/`, `3-20/`, `3-27/`, `4-3/`, `4-10/` | Date-organized coursework or class-stage materials. |
| `历史零散文件/` | Archived older local files collected from the original workspace. |

## Notes

The final project keeps the core experiment values fixed and documents both strong and weak results. The High Risk classifier is used as a screening reference, digital dependence regression is interpreted as prediction rather than causality, productivity prediction is treated as a weak result, and clustering is used for exploratory profile analysis.
