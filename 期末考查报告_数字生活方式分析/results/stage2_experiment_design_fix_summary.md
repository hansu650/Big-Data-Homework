# Stage 2 Experiment Design Fix Summary

## 1. 修复内容

本阶段补充了分类调参、分类阈值选择、双目标回归、聚类算法对比、聚类特征范围控制、EDA 图表和报告表格简化。所有新增结果均由 notebook 真实运行生成。

## 2. 分类调参和阈值调优结果

分类任务继续预测 `high_risk_flag`，并严格排除心理状态、效率、数字依赖、ID 和目标列。调参结果保存为 `results/classification_cv_results.csv`，阈值调优结果保存为 `results/classification_threshold_tuning.csv`。

测试集上当前综合 F1 较高的策略为 `recall_at_least_60_best_precision`，模型为 `gradient_boosting`，threshold=0.14，Precision=0.4593，Recall=0.6420，F1=0.5355，PR-AUC=0.5084，ROC-AUC=0.7531。

## 3. productivity_score 是否仍然弱预测

productivity_score 当前最佳模型为 `gradient_boosting`，R2=-0.0041，MSE=85.2031，RMSE=9.2306，MAE=7.1671。

该目标在当前特征下仍然属于弱预测或负结果，不能写成数字行为可以有效预测生产力。

## 4. digital_dependence_score 是否更适合作为回归主线

digital_dependence_score 当前最佳模型为 `gradient_boosting`，R2=0.9839，MSE=3.1471，RMSE=1.7740，MAE=0.9982。

digital_dependence_score 的效果优于 productivity_score，更适合作为回归主线；productivity_score 可作为辅助负结果分析。

## 5. 聚类特征范围

聚类已经改成只使用数字行为和生活习惯数值特征，不再把 gender、region、income_level、education_level、daily_role、device_type 等背景类别变量放入聚类训练。背景类别和结果变量只用于聚类后画像解释。

## 6. 聚类算法对比结果

聚类比较结果保存为 `results/clustering_model_comparison.csv`。当前 Silhouette 最高的模型为 `kmeans`，k=3，Silhouette=0.1860，Calinski-Harabasz=611.1770，Davies-Bouldin=1.7959。

轮廓系数仍然偏低，聚类只能作为探索性画像，不能作为严格人群边界。

## 7. 可以进入正式报告的结果

- 数据集合规性、字段结构、样本规模和合成数据限制。
- 分类任务的泄漏控制、调参流程、PR-AUC/ROC-AUC、阈值调优和混淆矩阵。
- digital_dependence_score 回归结果，如果其 R2 明显优于 productivity_score。
- 聚类输入特征白名单、算法对比和简化画像表。

## 8. 需要谨慎解释的结果

- productivity_score 若 R2 接近 0 或为负，只能作为弱预测/负结果分析。
- 聚类 Silhouette 若低于 0.20，只能写探索性用户画像，不写严格分群边界。
- 所有 EDA 相关性图只支持描述性分析，不支持因果结论。
