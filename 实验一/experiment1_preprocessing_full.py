############################################################
# Part 1. Read the raw csv files
############################################################

# use pandas to read the csv files
import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split

# this one is for scaling the numeric features later
from sklearn.preprocessing import StandardScaler

# use a non-interactive backend so figures can be saved by script
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# read train data and test data
train = pd.read_csv("pfm_train.csv")
test = pd.read_csv("pfm_test.csv")

# just check the size first
print("train shape:", train.shape)
print("test shape:", test.shape)

# have a look of the first few rows
train.head()


############################################################
# Part 2. Check basic information and missing values
############################################################

# check basic info of train set
print("=== train info ===")
train.info()

# also check the test set
print("\n=== test info ===")
test.info()

# see if there is any missing values in train
print("\n=== missing values in train ===")
print(train.isnull().sum())

# same thing for test
print("\n=== missing values in test ===")
print(test.isnull().sum())


############################################################
# Part 3. Check duplicate rows and constant columns
############################################################

# check duplicate rows first
print("duplicate rows in train:", train.duplicated().sum())
print("duplicate rows in test:", test.duplicated().sum())

# find the columns which only have one value
const_train = [col for col in train.columns if train[col].nunique(dropna=False) == 1]
const_test = [col for col in test.columns if test[col].nunique(dropna=False) == 1]

# print them out
print("constant cols in train:", const_train)
print("constant cols in test:", const_test)


############################################################
# Part 4. Check the label and categorical columns
############################################################

# see the target label distribution
print("attrition counts:")
print(train["Attrition"].value_counts())

# find all categorical columns in raw data
cat_cols_raw = train.select_dtypes(include="object").columns.tolist()
print("\nraw categorical cols:", cat_cols_raw)

# check each category values
for col in cat_cols_raw:
    print(f"\nvalue counts of {col}:")
    print(train[col].value_counts())


############################################################
# Part 5. Drop useless columns
############################################################

# copy the data first, so the raw one not be changed
train_clean = train.copy()
test_clean = test.copy()

# these columns are not useful, so remove them
# Over18 and StandardHours are basically same value
# EmployeeNumber is just id
drop_cols = ["Over18", "StandardHours", "EmployeeNumber"]

# drop these columns in both train and test
train_clean = train_clean.drop(columns=drop_cols)
test_clean = test_clean.drop(columns=drop_cols)

# check the shape after dropping
print("train_clean shape:", train_clean.shape)
print("test_clean shape:", test_clean.shape)


############################################################
# Part 6. Encode categorical features
############################################################

# get the categorical columns after dropping useless ones
cat_cols = train_clean.select_dtypes(include="object").columns.tolist()
print("categorical cols after drop:", cat_cols)

# do one-hot encoding for categorical features
# drop_first=True to avoid some repeated dummy columns
train_encoded = pd.get_dummies(train_clean, columns=cat_cols, drop_first=True)
test_encoded = pd.get_dummies(test_clean, columns=cat_cols, drop_first=True)

# split x and y from training data
X_train = train_encoded.drop(columns="Attrition")
y_train = train_encoded["Attrition"]

# make test columns same with train columns
# if some column is missing in test, fill it by 0
X_test = test_encoded.reindex(columns=X_train.columns, fill_value=0)

# find bool type columns
bool_cols_train = X_train.select_dtypes(include="bool").columns
bool_cols_test = X_test.select_dtypes(include="bool").columns

# change bool to int, maybe better for model later
X_train[bool_cols_train] = X_train[bool_cols_train].astype(int)
X_test[bool_cols_test] = X_test[bool_cols_test].astype(int)

# check shape after encoding
print("encoded train shape:", train_encoded.shape)
print("encoded test shape:", test_encoded.shape)
print("X_train shape:", X_train.shape)
print("X_test shape:", X_test.shape)


############################################################
# Part 7. Scale numeric features
############################################################

# pick numeric columns for scaling
# do not include the target column
num_cols = train_clean.select_dtypes(exclude="object").columns.tolist()
num_cols.remove("Attrition")

# print these numeric columns
print("scaled numeric cols:", num_cols)

# create the scaler
scaler = StandardScaler()

# fit on train data first, then transform it
X_train[num_cols] = scaler.fit_transform(X_train[num_cols])

# use the same scaler on test data
X_test[num_cols] = scaler.transform(X_test[num_cols])

# look the processed train data
X_train.head()


############################################################
# Part 8. Final check of prepared data
############################################################

# final check of the shapes
print("final X_train shape:", X_train.shape)
print("final y_train shape:", y_train.shape)
print("final X_test shape:", X_test.shape)

# see if there is still missing values
print("missing values in X_train:", X_train.isnull().sum().sum())
print("missing values in X_test:", X_test.isnull().sum().sum())

# check the final data types
print("\nX_train dtype summary:")
print(X_train.dtypes.value_counts())


############################################################
# Part 9. Prepare the final modeling matrix
############################################################

# save the preprocessing output for the later linear-model practice
# always write to the sibling experiment folder, so the files can be regenerated anytime
output_dir = Path.cwd().parent / "实验二"
output_dir.mkdir(parents=True, exist_ok=True)

X_train.to_csv(output_dir / "X_train_preprocessed.csv", index=False)
y_train.to_frame(name="Attrition").to_csv(output_dir / "y_train_preprocessed.csv", index=False)
X_test.to_csv(output_dir / "X_test_preprocessed.csv", index=False)

print("saved:", output_dir / "X_train_preprocessed.csv")
print("saved:", output_dir / "y_train_preprocessed.csv")
print("saved:", output_dir / "X_test_preprocessed.csv")


############################################################
# Part 10. Prepare validation data and figure folder
############################################################

sns.set_theme(style="whitegrid", context="talk")
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["axes.titlesize"] = 16
plt.rcParams["axes.labelsize"] = 13

X_fit, X_valid, y_fit, y_valid = train_test_split(
    X_train,
    y_train,
    test_size=0.25,
    random_state=42,
    stratify=y_train,
)

figure_dir = Path.cwd() / "experiment1_figures"
figure_dir.mkdir(exist_ok=True)

print("X_fit shape:", X_fit.shape)
print("X_valid shape:", X_valid.shape)
print("validation label distribution:")
print(y_valid.value_counts(normalize=True).round(4))


############################################################
# Part 11. Draw and save the main figures
############################################################

fig, axes = plt.subplots(2, 2, figsize=(18, 13))

sns.countplot(data=train, x="Attrition", hue="Attrition", palette="Set2", ax=axes[0, 0], legend=False)
axes[0, 0].set_title("Attrition Label Distribution")
axes[0, 0].set_xlabel("Attrition")
axes[0, 0].set_ylabel("Count")

sns.countplot(data=train, x="OverTime", hue="Attrition", palette="Set1", ax=axes[0, 1])
axes[0, 1].set_title("OverTime vs Attrition")
axes[0, 1].set_xlabel("OverTime")
axes[0, 1].set_ylabel("Count")

sns.histplot(data=train, x="Age", hue="Attrition", kde=True, bins=20, palette="Set2", ax=axes[1, 0], element="step")
axes[1, 0].set_title("Age Distribution by Attrition")
axes[1, 0].set_xlabel("Age")
axes[1, 0].set_ylabel("Frequency")

sns.boxplot(data=train, x="Attrition", y="MonthlyIncome", hue="Attrition", palette="Pastel1", ax=axes[1, 1], legend=False)
axes[1, 1].set_title("Monthly Income by Attrition")
axes[1, 1].set_xlabel("Attrition")
axes[1, 1].set_ylabel("Monthly Income")

plt.tight_layout()
fig.savefig(figure_dir / "figure_01_label_and_basic_patterns.png", dpi=200, bbox_inches="tight")
plt.close(fig)

fig, axes = plt.subplots(1, 3, figsize=(22, 7))

department_rate = (
    train.groupby("Department")["Attrition"]
    .mean()
    .sort_values(ascending=False)
    .mul(100)
    .round(2)
)
sns.barplot(
    x=department_rate.values,
    y=department_rate.index,
    palette="viridis",
    ax=axes[0],
)
axes[0].set_title("Attrition Rate by Department")
axes[0].set_xlabel("Attrition Rate (%)")
axes[0].set_ylabel("Department")

jobrole_rate = (
    train.groupby("JobRole")["Attrition"]
    .mean()
    .sort_values(ascending=False)
    .mul(100)
    .round(2)
)
sns.barplot(
    x=jobrole_rate.values,
    y=jobrole_rate.index,
    palette="magma",
    ax=axes[1],
)
axes[1].set_title("Attrition Rate by Job Role")
axes[1].set_xlabel("Attrition Rate (%)")
axes[1].set_ylabel("Job Role")

education_rate = (
    train.groupby("EducationField")["Attrition"]
    .mean()
    .sort_values(ascending=False)
    .mul(100)
    .round(2)
)
sns.barplot(
    x=education_rate.values,
    y=education_rate.index,
    palette="crest",
    ax=axes[2],
)
axes[2].set_title("Attrition Rate by Education Field")
axes[2].set_xlabel("Attrition Rate (%)")
axes[2].set_ylabel("Education Field")

plt.tight_layout()
fig.savefig(figure_dir / "figure_02_attrition_rate_by_category.png", dpi=200, bbox_inches="tight")
plt.close(fig)

corr_source = train.select_dtypes(exclude="object").copy()
corr_target = corr_source.corr(numeric_only=True)["Attrition"].drop("Attrition")
top_corr_features = corr_target.abs().sort_values(ascending=False).head(10).index.tolist()
heatmap_columns = top_corr_features + ["Attrition"]

fig, ax = plt.subplots(figsize=(12, 9))
sns.heatmap(
    corr_source[heatmap_columns].corr(),
    annot=True,
    fmt=".2f",
    cmap="RdBu_r",
    center=0,
    square=True,
    ax=ax,
)
ax.set_title("Correlation Heatmap of the Most Relevant Numeric Features")
plt.tight_layout()
fig.savefig(figure_dir / "figure_03_correlation_heatmap.png", dpi=200, bbox_inches="tight")
plt.close(fig)

print("top numeric correlations with Attrition:")
print(corr_target.sort_values(key=lambda s: s.abs(), ascending=False).head(10))


############################################################
# Part 12. Train multiple models and save the metrics
############################################################

models = {
    "Logistic Regression (L2)": LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42,
    ),
    "Logistic Regression (L1)": LogisticRegression(
        max_iter=3000,
        class_weight="balanced",
        penalty="l1",
        solver="liblinear",
        random_state=42,
    ),
    "SGD Log-Loss": SGDClassifier(
        loss="log_loss",
        class_weight="balanced",
        max_iter=3000,
        tol=1e-4,
        random_state=42,
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=400,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
    ),
}

model_results = []
fitted_models = {}

for name, model in models.items():
    model.fit(X_fit, y_fit)
    fitted_models[name] = model

    y_pred = model.predict(X_valid)
    if hasattr(model, "predict_proba"):
        y_score = model.predict_proba(X_valid)[:, 1]
    else:
        raw_score = model.decision_function(X_valid)
        y_score = 1 / (1 + np.exp(-raw_score))

    model_results.append(
        {
            "Model": name,
            "Accuracy": accuracy_score(y_valid, y_pred),
            "Precision": precision_score(y_valid, y_pred),
            "Recall": recall_score(y_valid, y_pred),
            "F1": f1_score(y_valid, y_pred),
            "ROC_AUC": roc_auc_score(y_valid, y_score),
        }
    )

metrics_df = pd.DataFrame(model_results).sort_values(
    by=["ROC_AUC", "F1"],
    ascending=False,
).reset_index(drop=True)
metrics_df.to_csv(Path.cwd() / "model_metrics.csv", index=False)

print("\nmodel metrics:")
print(metrics_df.round(4))


############################################################
# Part 13. Draw ROC curves and confusion matrices
############################################################

fig, ax = plt.subplots(figsize=(11, 8))

for name, model in fitted_models.items():
    if hasattr(model, "predict_proba"):
        y_score = model.predict_proba(X_valid)[:, 1]
    else:
        raw_score = model.decision_function(X_valid)
        y_score = 1 / (1 + np.exp(-raw_score))

    fpr, tpr, _ = roc_curve(y_valid, y_score)
    auc_value = roc_auc_score(y_valid, y_score)
    ax.plot(fpr, tpr, linewidth=2.5, label=f"{name} (AUC={auc_value:.3f})")

ax.plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=1.5, label="Random Guess")
ax.set_title("ROC Curves of Different Models")
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.legend(loc="lower right")
plt.tight_layout()
fig.savefig(figure_dir / "figure_04_roc_curves.png", dpi=200, bbox_inches="tight")
plt.close(fig)

best_log_model = fitted_models["Logistic Regression (L2)"]
rf_model = fitted_models["Random Forest"]

cm_log = confusion_matrix(y_valid, best_log_model.predict(X_valid))
cm_rf = confusion_matrix(y_valid, rf_model.predict(X_valid))

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

sns.heatmap(cm_log, annot=True, fmt="d", cmap="Blues", cbar=False, ax=axes[0])
axes[0].set_title("Confusion Matrix: Logistic Regression (L2)")
axes[0].set_xlabel("Predicted Label")
axes[0].set_ylabel("True Label")

sns.heatmap(cm_rf, annot=True, fmt="d", cmap="Greens", cbar=False, ax=axes[1])
axes[1].set_title("Confusion Matrix: Random Forest")
axes[1].set_xlabel("Predicted Label")
axes[1].set_ylabel("True Label")

plt.tight_layout()
fig.savefig(figure_dir / "figure_05_confusion_matrices.png", dpi=200, bbox_inches="tight")
plt.close(fig)


############################################################
# Part 14. Save coefficient and feature importance outputs
############################################################

log_coef = pd.Series(best_log_model.coef_[0], index=X_train.columns).sort_values()
top_negative = log_coef.head(8).sort_values(ascending=True)
top_positive = log_coef.tail(8).sort_values(ascending=False)

rf_importance = (
    pd.Series(rf_model.feature_importances_, index=X_train.columns)
    .sort_values(ascending=False)
    .head(12)
)

top_positive.to_csv(Path.cwd() / "logistic_top_positive_coefficients.csv", header=["coefficient"])
top_negative.to_csv(Path.cwd() / "logistic_top_negative_coefficients.csv", header=["coefficient"])
rf_importance.to_csv(Path.cwd() / "random_forest_feature_importances.csv", header=["importance"])

fig, axes = plt.subplots(1, 2, figsize=(18, 8))

coef_plot = pd.concat([top_positive, top_negative]).sort_values()
sns.barplot(
    x=coef_plot.values,
    y=coef_plot.index,
    palette=["#4c78a8" if value < 0 else "#e45756" for value in coef_plot.values],
    ax=axes[0],
)
axes[0].set_title("Most Influential Logistic Regression Coefficients")
axes[0].set_xlabel("Coefficient Value")
axes[0].set_ylabel("Feature")

sns.barplot(
    x=rf_importance.values,
    y=rf_importance.index,
    palette="rocket",
    ax=axes[1],
)
axes[1].set_title("Top Random Forest Feature Importances")
axes[1].set_xlabel("Importance")
axes[1].set_ylabel("Feature")

plt.tight_layout()
fig.savefig(figure_dir / "figure_06_model_interpretation.png", dpi=200, bbox_inches="tight")
plt.close(fig)

print("\ntop positive logistic coefficients:")
print(top_positive)
print("\ntop negative logistic coefficients:")
print(top_negative)
