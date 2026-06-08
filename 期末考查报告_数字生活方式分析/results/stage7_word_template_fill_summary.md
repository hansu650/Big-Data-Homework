# Stage 7 Word 模板填充总结

## 1. 本阶段目标

本阶段只进行 Word 模板填充、排版迁移、图表插入和结构检查；未新增实验，未重跑 notebook，未修改任何 results/*.csv 核心指标，也未改变分类、回归、聚类核心结论。

## 2. 输入与输出

- 使用的 Word 模板：`C:\Users\qintian\Downloads\examination report.docx`
- 正文依据：`期末考查报告_数字生活方式分析/overleaf_final/`
- 最终 DOCX：`期末考查报告_数字生活方式分析/final_submit/大数据分析与应用期末考查报告.docx`
- PDF 生成情况：未生成。

PDF 未生成原因：当前环境未检测到 LibreOffice/soffice、Microsoft Word COM 或其他可用 DOCX 转 PDF 后端。已尝试使用文档渲染工具进行转换检查，但转换依赖缺失，因此未完成本地 PDF 渲染。建议在 Word/WPS 中打开最终 DOCX 后另存为 PDF。

## 3. 内容迁移情况

- 使用 Stage 6 LaTeX 内容作为正文来源：是。
- 保留老师 7 项评分标准顺序：是。
- 保留大数据课程考查报告封面信息：是。
- 替换人工智能课程模板内容：是。
- 保留个人信息下划线占位：是。
- 插入核心图片：20 张。
- 插入核心表格：10 张。
- 插入核心代码片段：7 段。

最终 Word 章节顺序为：

1. 数据集自主选取
2. 自主选题与分析视角
3. 数据预处理
4. 探索性分析与数据可视化
5. 机器学习建模、调参与模型评估
6. 报告架构与代码规范呈现
7. 实验结论与个人反思
8. 参考文献
9. 附录A-D

## 4. 核心结论一致性

Word 版保留 Stage 6 的核心指标与边界表述：

- 分类任务：Gradient Boosting，threshold=0.14，Recall=0.6420，F1=0.5355，PR-AUC=0.5084。
- 回归主线：digital_dependence_score，R²=0.9839，MSE=3.1471，MAE=0.9982。
- 生产力弱预测：productivity_score，R²=-0.0041。
- 聚类任务：KMeans k=3，Silhouette=0.1860，仅作为探索性用户画像。
- 数据性质：合成教学/benchmark 数据，不用于医学诊断、个体健康判断或因果推断。

## 5. 自动检查结果

- DOCX 文件大小：2012192 bytes。
- Word 段落数：383。
- Word 表格数：13，其中正文核心结果表 10 个，封面与评分表 3 个。
- DOCX 内嵌图片关系数：21。
- 必需章节标题缺失数量：0。
- 人工智能课程残留词检查：0。
- LaTeX 命令残留检查：0。
- TODO/placeholder/Missing figure 检查：0。
- 大数据课程信息检查：通过。
- 报告题目检查：通过。
- 个人信息占位检查：通过。

检查过的人工智能课程残留词包括：人工智能技术与应用、CampusDepthSegLite、RGB-D、NYUDepthV2、PyTorch、王雷春、湖北大学本科课程设计、语义分割、校园室内巡检。

检查过的 LaTeX 残留包括：`\chapter`、`\section`、`\texttt`、`\input`、`\maybefigure`、Missing figure、placeholder、TODO。

## 6. 渲染检查说明

已尝试使用文档渲染脚本将 DOCX 转换为 PDF 进行页面抽查，但本机缺少可用转换器，转换失败。由于无法生成 PDF 页面截图，本阶段未声称完成视觉渲染 QA。

建议最终提交前人工执行：

1. 用 Word 或 WPS 打开 `final_submit/大数据分析与应用期末考查报告.docx`。
2. 检查封面、摘要、目录、第 4 章图表页、第 5 章建模结果页、参考文献和附录。
3. 确认图片显示正常、表格未严重超页、中文无乱码。
4. 填写姓名、学号、学院、专业年级、Institution、Grade and major。
5. 另存为 PDF，作为最终提交 PDF。

## 7. 仍需人工填写的信息

- 学号
- 姓名
- 学院
- 专业年级
- Institution
- Grade and major
- Teacher's comments、Total score、Grading teacher 由任课教师填写

