############################################################
# Part 1. Read the raw csv files
############################################################

# use pandas to read the csv files
import pandas as pd

# this one is for scaling the numeric features later
from sklearn.preprocessing import StandardScaler

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
# Part 9. Export preprocessing output for Experiment 2
############################################################

from pathlib import Path

# save the preprocessing output for the next experiment
base_dir = Path.cwd().parent
exp2_dir = next(
    p for p in base_dir.iterdir()
    if p.is_dir()
    and p != Path.cwd()
    and (p / "pfm_train.csv").exists()
    and (p / "pfm_test.csv").exists()
    and any(child.suffix.lower() == ".pptx" for child in p.iterdir())
)
exp2_dir.mkdir(parents=True, exist_ok=True)

X_train.to_csv(exp2_dir / "X_train_preprocessed.csv", index=False)
y_train.to_frame(name="Attrition").to_csv(exp2_dir / "y_train_preprocessed.csv", index=False)
X_test.to_csv(exp2_dir / "X_test_preprocessed.csv", index=False)

print("saved:", exp2_dir / "X_train_preprocessed.csv")
print("saved:", exp2_dir / "y_train_preprocessed.csv")
print("saved:", exp2_dir / "X_test_preprocessed.csv")
