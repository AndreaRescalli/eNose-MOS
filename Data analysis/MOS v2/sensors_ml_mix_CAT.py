"""
This script performs LDA and RF on the data collected with the mixture
of compounds.   
"""

import itertools

import matplotlib.pyplot as plt
import scipy.stats
import pandas as pd
import numpy as np
import seaborn as sns
import sklearn.decomposition
import sklearn.preprocessing
from pathlib import Path
import sklearn.discriminant_analysis
import pickle as pk
import os
from matplotlib import cm
from matplotlib.colors import ListedColormap
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier
#from sklearn.svm import SVC
from catboost import CatBoostClassifier, Pool
#from lightgbm import LGBMClassifier
#from xgboost import XGBClassifier


#_SENSOR_LABELS = ["S-1", "S-2", "S-3", "S-4", "S-5", "S-6"]
_SENSOR_LABELS = ["S-2", "S-3", "S-4", "S-5"]
_FEATURE_LIST = [
    "DeltaH",
    "DeltaT1",
    "DeltaT2",
    "DeltaT3",
    "SlopeH",
    "SlopeL",
    "AreaS",
    "AreaT",
    #"DeltaR"
]
_TEMPERATURE_MODULATION = ["Sq+Tr"]

CURRENT_DIR = Path(__file__).parent.resolve()
FEATURES_FOLDER = CURRENT_DIR / "Outputs" / "Features MIX" / "TEST_R_NORM_ZSCORE"

# Load data and change concentration
features = pd.read_csv(FEATURES_FOLDER / "compound_mixtures_features.csv", index_col=0)

features.loc[features.Isopropanol < 100, "Isopropanol"] = 50
features.loc[(features.Isopropanol > 100) & (features.Isopropanol < 220), "Isopropanol"] = 150
features.loc[features.Isopropanol > 230, "Isopropanol"] = 300

features.loc[features.Acetone < 100, "Acetone"] = 50
features.loc[(features.Acetone > 100) & (features.Acetone < 180), "Acetone"] = 150
features.loc[features.Acetone > 200, "Acetone"] = 300

features.loc[features.Toluene < 120, "Toluene"] = 50
features.loc[(features.Toluene > 120) & (features.Toluene < 340) & (features.Toluene != 300), "Toluene"] = 150
features.loc[(features.Toluene > 350), "Toluene"] = 300

features = features[features["Repetition"] > 0].reset_index(drop=True)
features = features[features["Repetition"] < 6].reset_index(drop=True)

# Generate new column names
all_columns = list(itertools.product(_SENSOR_LABELS, _FEATURE_LIST))
all_columns = [f"{x[0]}-{x[1]}" for x in all_columns]
all_columns.append("Mixture")
all_columns.append("Isopropanol")
all_columns.append("Acetone")
all_columns.append("Toluene")

def apply_cat_conc(x):
    if x < 100:
        return "L"
    elif x >= 100 and x <= 200:
        return "M"
    else:
        return "H"
    
features["Isopropanol"] = features[
    "Isopropanol"
].apply(apply_cat_conc)
features["Acetone"] = features[
    "Acetone"
].apply(apply_cat_conc)
features["Toluene"] = features[
    "Toluene"
].apply(apply_cat_conc)

features["Mixture"] = (
    features["Isopropanol"]
    + "-"
    + features["Acetone"]
    + "-"
    + features["Toluene"]
)

# Set up new dataframe
features_remapped = pd.DataFrame()
features_remapped["Mixture"] = features.loc[
    (features.Sensor == "S-1"),
    "Mixture",
]
features_remapped["Repetition"] = features.loc[
    (features.Sensor == "S-1"),
    "Repetition",
]
features_remapped["Isopropanol"] = features.loc[
    (features.Sensor == "S-1"),
    "Isopropanol",
]
features_remapped["Acetone"] = features.loc[
    (features.Sensor == "S-1"),
    "Acetone",
]
features_remapped["Toluene"] = features.loc[
    (features.Sensor == "S-1"),
    "Toluene",
]
features_remapped = features_remapped.reset_index(drop=True)

for sensor in _SENSOR_LABELS:
    for feature in _FEATURE_LIST:
        for temp_mod in _TEMPERATURE_MODULATION:
            temp_df = features.loc[
                (features.Sensor == sensor)
                & (features["Temperature Modulation"] == temp_mod),
                [feature, "Mixture", "Repetition"],
            ]
            temp_df[f"{sensor}-{feature}-{temp_mod}"] = temp_df[feature]
            temp_df = temp_df.drop(feature, axis=1)
            features_remapped = pd.merge(
                features_remapped,
                temp_df,
                on=["Mixture", "Repetition"],
                how="outer",
            )
            if len(features_remapped) == 0:
                print(f"{sensor}-{feature}-{temp_mod}")
                raise

features_remapped_dropna = features_remapped.dropna(axis=0).copy()
features_var_dropna_norm = features_remapped_dropna.drop(
    ["Mixture", "Repetition", "Acetone", "Toluene", "Isopropanol"], axis=1
)
features_var_dropna_norm = scipy.stats.zscore(features_var_dropna_norm)


######################
#         ML         #
######################
X = features_var_dropna_norm
corr_matrix = pd.DataFrame(X, columns=features_var_dropna_norm.columns).corr()
sns.heatmap(corr_matrix, annot=False, cmap="coolwarm")
plt.show()
y = np.array(features_remapped_dropna[["Mixture"]])
y = y.ravel()
#label_encoder = LabelEncoder()
#y = label_encoder.fit_transform(y)  # Encode the target variable (y)

skf = StratifiedKFold(n_splits=3) # we have a small dataset and few obs per type.. keep n_splits low or you get only 1 obs in the test
for train_index, test_index in skf.split(X, y):
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y[train_index], y[test_index]
    train_size = len(train_index)
    test_size = len(test_index)
    total_size = train_size + test_size
    
    train_percentage = (train_size / total_size) * 100
    test_percentage = (test_size / total_size) * 100

    print(f" - Train size: {train_size} ({train_percentage:.2f}%)")
    print(f" - Test size: {test_size} ({test_percentage:.2f}%)")

# Preload LDA model and transofrm mixture data using the single compounds space
with open(r"C:\Users\resca\OneDrive - Politecnico di Milano\_Dottorato\4 - Code\temperature-enose-data-analysis\mos-v2\Outputs\Features\TEST_R_NORM_ZSCORE\single_lda.pkl", "rb") as file:
    lda = pk.load(file)

# Access explained variance ratio ON SINGLES
explained_variance_ratio = lda.explained_variance_ratio_
print("LDA Cumulative")
print(explained_variance_ratio)
# Plot explained variance
plt.figure(figsize=(8, 6))
plt.bar(range(1, len(explained_variance_ratio) + 1), explained_variance_ratio, alpha=0.7, align='center', color='blue', label='Individual EVR')
plt.step(range(1, len(explained_variance_ratio) + 1), np.cumsum(explained_variance_ratio), where='mid', linestyle='--', color='orange', label='Cumulative EVR')
plt.xlabel('Linear Discriminants')
plt.ylabel('Explained Variance Ratio')
plt.title('Explained Variance Ratio by Linear Discriminant')
plt.legend()
plt.show()

X_train_lda = lda.transform(X_train)
X_test_lda = lda.transform(X_test)
n_components = X_train_lda.shape[1]
lda_feature_names = [f"LD{i+1}" for i in range(n_components)]
corr_matrix = pd.DataFrame(X_train_lda, columns=lda_feature_names).corr()
sns.heatmap(corr_matrix, annot=False, cmap="coolwarm")
plt.show()

# Train a classifier on the LDA-transformed data
#classifier = RandomForestClassifier() #poor
#classifier = SVC(kernel='rbf', probability=True, random_state=42) #very bad
#classifier = LGBMClassifier(random_state=42) #bad
#classifier = XGBClassifier(random_state=42) #bad

# Convert to CatBoost's Pool format (optional but recommended)
train_pool = Pool(X_train_lda, y_train)
test_pool = Pool(X_test_lda, y_test)

# Step 2: Define logging directory
tensorboard_log_dir = "./catboost_tensorboard_logs"
os.makedirs(tensorboard_log_dir, exist_ok=True)

# Step 3: Train CatBoost model with TensorBoard logging
model = CatBoostClassifier(
    iterations=150,
    learning_rate=0.05,
    depth=10,
    eval_metric="Accuracy",
    random_seed=6,
    verbose=50,  # Print progress every 50 iterations
)
#classifier = CatBoostClassifier(verbose=0, random_state=6) #not so bad

model.fit(train_pool, eval_set=test_pool, use_best_model=True)
#classifier.fit(X_train_lda, y_train)

# Predictions
y_pred = model.predict(X_test_lda)
#y_pred = classifier.predict(X_test_lda)

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
classes = sorted(set(y_test))
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=classes, yticklabels=classes)
plt.xlabel("Predicted", fontsize=12)
plt.ylabel("True", fontsize=12)
#plt.title("Confusion Matrix")
plt.show()

print(classification_report(y_test, y_pred))

# Calculate global metrics
accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted')
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')

# Prepare the data for the bar plot
metrics = ['Accuracy', 'F1-Score', 'Precision', 'Recall']
values = [accuracy, f1, precision, recall]

# Create a bar plot
plt.figure(figsize=(8, 6))
bars = plt.bar(metrics, values, color=['blue', 'orange', 'green', 'red'])
plt.ylim(0, 1.2)  # Metrics range from 0 to 1
plt.title('Global Classification Metrics')
plt.xlabel('Metric')
plt.ylabel('Score')
# Add value labels at the top of each bar
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.02, round(yval, 2), ha='center', va='bottom', fontsize=12)
plt.show()

importance = model.feature_importances_
#importance = classifier.feature_importances_
sorted_indices = np.argsort(importance)[::-1]
sorted_lda_feature_names = [lda_feature_names[i] for i in sorted_indices] # Sort the LDA feature names according to the importance order
plt.bar(range(len(importance)), importance[sorted_indices])
plt.xticks(range(len(importance)), sorted_lda_feature_names, rotation=90)
plt.xlabel('LDA Components')
plt.ylabel('Feature Importance')
plt.title('Random Forest Feature Importance After LDA')
plt.tight_layout()
plt.show()