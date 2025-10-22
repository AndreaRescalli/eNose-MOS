import itertools

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import sklearn.decomposition
import sklearn.preprocessing

_SENSOR_LABELS = ["S-1", "S-2", "S-3", "S-4", "S-5", "S-6", "S-7", "S-8"]
_FEATURE_LIST = ["DeltaH", "DeltaL"]
_TEMPERATURE_MODULATION = ["Sine", "Square", "Triangle", "Sq+Tr"]

# Load data and change concentration
features = pd.read_csv("complete_features.csv", index_col=0)
features.loc[features.Concentration == 131, "Concentration"] = 130
features.loc[features.Concentration == 303, "Concentration"] = 300
features = features[features["Repetition"] > 0].reset_index(drop=True)
features = features[features["Repetition"] < 11].reset_index(drop=True)

# Generate new column names
all_columns = list(
    itertools.product(_SENSOR_LABELS, _FEATURE_LIST, _TEMPERATURE_MODULATION)
)
all_columns = [f"{x[0]}-{x[1]}-{x[2]}" for x in all_columns]
all_columns.append("Concentration")
all_columns.append("Compound")

# Set up new dataframe
features_remapped = pd.DataFrame()
features_remapped["Concentration"] = features.loc[
    (features.Sensor == "S-1") & (features["Temperature Modulation"] == "Sine"),
    "Concentration",
]
features_remapped["Compound"] = features.loc[
    (features.Sensor == "S-1") & (features["Temperature Modulation"] == "Sine"),
    "Compound",
]

features_remapped["Repetition"] = features.loc[
    (features.Sensor == "S-1") & (features["Temperature Modulation"] == "Sine"),
    "Repetition",
]
features_remapped = features_remapped.reset_index(drop=True)
print(features_remapped)

for sensor in _SENSOR_LABELS:
    for feature in _FEATURE_LIST:
        for temp_mod in _TEMPERATURE_MODULATION:
            temp_df = features.loc[
                (features.Sensor == sensor)
                & (features["Temperature Modulation"] == temp_mod),
                [feature, "Concentration", "Compound", "Repetition"],
            ]
            temp_df[f"{sensor}-{feature}-{temp_mod}"] = temp_df[feature]
            temp_df = temp_df.drop(feature, axis=1)
            features_remapped = pd.merge(
                features_remapped,
                temp_df,
                on=["Concentration", "Compound", "Repetition"],
                how="outer",
            )
            if len(features_remapped) == 0:
                print(f"{sensor}-{feature}-{temp_mod}")
                raise

print(features_remapped)
features_remapped_dropna = features_remapped.dropna(axis=0).copy()

features_var_dropna_norm = features_remapped_dropna.drop(
    ["Concentration", "Compound", "Repetition"], axis=1
)
features_var_dropna_norm = (
    features_var_dropna_norm - features_var_dropna_norm.min()
) / (features_var_dropna_norm.max() - features_var_dropna_norm.min())

# PCA
n_comp = 10
pca = sklearn.decomposition.PCA(n_comp)
x_transf = pca.fit_transform(features_var_dropna_norm)
features_remapped_dropna["PC1"] = x_transf[:, 0]
features_remapped_dropna["PC2"] = x_transf[:, 1]
features_remapped_dropna["PC3"] = x_transf[:, 2]

# Get the explained variance ratio for each component
explained_variance_ratio = pca.explained_variance_ratio_

# Calculate the cumulative sum of explained variance ratio
cumulative_variance_ratio = np.cumsum(explained_variance_ratio)

# Plot the cumulative explained variance ratio
plt.figure()
plt.plot(range(1, n_comp + 1), cumulative_variance_ratio, marker="o")
plt.xlabel("Number of Principal Components")
plt.ylabel("Cumulative Explained Variance Ratio")
plt.title("Cumulative Explained Variance Ratio vs. Number of Principal Components")
plt.show()

# Print the cumulative explained variance ratios
print("Cumulative Explained Variance Ratios:")
for i, ratio in enumerate(cumulative_variance_ratio):
    print(f"PC{i + 1}: {ratio:.4f}")


legend_handles = []
legend_labels = []

fig = plt.figure()
plt.subplot(1, 3, 1)
scatter1 = sns.scatterplot(
    x="PC1",
    y="PC2",
    data=features_remapped_dropna,
    hue="Compound",
    size="Concentration",
    style="Repetition",
)
handles, labels = scatter1.get_legend_handles_labels()
legend_handles.extend(handles)
legend_labels.extend(labels)
plt.xlabel("PC1")
plt.ylabel("PC2")

plt.subplot(1, 3, 2)
scatter2 = sns.scatterplot(
    x="PC1",
    y="PC3",
    data=features_remapped_dropna,
    hue="Compound",
    size="Concentration",
    style="Repetition",
)
plt.xlabel("PC1")
plt.ylabel("PC3")

plt.subplot(1, 3, 3)
scatter3 = sns.scatterplot(
    x="PC2",
    y="PC3",
    data=features_remapped_dropna,
    hue="Compound",
    size="Concentration",
    style="Repetition",
)
plt.xlabel("PC2")
plt.ylabel("PC3")

# Create a common legend for all subplots
scatter1.legend_.remove()
scatter2.legend_.remove()
scatter3.legend_.remove()
fig.legend(legend_handles, legend_labels, loc="center right")
fig.suptitle("2D visualization of PC1, PC2, and PC3")


features_remapped_dropna["xColor"] = 0
features_remapped_dropna.loc[features_remapped_dropna.Compound == "BUT", "xColor"] = 1
features_remapped_dropna.loc[features_remapped_dropna.Compound == "CH4", "xColor"] = 2


from mpl_toolkits.mplot3d import Axes3D

# axes instance
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(projection="3d")

ax.scatter(
    features_remapped_dropna["PC1"],
    features_remapped_dropna["PC2"],
    features_remapped_dropna["PC3"],
    c=features_remapped_dropna["xColor"],
)
ax.set_title("3D visualization of PC1, PC2, and PC3")
ax.set_xlabel("PC1")
ax.set_ylabel("PC2")
ax.set_zlabel("PC3")

plt.show()


# KNN
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


def combine_cols(row):
    if row["Compound"] == "BUT" and row["Concentration"] == 75:
        return "BUT_075"
    elif row["Compound"] == "BUT" and row["Concentration"] == 130:
        return "BUT_130"
    elif row["Compound"] == "BUT" and row["Concentration"] == 300:
        return "BUT_300"
    elif row["Compound"] == "CH4" and row["Concentration"] == 75:
        return "CH4_075"
    elif row["Compound"] == "CH4" and row["Concentration"] == 130:
        return "CH4_130"
    elif row["Compound"] == "CH4" and row["Concentration"] == 300:
        return "CH4_300"
    elif row["Compound"] == "CO2" and row["Concentration"] == 75:
        return "CO2_075"
    elif row["Compound"] == "CO2" and row["Concentration"] == 130:
        return "CO2_130"
    elif row["Compound"] == "CO2" and row["Concentration"] == 300:
        return "CO2_300"
    else:
        return None  # Or any default value if no condition is satisfied


features_remapped_dropna["Target"] = features_remapped_dropna.apply(
    combine_cols, axis=1
)
label_encoder = LabelEncoder()
features_remapped_dropna["Target"] = label_encoder.fit_transform(
    features_remapped_dropna["Target"]
)
y = features_remapped_dropna["Target"]  # Target variable

X = features_remapped_dropna[["PC1", "PC2", "PC3"]]  # Features

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Initialize the k-NN classifier
knn_classifier = KNeighborsClassifier(n_neighbors=8)

# Perform 4-fold cross-validation on the training data
cv_scores = cross_val_score(knn_classifier, X_train, y_train, cv=4)

# Print the cross-validation scores for each fold
print("Cross-validation scores:", cv_scores)

# Calculate and print the average cross-validation score
avg_cv_score = cv_scores.mean()
print("Average cross-validation score:", avg_cv_score)

# Train the classifier on the training data
knn_classifier.fit(X_train, y_train)

# Make predictions on the testing data
y_pred = knn_classifier.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
# Calculate precision
precision = precision_score(y_test, y_pred, average="macro")
# Calculate recall
recall = recall_score(y_test, y_pred, average="macro")
# Calculate F1-score
f1 = f1_score(y_test, y_pred, average="macro")
# Confusion matrix
confusion_mat = confusion_matrix(y_test, y_pred)

# Create a confusion matrix heatmap
plt.figure(figsize=(7, 7))
sns.heatmap(
    confusion_mat,
    annot=True,
    fmt="d",
    cmap="Blues",
    square=True,
    xticklabels=label_encoder.classes_,
    yticklabels=label_encoder.classes_,
)
plt.xlabel("Predicted Labels")
plt.ylabel("True Labels")
plt.title("Confusion Matrix")
plt.show()

# Create a bar plot for precision, recall, and F1-score
metrics_dict = {"Precision": precision, "Recall": recall, "F1-score": f1}
plt.figure(figsize=(8, 5))
sns.barplot(x=list(metrics_dict.keys()), y=list(metrics_dict.values()))
plt.ylabel("Score")
plt.title("Performance Metrics")
plt.show()
