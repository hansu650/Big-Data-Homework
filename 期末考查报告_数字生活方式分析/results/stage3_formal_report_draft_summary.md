# Stage 3 Formal LaTeX Report Draft Summary

生成日期：2026-06-07

## 本阶段范围

本阶段基于 commit `6fe97f3` 后的 `期末考查报告_数字生活方式分析/` 项目撰写正式 LaTeX 报告正文初稿。未新增实验，未重跑分类、回归或聚类主模型，未改变 `results/` 中已有核心指标。

## 已完成内容

1. 新增课程封面页：`report/sections/00_cover.tex`。
2. 替换 `report/main.tex` 中的 placeholder 摘要，并补充关键词。
3. 完成 9 个正文章节和附录初稿：
   - 研究背景与问题定义；
   - 数据集选择与合规性说明；
   - 数据预处理；
   - 探索性分析与数据可视化；
   - 分类实验：高风险数字生活方式筛查；
   - 回归实验：数字依赖预测与生产力弱预测检验；
   - 聚类实验：数字生活方式用户画像分析；
   - 综合结果分析与业务建议；
   - 总结与个人反思；
   - 附录：核心代码与复现实验说明。
4. 新增正文精简表：
   - `report/tables/dataset_compliance_summary.tex`
   - `report/tables/preprocessing_quality_check_compact.tex`
   - `report/tables/pca_explained_variance_compact.tex`
5. 将宽表改为适合正文排版的 LaTeX 表格，并保留 CSV 原始结果作为指标来源。

## 核心结果写入口径

- 分类任务：最终采用 Gradient Boosting，threshold=0.14，测试集 Recall=0.6420，F1=0.5355，PR-AUC=0.5084。
- 回归任务主线：`digital_dependence_score`，最佳模型 Gradient Boosting，R2=0.9839，MSE=3.1471，MAE=0.9982。
- 生产力得分：`productivity_score` 的最佳 R2=-0.0041，正文写作中明确作为弱预测/负结果分析。
- 聚类任务：KMeans k=3，Silhouette=0.1860，正文中明确写作探索性画像，不写成天然清晰分群。

## 图表覆盖

已根据 `results/final_report_figure_selection.csv` 覆盖全部 20 张推荐图：

- 正文图：16 张；
- 附录图：4 张；
- 选择清单中未被引用的图：0 张。

正文和附录使用了 `results/final_report_table_selection.csv` 中的主要表格材料。分类和回归的完整调参 CSV 作为附录电子材料说明，不在正文中直接铺开宽表。

## LaTeX 静态检查

按用户要求，本阶段没有编译 PDF，只做 Overleaf 前的 LaTeX 静态检查：

- `main.tex` 不再包含 placeholder 摘要；
- `\input` 文件缺失数量：0；
- `\maybefigure` 引用图片缺失数量：0；
- `\begin{...}` 数量：39；
- `\end{...}` 数量：39；
- 摘要长度静态计数：490 个字符，满足 300--500 字要求。

## 说明

正文所有核心指标均来自现有 `results/` 文件或对应报告表格，没有编造指标。报告未将模型写作医学诊断工具，未写因果化结论，且明确说明数据集为合成数据。
