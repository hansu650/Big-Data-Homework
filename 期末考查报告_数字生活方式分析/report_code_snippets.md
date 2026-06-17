# Report Code Snippets

Copy the following short code snippets into the corresponding placeholders in the Word report.

## Code1 Data Loading and Basic Inspection

```python
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path("期末考查报告_数字生活方式分析")
raw_path = PROJECT_ROOT / "data" / "raw" / "digital_lifestyle_benchmark_2025.csv"

df = pd.read_csv(raw_path)

print("Shape:", df.shape)
print("Columns:", df.columns.tolist())
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

engineered["social_media_hours"] = engineered["social_media_mins"] / 60
engineered["study_hours"] = engineered["study_mins"] / 60
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
engineered["social_to_study_ratio"] = engineered["social_media_mins"] / (engineered["study_mins"] + 1)
```

## Code4 Leakage Control and Feature Selection

```python
classification_drop = [
    "id", "high_risk_flag", "anxiety_score", "depression_score",
    "stress_level", "happiness_score", "focus_score",
    "productivity_score", "digital_dependence_score",
]

regression_drop = [
    "id", "digital_dependence_score", "high_risk_flag",
    "anxiety_score", "depression_score", "stress_level",
    "happiness_score", "focus_score", "productivity_score",
]

clustering_features = [
    "device_hours_per_day", "phone_unlocks", "notifications_per_day",
    "social_media_mins", "study_mins", "physical_activity_days",
    "sleep_hours", "sleep_quality", "social_media_hours", "study_hours",
    "notifications_per_device_hour", "unlocks_per_device_hour",
    "device_to_sleep_ratio", "activity_sleep_interaction", "social_to_study_ratio",
]
```

## Code5 Classification Training and Threshold Tuning

```python
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import precision_score, recall_score, f1_score

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
param_grid = {
    "model__learning_rate": [0.03, 0.05, 0.1],
    "model__max_depth": [2, 3],
    "model__n_estimators": [100, 200],
}

search = GridSearchCV(pipeline, param_grid, scoring="average_precision", cv=cv, n_jobs=-1)
search.fit(X_train, y_train)

valid_proba = search.predict_proba(X_valid)[:, 1]
threshold = 0.14
y_pred = (valid_proba >= threshold).astype(int)

print(precision_score(y_valid, y_pred), recall_score(y_valid, y_pred), f1_score(y_valid, y_pred))
```

## Code6 Regression Evaluation

```python
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

y_pred = best_regression_model.predict(X_test)

regression_metrics = {
    "R2": r2_score(y_test, y_pred),
    "MSE": mean_squared_error(y_test, y_pred),
    "RMSE": mean_squared_error(y_test, y_pred, squared=False),
    "MAE": mean_absolute_error(y_test, y_pred),
}

pd.DataFrame([regression_metrics]).to_csv(
    "results/regression_metrics_example.csv", index=False
)
print(regression_metrics)
```

## Code7 Clustering and K Selection

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

cluster_X = engineered[clustering_features]
cluster_X_scaled = StandardScaler().fit_transform(cluster_X)

scores = []
for k in range(2, 9):
    model = KMeans(n_clusters=k, random_state=42, n_init=20)
    labels = model.fit_predict(cluster_X_scaled)
    scores.append({
        "k": k,
        "inertia": model.inertia_,
        "silhouette": silhouette_score(cluster_X_scaled, labels),
    })

k_scores = pd.DataFrame(scores)
print(k_scores)
```

## Code8 Export Figures and Screenshot Tables

```python
from pathlib import Path

fig_dir = PROJECT_ROOT / "figures" / "final_report"
table_dir = PROJECT_ROOT / "screenshot_tables"
fig_dir.mkdir(parents=True, exist_ok=True)
table_dir.mkdir(parents=True, exist_ok=True)

fig.savefig(fig_dir / "fig1_high_risk_no_risk_distribution.png", dpi=300)

with pd.ExcelWriter(table_dir / "table1_raw_dataset_preview.xlsx") as writer:
    df.head(20).to_excel(writer, sheet_name="raw_preview", index=False)
```

