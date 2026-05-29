# Experiment 4: Wine Clustering Model Practice

本目录是《大数据分析与应用》实验四，主题是基于 Wine 数据集建立聚类模型，对葡萄酒样本进行无监督聚类分析，并使用聚类内部指标评价模型效果。

**This is a clustering experiment, not a classification experiment.**

## 1. 实验任务简介

根据老师 PPT 要求，本实验使用给定的 wine classification dataset，但实验目标不是分类，而是聚类：

1. 读取 `wine.data`。
2. 单独保存第一列原始类别标签为 `y_true_optional`。
3. 删除第一列 `class`，只使用后面的 13 个化学特征作为聚类输入。
4. 使用传统 sklearn 聚类算法建立模型：
   - KMeans
   - AgglomerativeClustering
   - DBSCAN
5. 使用聚类内部指标进行主评价，并生成实验报告所需的表格和图片。

## 2. 数据集说明

`wine.data` 无表头，代码中设置 14 个列名：

```text
class,
Alcohol,
Malic acid,
Ash,
Alcalinity of ash,
Magnesium,
Total phenols,
Flavanoids,
Nonflavanoid phenols,
Proanthocyanins,
Color intensity,
Hue,
OD280/OD315 of diluted wines,
Proline
```

其中第一列 `class` 是原始类别标签，不属于聚类输入特征。实际聚类使用的特征矩阵为：

```python
y_true_optional = df["class"]
X = df.drop(columns=["class"])
```

**The class labels in wine.data are removed before clustering.**

## 3. 为什么要删除 class 标签

聚类是无监督学习，模型训练时不能知道样本的真实类别。如果把 `class` 放进 `X`，聚类算法就会直接利用真实标签信息，实验会变成“带标签信息的伪聚类”，不符合本实验要求。

本实验严格保证：

1. `wine.data` 第一列只保存为 `y_true_optional`。
2. `X` 只包含 13 个化学特征。
3. **The labels are not used for model training, parameter selection, or main evaluation.**
4. 原始标签只在最后的 optional external comparison 中使用。

## 4. 为什么不能使用分类指标作为聚类主指标

分类指标需要真实标签参与评价，而聚类主实验不能依赖真实类别标签。因此：

**Main evaluation metrics are Silhouette, Calinski-Harabasz, and Davies-Bouldin.**

主评价指标为：

1. **Silhouette Coefficient**：越高越好。
2. **Calinski-Harabasz Index**：越高越好。
3. **Davies-Bouldin Index**：越低越好。

KMeans 额外记录 `inertia`，但 `inertia` 只用于 KMeans 内部选择 k 值，不作为跨模型唯一结论。

**Accuracy, precision, recall, F1-score, ROC-AUC, PR-AUC, confusion matrix, and classification report are not used as main clustering metrics.**

ARI、NMI、homogeneity、completeness、v-measure 和 class crosstab 只作为可选外部对照：

**ARI/NMI/crosstab are optional external comparison only.**

必须强调：

**The original class labels were not used in clustering training, parameter selection, or main evaluation. They were only used after clustering as an optional external comparison.**

## 5. CPU 和依赖说明

**The experiment uses sklearn traditional clustering algorithms and CPU only.**

**No GPU is needed.**

不使用 cuML、RAPIDS、PyTorch、TensorFlow，也不需要 GPU。

安装依赖：

```bash
pip install numpy pandas matplotlib scikit-learn scipy
```

`scipy` 只用于绘制 AgglomerativeClustering 的 dendrogram。本实验没有使用 seaborn，所有图片均用 matplotlib 保存。

## 6. 实验方法

### 6.1 数据读取与检查

脚本会读取：

```text
实验四/data/wine.data
```

如果仓库根目录、`实验四/` 或 `实验四/data/` 中存在 `wine.zip`，代码会自动解压其中的 `wine.data`、`wine.names` 和 `Index` 到 `实验四/data/`。

如果找不到 `wine.data`，脚本会抛出清晰的 `FileNotFoundError`，提示将文件放到：

```text
实验四/data/wine.data
```

脚本会保存：

- 数据形状
- 缺失值
- 重复行
- 数据类型
- 特征描述性统计
- 标准化前后统计信息
- 原始类别分布，但仅作为 optional information

### 6.2 标准化与 PCA

聚类输入为删除 `class` 后的 13 个特征。由于不同化学特征量纲差异较大，实验使用：

```python
StandardScaler()
```

得到 `X_scaled`。

然后使用：

```python
PCA(n_components=2, random_state=42)
```

得到二维 PCA 结果，仅用于可视化，不作为主评价。

### 6.3 KMeans

KMeans 对 `k=2` 到 `k=10` 循环实验，记录：

- n_clusters
- inertia
- silhouette_score
- calinski_harabasz_score
- davies_bouldin_score
- training_time_seconds
- cluster_size_summary

最终重点保留：

```python
KMeans(n_clusters=3, n_init=50, random_state=42)
```

同时保存 best KMeans by silhouette，用于模型总表比较。

### 6.4 AgglomerativeClustering

层次聚类测试四种 linkage：

- ward
- complete
- average
- single

每种 linkage 测试 `k=2` 到 `k=10`。最终重点保留：

```python
AgglomerativeClustering(linkage="ward", n_clusters=3)
```

同时保存 best Agglomerative by silhouette。

### 6.5 DBSCAN

DBSCAN 使用标准化后的 `X_scaled`，并绘制 k-distance curve 辅助解释 eps 选择。

网格搜索范围：

- `eps`: 0.3 到 5.0
- `min_samples`: 3, 4, 5, 6, 8, 10

如果有效簇数量少于 2，则 Silhouette、Calinski-Harabasz、Davies-Bouldin 记录为 `NaN`。DBSCAN 对 `eps` 和 `min_samples` 非常敏感，因此最终选择时同时考虑内部指标和 noise ratio，不能为了较高指标让大多数样本变成 noise。

## 7. 运行 Python 脚本

在仓库根目录运行：

```bash
python 实验四/experiment4_wine_clustering.py
```

或进入实验四目录运行：

```bash
cd 实验四
python experiment4_wine_clustering.py
```

脚本会自动创建：

```text
实验四/results/
实验四/figures/
```

运行结束后会打印：

- generated results files
- generated figures files
- recommended model
- short analysis text

## 8. 运行 Notebook

打开：

```text
实验四/experiment4_wine_clustering.ipynb
```

然后从上到下运行所有单元格即可。

Notebook 分成以下部分：

- Read data
- Remove label
- Data checking
- Standardization
- PCA visualization
- KMeans experiment
- Agglomerative clustering experiment
- DBSCAN experiment
- Model comparison
- Cluster profile analysis
- Optional label comparison
- Final conclusion

Notebook 会 import `experiment4_wine_clustering.py` 中的函数，避免两套逻辑互相矛盾。Notebook 运行后也会生成同样的 `results/` 和 `figures/` 文件。

## 9. results 文件说明

`data_basic_info.csv`

- 数据集路径、样本数、原始列数、聚类特征数、删除的标签列、特征列名、数据类型。
- 原始 class 分布只作为 optional information。

`feature_descriptive_statistics.csv`

- 13 个化学特征的描述性统计。
- 同时包含 before_scaling 和 after_scaling 两个版本。

`missing_duplicate_check.csv`

- 原始数据和聚类特征矩阵中的缺失值、重复行检查。

`kmeans_k_selection_results.csv`

- KMeans 在 `k=2` 到 `k=10` 下的 inertia 和三个聚类内部指标。

`agglomerative_grid_results.csv`

- AgglomerativeClustering 在不同 linkage 和 k 下的聚类内部指标。

`dbscan_grid_search_results.csv`

- DBSCAN 在不同 eps 和 min_samples 下的有效簇数量、noise 数量、noise ratio 和聚类内部指标。

`final_model_comparison.csv`

- 汇总比较：
  - KMeans k=3
  - Best KMeans by silhouette
  - Agglomerative ward k=3
  - Best Agglomerative by silhouette
  - Best DBSCAN valid setting

`model_ranking_summary.csv`

- 根据 Silhouette、Calinski-Harabasz、Davies-Bouldin 和 DBSCAN noise ratio 生成的模型排序。

`cluster_profile_summary.csv`

- KMeans k=3 每个 cluster 的样本数量和原始特征均值。

`cluster_profile_scaled_mean.csv`

- KMeans k=3 每个 cluster 的标准化特征均值。

`cluster_profile_interpretation.txt`

- 自动生成的 cluster profile 解释文字。

`final_cluster_assignments.csv`

- 每个样本的聚类结果。
- 包含 `sample_id`、`kmeans_k3_cluster`、`best_kmeans_cluster`、`agglomerative_ward_k3_cluster`、`best_agglomerative_cluster`、`best_dbscan_cluster`。
- 不包含原始 `class` 标签。

`optional_external_label_comparison.csv`

- ARI、NMI、homogeneity、completeness、v-measure。
- optional external comparison only。

`optional_kmeans_class_crosstab.csv`

- KMeans k=3 cluster 与原始 class 的交叉表，仅 optional。

`optional_agglomerative_class_crosstab.csv`

- Agglomerative ward k=3 cluster 与原始 class 的交叉表，仅 optional。

`optional_dbscan_class_crosstab.csv`

- Best DBSCAN cluster 与原始 class 的交叉表，仅 optional。

## 10. figures 图片说明

`01_feature_boxplots_before_scaling.png`

- 标准化前 13 个化学特征的箱线图。

`02_feature_boxplots_after_scaling.png`

- 标准化后 13 个化学特征的箱线图。

`03_feature_correlation_heatmap.png`

- 特征相关性热力图。

`04_pca_original_labels_optional.png`

- PCA 二维图，颜色为原始 class，仅用于 optional reference。

`05_kmeans_elbow_curve.png`

- KMeans inertia elbow curve，用于 k 值观察。

`06_kmeans_silhouette_by_k.png`

- KMeans 不同 k 的 Silhouette 对比。

`07_kmeans_ch_by_k.png`

- KMeans 不同 k 的 Calinski-Harabasz 对比。

`08_kmeans_db_by_k.png`

- KMeans 不同 k 的 Davies-Bouldin 对比。

`09_pca_kmeans_k3_clusters.png`

- KMeans k=3 的 PCA 聚类可视化。

`10_pca_best_kmeans_clusters.png`

- Best KMeans by silhouette 的 PCA 聚类可视化。

`11_agglomerative_silhouette_comparison.png`

- 不同 linkage 和 k 下的 Agglomerative Silhouette 对比。

`12_agglomerative_ch_comparison.png`

- 不同 linkage 和 k 下的 Calinski-Harabasz 对比。

`13_agglomerative_db_comparison.png`

- 不同 linkage 和 k 下的 Davies-Bouldin 对比。

`14_agglomerative_dendrogram.png`

- Ward linkage 的 dendrogram。

`15_pca_agglomerative_ward_k3_clusters.png`

- Agglomerative ward k=3 的 PCA 聚类可视化。

`16_dbscan_k_distance_curve.png`

- DBSCAN k-distance curve，用于解释 eps 选择。

`17_dbscan_silhouette_heatmap.png`

- DBSCAN Silhouette heatmap。

`18_dbscan_noise_ratio_heatmap.png`

- DBSCAN noise ratio heatmap。

`19_dbscan_cluster_count_heatmap.png`

- DBSCAN 有效簇数量 heatmap。

`20_pca_best_dbscan_clusters.png`

- Best DBSCAN setting 的 PCA 聚类可视化。

`21_final_model_metrics_comparison.png`

- 最终模型内部指标对比图。

`22_cluster_size_comparison.png`

- 最终模型 cluster size 对比图。

`23_cluster_profile_heatmap.png`

- KMeans k=3 的 cluster profile heatmap。

`24_optional_external_metric_comparison.png`

- optional external metrics 对比图，不作为主评价。

## 11. 报告写作提示

建议报告重点使用以下图片：

1. `03_feature_correlation_heatmap.png`
2. `05_kmeans_elbow_curve.png`
3. `06_kmeans_silhouette_by_k.png`
4. `09_pca_kmeans_k3_clusters.png`
5. `11_agglomerative_silhouette_comparison.png`
6. `16_dbscan_k_distance_curve.png`
7. `21_final_model_metrics_comparison.png`
8. `23_cluster_profile_heatmap.png`

报告中可以把 `04_pca_original_labels_optional.png` 和 `24_optional_external_metric_comparison.png` 放在“可选外部对照”部分，不能把它们写成主评价依据。

## 12. 主要实验结论草稿

可以按以下思路写结论，具体数值以你运行脚本后生成的 CSV 为准：

1. Wine 数据集中不同化学指标的量纲差异明显，因此聚类前需要 StandardScaler 标准化。
2. KMeans 在不同 k 下的 Silhouette、Calinski-Harabasz、Davies-Bouldin 可以帮助选择合适的 k；`k=3` 是本实验重点保留设置，也方便与数据集原始结构做 optional 对照。
3. AgglomerativeClustering 中不同 linkage 的表现不同，Ward linkage 通常更适合欧氏距离下的紧凑簇结构。
4. DBSCAN 对 eps 和 min_samples 敏感，部分参数可能产生过多 noise，因此不能只看单个指标。
5. 最终模型推荐应以 `final_model_comparison.csv` 和 `model_ranking_summary.csv` 为准，优先看 Silhouette，再参考 Calinski-Harabasz 和 Davies-Bouldin，同时检查 DBSCAN noise ratio。
6. 原始 class 标签没有参与训练、调参或主评价，只在 optional external comparison 中用于观察聚类结果和原始类别之间的对应关系。

## 13. 实验心得可写的关键点

1. 聚类实验和分类实验的评价逻辑不同，不能直接套用 accuracy、precision、recall、F1-score 等分类指标。
2. 对于无监督学习，数据预处理和特征尺度会显著影响聚类结果。
3. KMeans 简单、稳定、可解释性较强，但需要预先指定 k。
4. 层次聚类可以通过 dendrogram 辅助理解样本合并过程。
5. DBSCAN 能识别 noise，但参数敏感，需要结合 k-distance curve 和 noise ratio 分析。
6. optional external comparison 可以帮助理解聚类结果，但不能改变“标签不参与主实验”的原则。
