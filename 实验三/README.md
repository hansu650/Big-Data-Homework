# Experiment 3: Classification Model Practice

本目录是《大数据分析与应用》实验三，主题是基于员工历史信息预测员工是否可能离职。实验使用实验二已经预处理好的数据，建立并比较多个传统机器学习分类模型。

## 1. 实验任务简介

根据影响员工离职的因素和历史离职记录，分别建立多个分类模型，用于预测员工是否可能离职，并对模型进行评价。

本实验包含四个模型：

1. **Information Gain Decision Tree**  
   使用 `DecisionTreeClassifier(criterion="entropy")`，通过信息熵和信息增益选择划分特征。

2. **Gini Index Decision Tree**  
   使用 `DecisionTreeClassifier(criterion="gini")`，通过 Gini impurity 选择划分特征。

3. **Naive Bayes**  
   使用 `GaussianNB()`，适合做简单、快速的概率分类基线模型。

4. **Support Vector Machine**  
   使用 `Pipeline([("scaler", StandardScaler()), ("svm", SVC(kernel="rbf", probability=True))])`。SVM 前使用标准化，因为 SVM 对特征尺度比较敏感。

## 2. 为什么决策树分成两种模型

Decision Tree 可以使用不同的节点划分标准。本实验分别使用：

- **Information Gain / Entropy**：更接近课堂中信息增益的决策树理论。
- **Gini Index**：CART 决策树中常见的划分标准。

两者都是决策树模型，但特征选择标准不同，所以在验证集上的结果、树结构和特征重要性可能不同。

## 3. 为什么用 validation set 评价模型

实验二目录中有：

- `../实验二/X_train_preprocessed.csv`
- `../实验二/y_train_preprocessed.csv`
- `../实验二/X_test_preprocessed.csv`

但目前没有 `y_test_preprocessed.csv`，所以 `X_test_preprocessed.csv` 没有真实标签，不能用于计算 accuracy、precision、recall、F1-score 等评价指标。

因此，本实验从 `X_train_preprocessed.csv` 和 `y_train_preprocessed.csv` 中重新划分：

- training set: 80%
- validation set: 20%

模型评价全部在 validation set 上完成。`X_test_preprocessed.csv` 只用于生成最终预测结果 `test_predictions.csv`。

## 4. CPU 和依赖说明

本实验使用 sklearn 的传统机器学习模型，只需要 CPU，不使用 GPU。

没有使用 cuML、RAPIDS、PyTorch 或其他 GPU 框架。这样更适合课程实验复现，也方便在普通电脑上运行。

安装依赖：

```bash
pip install numpy pandas matplotlib scikit-learn
```

本实验没有使用 seaborn。

## 5. 运行 Python 脚本

在仓库根目录运行：

```bash
python 实验三/experiment3_classification_models.py
```

或进入实验三目录运行：

```bash
cd 实验三
python experiment3_classification_models.py
```

脚本会自动读取实验二的预处理数据，并生成 `results/` 和 `figures/` 中的所有文件。

## 6. 运行 Notebook

打开：

```text
实验三/experiment3_classification_models.ipynb
```

然后从上到下运行所有单元格即可。Notebook 会分步骤展示数据读取、检查清洗、模型训练、模型评价、图表生成、错误分析和最终预测。

`experiment3_classification_models.py` 是主版本，Notebook 复用同一套函数并拆成多个步骤展示，所以两者使用同一套数据、同一套模型、同一套评价指标和同一套输出结果。

## 7. results/ 文件说明

`results/model_evaluation_results.csv`

- 四个模型的整体评价指标。
- 包含 accuracy、precision、recall、f1_score、roc_auc、pr_auc、training_score、validation_score、overfitting_gap、training_time_seconds、prediction_time_seconds。
- 也保存了 confusion matrix 的 TN、FP、FN、TP 数值。

`results/classification_report_all_models.txt`

- 四个模型的 classification report。
- 同时包含每个模型的 confusion matrix。

`results/validation_predictions_all_models.csv`

- validation set 上每条样本的真实标签。
- 每个模型的预测标签。
- 每个模型对 positive class 的预测概率或 score。

`results/test_predictions.csv`

- 对 `X_test_preprocessed.csv` 的最终预测结果。
- 因为没有真实标签，所以这里只保存预测标签和 positive probability / score，不计算模型评价指标。

`results/model_runtime_results.csv`

- 每个模型的训练时间和预测时间。

`results/model_ranking_summary.csv`

- 模型排名总结。
- 包含 best_accuracy_model、best_precision_model、best_recall_model、best_f1_model、best_roc_auc_model、best_pr_auc_model、fastest_training_model、largest_overfitting_gap_model。

## 8. figures/ 图片说明

`01_target_distribution.png`

- 目标变量类别分布图。

`02_feature_correlation_heatmap.png`

- 特征相关性热力图。
- 如果特征较多，只选方差最大的前 25 个特征。

`03_model_metrics_comparison.png`

- 四个模型的 accuracy、precision、recall、F1-score、ROC-AUC、PR-AUC 对比图。

`04_confusion_matrix_entropy_tree.png`

- Information Gain Decision Tree 的混淆矩阵。

`05_confusion_matrix_gini_tree.png`

- Gini Index Decision Tree 的混淆矩阵。

`06_confusion_matrix_naive_bayes.png`

- Naive Bayes 的混淆矩阵。

`07_confusion_matrix_svm.png`

- Support Vector Machine 的混淆矩阵。

`08_roc_curves_all_models.png`

- 四个模型 ROC 曲线对比图。

`09_pr_curves_all_models.png`

- 四个模型 Precision-Recall 曲线对比图。

`10_entropy_tree_structure.png`

- Information Gain Decision Tree 的树结构图。
- 可视化限制 `max_depth=3`，便于放入报告。

`11_gini_tree_structure.png`

- Gini Index Decision Tree 的树结构图。
- 可视化限制 `max_depth=3`。

`12_entropy_tree_feature_importance.png`

- Information Gain Decision Tree 的前 20 个重要特征。

`13_gini_tree_feature_importance.png`

- Gini Index Decision Tree 的前 20 个重要特征。

`14_prediction_probability_distribution.png`

- 四个模型在 validation set 上对 positive class 的预测概率或 score 分布。

`15_error_analysis_fp_fn.png`

- 四个模型 False Positive 和 False Negative 数量对比。
- 员工离职预测中尤其需要关注 False Negative。

`16_model_training_time_comparison.png`

- 四个模型训练时间和预测时间对比。

## 9. 报告写作提示

模型评价部分建议重点使用以下图：

- `03_model_metrics_comparison.png`
- `04_confusion_matrix_entropy_tree.png` 到 `07_confusion_matrix_svm.png`
- `08_roc_curves_all_models.png`
- `09_pr_curves_all_models.png`
- `15_error_analysis_fp_fn.png`

如果讨论模型解释性，可以加入：

- `10_entropy_tree_structure.png`
- `11_gini_tree_structure.png`
- `12_entropy_tree_feature_importance.png`
- `13_gini_tree_feature_importance.png`

员工离职预测不能只看 accuracy。因为离职员工通常是少数类，模型即使倾向预测“不离职”也可能得到较高 accuracy。更应该结合 recall、F1-score、PR-AUC 和 False Negative 数量，判断模型能否发现真正可能离职的员工。
