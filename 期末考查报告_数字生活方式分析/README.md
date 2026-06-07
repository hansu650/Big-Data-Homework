# Big Data Analysis Final Report Project

题目：数字生活方式对身心风险与效率表现的影响分析--基于 2025 Digital Lifestyle Benchmark 数据集的分类、回归与聚类研究

本项目用于《大数据分析与应用》期末考查报告的实验代码、结果输出和 LaTeX 报告框架。项目坚持 CPU 运行、非深度学习方法、可复现实验设置，并统一使用 `random_state=42`。

## Project Structure

```text
final_report_project/
├─ data/
│  ├─ raw/
│  └─ processed/
├─ notebooks/
├─ src/
├─ figures/
├─ results/
├─ report/
│  ├─ sections/
│  └─ tables/
└─ requirements.txt
```

## Dataset

优先数据集为 Hugging Face 上的 2025 Digital Lifestyle Benchmark Dataset：

- Dataset page: https://huggingface.co/datasets/tarekmasryo/digital-lifestyle-benchmark-dataset
- Canonical CSV: `data/digital_lifestyle_benchmark_2025.csv`
- License: CC BY 4.0

`notebooks/00_dataset_selection_and_compliance.ipynb` 会下载原始 CSV 到 `data/raw/`，并输出数据来源、许可、字段检查和基础规模信息。若网络不可用，可以手动把 CSV 放入：

```text
data/raw/digital_lifestyle_benchmark_2025.csv
```

## Reproducibility

```bash
pip install -r requirements.txt
```

建议按下面顺序运行 notebook：

1. `notebooks/00_dataset_selection_and_compliance.ipynb`
2. `notebooks/01_data_preprocessing_and_eda.ipynb`
3. `notebooks/02_classification_high_risk.ipynb`
4. `notebooks/03_regression_productivity.ipynb`
5. `notebooks/04_clustering_lifestyle_profiles.ipynb`
6. `notebooks/05_result_summary_for_report.ipynb`

所有实验结果会保存为 CSV 到 `results/`，所有图表会保存为 PNG 到 `figures/`，方便在 LaTeX 报告中引用。

## Target Leakage Rule

分类任务预测 `high_risk_flag` 时，主模型不使用以下潜在泄漏或结果型变量：

```text
anxiety_score, depression_score, stress_level, happiness_score,
focus_score, productivity_score, digital_dependence_score
```

聚类任务也仅基于数字行为与生活习惯变量建模，身心风险和效率变量只在聚类后用于画像解释。

## Current Report Status

`report/` 目录只提供结构化 LaTeX 骨架、图表占位和方法说明。正式结论需要在真实模型结果跑完后再补写，避免提前编造实验结论。

