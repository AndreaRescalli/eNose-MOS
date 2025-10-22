"""
This script performs PCA on the data collected with the mixture
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
OUTPUTS_FOLDER = CURRENT_DIR / "Outputs" / "Features MIX" / "TEST_R_NORM_ZSCORE"
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
print(features_remapped)


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

print(features_remapped)
features_remapped_dropna = features_remapped.dropna(axis=0).copy()

# features_remapped_dropna = (
#    features_remapped_dropna.groupby("Mixture").mean().reset_index()
# )
print(features_remapped_dropna)
features_var_dropna_norm = features_remapped_dropna.drop(
    ["Mixture", "Repetition", "Acetone", "Toluene", "Isopropanol"], axis=1
)
#features_var_dropna_norm = (
#    features_var_dropna_norm - features_var_dropna_norm.min()
#) / (features_var_dropna_norm.max() - features_var_dropna_norm.min())

features_var_dropna_norm = scipy.stats.zscore(features_var_dropna_norm)


# PCA
single_pca: sklearn.decomposition.PCA = pk.load(
    open(r"C:\Users\resca\OneDrive - Politecnico di Milano\_Dottorato\4 - Code\temperature-enose-data-analysis\mos-v2\Outputs\Features\TEST_R_NORM_ZSCORE\single_pca.pk", "rb")
)

x_transf_single = single_pca.transform(features_var_dropna_norm)
features_remapped_dropna["Single_PC1"] = x_transf_single[:, 0]
features_remapped_dropna["Single_PC2"] = x_transf_single[:, 1]
features_remapped_dropna["Single_PC3"] = x_transf_single[:, 2]

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
    hue="Mixture",
    # size="Acetone",
    # style="Repetition",
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
    hue="Mixture",
    # size="Acetone",
    # style="Repetition",
)
plt.xlabel("PC1")
plt.ylabel("PC3")

plt.subplot(1, 3, 3)
scatter3 = sns.scatterplot(
    x="PC2",
    y="PC3",
    data=features_remapped_dropna,
    hue="Mixture",
    # size="Acetone",
    # style="Repetition",
)
plt.xlabel("PC2")
plt.ylabel("PC3")

# Create a common legend for all subplots
scatter1.legend_.remove()
scatter2.legend_.remove()
scatter3.legend_.remove()
fig.legend(legend_handles, legend_labels, loc="center right")
fig.suptitle("2D visualization of PC1, PC2, and PC3 - PCA from Mixtures ")

## Plot using PCA from single compounds
legend_handles = []
legend_labels = []

fig = plt.figure()
plt.subplot(1, 3, 1)
scatter1 = sns.scatterplot(
    x="Single_PC1",
    y="Single_PC2",
    data=features_remapped_dropna,
    hue="Mixture",
)
handles, labels = scatter1.get_legend_handles_labels()
legend_handles.extend(handles)
legend_labels.extend(labels)
plt.xlabel("PC1")
plt.ylabel("PC2")

plt.subplot(1, 3, 2)
scatter2 = sns.scatterplot(
    x="Single_PC1",
    y="Single_PC3",
    data=features_remapped_dropna,
    hue="Mixture",
)
plt.xlabel("PC1")
plt.ylabel("PC3")

plt.subplot(1, 3, 3)
scatter3 = sns.scatterplot(
    x="Single_PC2",
    y="Single_PC3",
    data=features_remapped_dropna,
    hue="Mixture",
)
plt.xlabel("PC2")
plt.ylabel("PC3")

# Create a common legend for all subplots
scatter1.legend_.remove()
scatter2.legend_.remove()
scatter3.legend_.remove()
fig.legend(legend_handles, legend_labels, loc="center right")
fig.suptitle("2D visualization of PC1, PC2, and PC3 - PCA from Single Compounds")
plt.show()


######################
#       LDA          #
######################
# Encode the 'Mixture' column to numeric values
mixture_labels, mixture_encoded = np.unique(features_remapped_dropna["Mixture"], return_inverse=True)

# Create a colormap
from matplotlib.colors import to_hex
colormap = cm.get_cmap('tab20', len(mixture_labels))
colors = [to_hex(color) for color in colormap(mixture_encoded)]  # Convert to hex
# Create symbolic names for each mixture
symbolic_labels = [f"class{i+1}" for i in range(len(mixture_labels))]
mixture_to_symbolic = dict(zip(mixture_labels, symbolic_labels))

lda = sklearn.discriminant_analysis.LinearDiscriminantAnalysis(n_components=3)
X_r2 = lda.fit_transform(features_var_dropna_norm, features_remapped_dropna["Mixture"])

features_remapped_dropna["LD1"] = X_r2[:, 0]
features_remapped_dropna["LD2"] = X_r2[:, 1]
features_remapped_dropna["LD3"] = X_r2[:, 2]
features_remapped_dropna["SymbolicLabel"] = features_remapped_dropna["Mixture"].map(mixture_to_symbolic)

fig, ax = plt.subplots(1, 1, figsize=(8, 6))
scatter1 = sns.scatterplot(
    x="LD1",
    y="LD2",
    data=features_remapped_dropna,
    hue="Mixture",
    ax=ax,
)
ax.set_title("LD1 and LD2 - LDA from Mixtures")

# 3D
# Prepare data for export
data_to_export = pd.DataFrame({
    "LD1": features_remapped_dropna["LD1"],
    "LD2": features_remapped_dropna["LD2"],
    "LD3": features_remapped_dropna["LD3"],
    "SymbolicLabel": features_remapped_dropna["SymbolicLabel"]
})

# Save to a .dat file
data_to_export.to_csv("LDA_mix_from_mix_plot_data.dat", sep=" ", index=False, header=False)

fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(projection="3d")

ax.scatter(
    features_remapped_dropna["LD1"],
    features_remapped_dropna["LD2"],
    features_remapped_dropna["LD3"],
    c=colors,
)
#ax.set_title("3D visualization of LD1, LD2, and LD3")
ax.set_xlabel("LD1", fontsize=12)
ax.set_ylabel("LD2", fontsize=12)
ax.set_zlabel("LD3", fontsize=12)
#for label, color in zip(mixture_labels, colormap.colors[:len(mixture_labels)]):
    #ax.scatter([], [], [], color=color, label=label)  # Dummy points for legend

plt.show()


## REMAPPING MIXTURES INTO SINGLES SPACE
with open(r"C:\Users\resca\OneDrive - Politecnico di Milano\_Dottorato\4 - Code\temperature-enose-data-analysis\mos-v2\Outputs\Features\TEST_R_NORM_ZSCORE\single_lda.pkl", "rb") as file:
    lda_single = pk.load(file)
X_r2 = lda_single.transform(features_var_dropna_norm)
features_remapped_dropna["LD1_Single"] = X_r2[:, 0]
features_remapped_dropna["LD2_Single"] = X_r2[:, 1]
features_remapped_dropna["LD3_Single"] = X_r2[:, 2]

fig, ax = plt.subplots(1, 1, figsize=(8, 6))
scatter1 = sns.scatterplot(
    x="LD1_Single",
    y="LD2_Single",
    data=features_remapped_dropna,
    hue="Mixture",
    ax=ax,
)
ax.set_title("LD1 and LD2 - LDA from Single")
plt.show()

# 3D
data_to_export = pd.DataFrame({
    "LD1": features_remapped_dropna["LD1_Single"],
    "LD2": features_remapped_dropna["LD2_Single"],
    "LD3": features_remapped_dropna["LD3_Single"],
    "SymbolicLabel": features_remapped_dropna["SymbolicLabel"]
})

# Save to a .dat file
data_to_export.to_csv("LDA_mix_from_singles_plot_data.dat", sep=" ", index=False, header=False)

fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(projection="3d")

ax.scatter(
    features_remapped_dropna["LD1_Single"],
    features_remapped_dropna["LD2_Single"],
    features_remapped_dropna["LD3_Single"],
    c=colors,
)
#ax.set_title("3D visualization of LD1, LD2, and LD3")
ax.set_xlabel("LD1", fontsize=12)
ax.set_ylabel("LD2", fontsize=12)
ax.set_zlabel("LD3", fontsize=12)
#for label, color in zip(mixture_labels, colormap.colors[:len(mixture_labels)]):
    #ax.scatter([], [], [], color=color, label=label)  # Dummy points for legend

plt.show()
