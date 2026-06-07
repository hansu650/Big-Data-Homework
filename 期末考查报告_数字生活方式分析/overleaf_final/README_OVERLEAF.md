# Overleaf 编译说明

本目录是《大数据分析与应用》期末考查报告的 Overleaf 自包含编译包。

## 上传方式

将 `overleaf_final/` 目录中的全部文件上传到 Overleaf 项目根目录，保持以下结构：

```text
main.tex
sections/
tables/
figures/
README_OVERLEAF.md
```

不要额外上传 `notebooks/`、`data/`、`results/` 或原始数据文件。

## 编译方式

在 Overleaf 中选择：

```text
Compiler: XeLaTeX
Main document: main.tex
```

建议至少连续编译两次，以更新目录、图表编号和交叉引用。

## 内容说明

- `main.tex` 已使用 `\graphicspath{{figures/}}`，图片从 `figures/` 目录读取。
- `sections/` 保存正文各章节。
- `tables/` 保存正文精简表和附录精简表。
- `figures/` 只包含报告实际引用的 20 张图片。
- 完整实验代码、notebook、CSV 结果和原始数据仍保留在仓库项目目录中，不放入本 Overleaf 包。

## 注意事项

本报告正文中的指标来自项目 `results/` 目录下已有结果文件。Overleaf 包只用于排版编译，不用于重新运行实验。
