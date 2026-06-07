# Stage 2.6 Pre-writing Cleanup Summary

生成日期：2026-06-07

## 本次清理范围

本次仅进行写作前证据与文本一致性清理，不新增核心建模实验，不重新设计分类、回归或聚类流程，也不改变第二阶段已经形成的模型结果与结论口径。

## 标题统一

项目标题已统一为：

《数字生活方式下的高风险识别、数字依赖预测与用户画像分析——基于 2025 Digital Lifestyle Benchmark 数据集的分类、回归与聚类研究》

已检查并同步的位置：

- `README.md`
- `report/main.tex`
- `report/sections/01_introduction.tex`
- `report/sections/06_regression.tex`
- `report/sections/07_clustering.tex`
- `report/sections/08_discussion.tex`

检查后未发现旧标题“数字生活方式对身心风险与效率表现的影响分析”的完整残留。

## 代码检查

已运行：

```bash
python -m py_compile src/*.py scripts/*.py
```

实际执行时使用 `conda run -n qintian-DL` 和 PowerShell 展开文件列表。检查通过，未发现 Python 语法错误。

## Stage 2.5 证据脚本复现

已运行：

```bash
python scripts/stage2_5_evidence_enhancement.py
```

脚本成功重新生成以下关键文件：

- `results/preprocessing_quality_check.csv`
- `results/pca_explained_variance.csv`
- `figures/pca_explained_variance.png`
- `results/final_report_figure_selection.csv`
- `results/final_report_table_selection.csv`

同时脚本也重新生成了 `results/preprocessing_quality_check.md` 和 `results/stage2_5_evidence_enhancement_summary.md`。

## 图表与表格清单存在性检查

已检查 `results/final_report_figure_selection.csv` 和 `results/final_report_table_selection.csv` 中列出的 `artifact_path` 是否真实存在。

检查结果：

- 图表清单：20 项，建议进入正文 16 项，建议进入附录 4 项，缺失 0 项。
- 表格清单：12 项，建议进入正文 9 项，建议进入附录 3 项，缺失 0 项。

## 对核心实验结果的影响

本次清理没有重新运行分类、回归、聚类主实验，没有新增模型，没有引入深度学习或 LCA，也没有改变已有核心指标文件中的模型结果。

当前材料已经具备进入正式报告写作的基础：预处理质量证据、PCA 辅助说明、最终报告图表筛选清单和 Stage 2 模型结果可以直接用于后续正文撰写。
