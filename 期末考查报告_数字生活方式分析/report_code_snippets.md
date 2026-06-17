# Report Code Snippets

Copy these short snippets into the matching code placeholders in the Word report.
Each snippet is intentionally short enough for the main text. The complete runnable
code is kept in `appendix_A_complete_code.py`.

## Code1 Data Loading and Basic Inspection

```python
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path.cwd() / "期末考查报告_数字生活方式分析"
raw_path = PROJECT_ROOT / "data" / "raw" / "digital_lifestyle_benchmark_2025.csv"

df = pd.read_csv(raw_path)

print("Shape:", df.shape)
print("Columns:", df.columns.tolist())
print("Data types:")
print(df.dtypes)
print(df.head())
```

## Code2 Missing, Duplicate, and Range Check

```python
key_numeric = [
    "age", "device_hours_per_day", "phone_unlocks",
    "notifications_per_day", "social_media_mins", "study_mins",
    "sleep_hours", "sleep_quality", "productivity_score",
    "digital_dependence_score",
]

missing_summary = df.isna().sum().reset_index()
missing_summary.columns = ["field_name", "missing_count"]

duplicate_rows = df.duplicated().sum()
duplicate_id = df["id"].duplicated().sum()
range_summary = df[key_numeric].agg(["min", "max", "mean"]).T

print(missing_summary)
print("Duplicate rows:", duplicate_rows)
print("Duplicate id:", duplicate_id)
print(range_summary)
```

## Code3 Feature Engineering

```python
engineered = df.copy()
eps = 1e-6

engineered["social_media_hours"] = engineered["social_media_mins"] / 60.0
engineered["study_hours"] = engineered["study_mins"] / 60.0
engineered["notifications_per_device_hour"] = (
    engineered["notifications_per_day"] / engineered["device_hours_per_day"].clip(lower=eps)
)
engineered["unlocks_per_device_hour"] = (
    engineered["phone_unlocks"] / engineered["device_hours_per_day"].clip(lower=eps)
)
engineered["device_to_sleep_ratio"] = (
    engineered["device_hours_per_day"] / engineered["sleep_hours"].clip(lower=eps)
)
engineered["activity_sleep_interaction"] = (
    engineered["physical_activity_days"] * engineered["sleep_hours"]
)
engineered["social_to_study_ratio"] = engineered["social_media_mins"] / (
    engineered["study_mins"] + 1.0
)
```

## Code4 Leakage Control and Task-Specific Feature Selection

```python
outcome_cols = [
    "anxiety_score", "depression_score", "stress_level",
    "happiness_score", "focus_score", "high_risk_flag",
    "productivity_score", "digital_dependence_score",
]
classification_drop = [
    "id", "high_risk_flag", "anxiety_score", "depression_score",
    "stress_level", "happiness_score", "focus_score",
    "productivity_score", "digital_dependence_score",
]

def regression_drop_for(target):
    drop_cols = {"id", target}
    drop_cols.update(outcome_cols)
    if target == "digital_dependence_score":
        drop_cols.add("productivity_score")
    if target == "productivity_score":
        drop_cols.add("digital_dependence_score")
    return sorted(drop_cols)

clustering_features = [
    "device_hours_per_day", "phone_unlocks", "notifications_per_day",
    "social_media_mins", "study_mins", "physical_activity_days",
    "sleep_hours", "sleep_quality", "social_media_hours", "study_hours",
    "notifications_per_device_hour", "unlocks_per_device_hour",
    "device_to_sleep_ratio", "activity_sleep_interaction", "social_to_study_ratio",
]

digital_dependence_drop = regression_drop_for("digital_dependence_score")
productivity_drop = regression_drop_for("productivity_score")
```

## Code5 Classification Model Comparison and Threshold Tuning

```python
from sklearn.model_selection import StratifiedKFold, GridSearchCV, train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import precision_recall_fscore_support
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

X = engineered.drop(columns=classification_drop)
y = engineered["high_risk_flag"]
num_cols = X.select_dtypes(include="number").columns.tolist()
cat_cols = X.select_dtypes(exclude="number").columns.tolist()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42
)

preprocess = ColumnTransformer([
    ("num", StandardScaler(), num_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
])
pipe = Pipeline([
    ("preprocess", preprocess),
    ("model", GradientBoostingClassifier(random_state=42)),
])
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
grid = GridSearchCV(
    pipe,
    {"model__learning_rate": [0.03, 0.05, 0.1], "model__max_depth": [2, 3]},
    scoring="average_precision",
    cv=cv,
)
grid.fit(X_train, y_train)
proba = grid.predict_proba(X_test)[:, 1]
pred = (proba >= 0.14).astype(int)
print(precision_recall_fscore_support(y_test, pred, average="binary"))
```

## Code6 Regression Model Evaluation

```python
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def regression_metrics(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    return {
        "r2": r2_score(y_true, y_pred),
        "mse": mse,
        "rmse": np.sqrt(mse),
        "mae": mean_absolute_error(y_true, y_pred),
    }

dd_pred = pd.read_csv(PROJECT_ROOT / "results" / "regression_digital_dependence_predictions.csv")
prod_pred = pd.read_csv(PROJECT_ROOT / "results" / "regression_productivity_predictions.csv")

print(regression_metrics(dd_pred["actual"], dd_pred["predicted"]))
print(regression_metrics(prod_pred["actual"], prod_pred["predicted"]))
```

## Code7 Clustering Model Comparison and k Selection

```python
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

X_cluster = engineered[clustering_features]
X_scaled = StandardScaler().fit_transform(X_cluster)

scores = []
for k in range(2, 9):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km_labels = km.fit_predict(X_scaled)
    agg = AgglomerativeClustering(n_clusters=k)
    agg_labels = agg.fit_predict(X_scaled)
    gmm = GaussianMixture(n_components=k, random_state=42)
    gmm_labels = gmm.fit_predict(X_scaled)
    scores.extend([
        {"algorithm": "KMeans", "k": k, "silhouette": silhouette_score(X_scaled, km_labels)},
        {"algorithm": "Agglomerative", "k": k, "silhouette": silhouette_score(X_scaled, agg_labels)},
        {"algorithm": "GaussianMixture", "k": k, "silhouette": silhouette_score(X_scaled, gmm_labels)},
    ])

print(pd.DataFrame(scores))
```
