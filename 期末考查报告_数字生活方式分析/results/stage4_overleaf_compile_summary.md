# Stage 4 Overleaf Compile Package Summary

生成日期：2026-06-07

## 本阶段范围

本阶段只进行 Overleaf 编译包整理、LaTeX 路径修正、图片表格排版和封面格式微调。未新增实验，未重跑分类、回归或聚类主模型，未修改 `results/` 中任何分类、回归、聚类核心 CSV 指标。

## Overleaf 自包含目录

已创建：

```text
overleaf_final/
├─ main.tex
├─ main.pdf
├─ sections/
├─ tables/
├─ figures/
└─ README_OVERLEAF.md
```

该目录未复制 notebooks、raw data、processed data 或 results CSV。完整实验材料仍保留在项目主目录。

## 图片复制与引用检查

- 从项目 `figures/` 复制报告实际引用图片：20 张。
- 正文图数量：16 张。
- 附录图数量：4 张。
- `overleaf_final/main.tex` 已改为 `\graphicspath{{figures/}}`。
- `\maybefigure` 已改为从 `figures/#1` 检查并读取图片。
- 静态检查结果：引用图片缺失数量为 0。
- PDF 视觉抽查页面包括封面、摘要、目录、正文表格页、EDA 图页、分类图页和附录页，未发现图片缺失或空白图。

## 表格与正文格式检查

已检查以下正文核心表：

- `classification_threshold_tuning.tex`
- `classification_tuned_metrics.tex`
- `regression_target_comparison.tex`
- `regression_digital_dependence_metrics.tex`
- `regression_productivity_metrics.tex`
- `clustering_model_comparison.tex`
- `clustering_lifestyle_profiles_compact.tex`
- `preprocessing_quality_check_compact.tex`
- `dataset_compliance_summary.tex`

宽表已使用 `\resizebox{\textwidth}{!}{...}` 或正文精简列。正文未放入完整调参大表或完整聚类画像大表；完整 CSV 结果仅在附录和说明中作为电子材料引用。

## 变量名与封面检查

- 未发现 `\_ ` 形式的变量名错误空格。
- 已检查重点变量：`high_risk_flag`、`digital_dependence_score`、`productivity_score`、`device_hours_per_day`、`notifications_per_day`、`phone_unlocks`、`social_media_mins`、`sleep_hours`、`sleep_quality`。
- 封面包含湖北大学课程考查试题纸、英文说明、课程名、报告内容、教师、题目、学号、姓名、学院、专业年级。
- 学号、姓名、学院、专业年级均保留下划线占位，未编造个人信息。
- `overleaf_final/main.tex` 中无 `\maketitle`，避免双封面。
- 封面、摘要和目录分别独立起页。

## 编译结果

本机未检测到 `xelatex` 或 `latexmk`，但检测到 Tectonic。已在 `overleaf_final/` 中使用 Tectonic 成功编译：

```bash
tectonic --keep-logs --keep-intermediates main.tex
```

输出 PDF：

```text
overleaf_final/main.pdf
```

PDF 文件大小：2,379,084 bytes。

编译日志中未出现 Missing、Undefined、Error 或 Overfull 提示；仅有若干 Underfull hbox 断行松散提示，不影响 PDF 内容显示。编译完成后已清理 LaTeX 中间文件和临时渲染检查图，仅保留 `main.pdf`。

## 最终静态检查

最终静态检查全部通过：

- `overleaf_final/main.tex` 存在；
- `sections/*.tex` 存在，数量 11；
- `tables/*.tex` 存在，数量 13；
- `figures/` 中存在全部 20 张被引用图片；
- 不存在 `Missing figure` 文本；
- 不存在 placeholder 摘要；
- 不存在 TODO；
- 不存在变量名中的 `\_ ` 错误空格；
- `\begin{...}` 数量为 39，`\end{...}` 数量为 39；
- `main.pdf` 存在且大小大于 0。

## Overleaf 上传说明

将 `overleaf_final/` 中全部文件上传到 Overleaf 项目根目录，选择：

```text
Compiler: XeLaTeX
Main document: main.tex
```

建议连续编译两次，以刷新目录和交叉引用。若 Overleaf 提示 underfull hbox，可忽略；若提示缺图，请确认 `figures/` 目录与 `main.tex` 位于同一项目根目录。
