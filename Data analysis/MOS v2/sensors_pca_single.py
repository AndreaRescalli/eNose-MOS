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
OUTPUTS_FOLDER = CURRENT_DIR / "Outputs" / "Features" / "TEST_R_NORM_ZSCORE"
FEATURES_FOLDER = CURRENT_DIR / "Outputs" / "Features" / "TEST_R_NORM_ZSCORE"

# Load data and change concentration
features = pd.read_csv(FEATURES_FOLDER / "single_compounds_features.csv", index_col=0)
features.loc[features.Concentration < 100, "Concentration"] = 75
features.loc[(features.Concentration > 100) & (features.Concentration < 200), "Concentration"] = 150
features.loc[features.Concentration > 290, "Concentration"] = 300
features = features[features["Repetition"] > 0].reset_index(drop=True)
features = features[features["Repetition"] < 6].reset_index(drop=True)

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
    (features.Sensor == "S-1") & (features["Temperature Modulation"] == "Sq+Tr"),
    "Concentration",
]
features_remapped["Compound"] = features.loc[
    (features.Sensor == "S-1") & (features["Temperature Modulation"] == "Sq+Tr"),
    "Compound",
]

features_remapped["Repetition"] = features.loc[
    (features.Sensor == "S-1") & (features["Temperature Modulation"] == "Sq+Tr"),
    "Repetition",
]
features_remapped = features_remapped.reset_index(drop=True)

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

features_remapped_dropna = features_remapped.dropna(axis=0).copy()
features_var_dropna_norm = features_remapped_dropna.drop(
    ["Concentration", "Compound", "Repetition"], axis=1
)
#features_var_dropna_norm = (
#    features_var_dropna_norm - features_var_dropna_norm.min()
#) / (features_var_dropna_norm.max() - features_var_dropna_norm.min())
features_var_dropna_norm = scipy.stats.zscore(features_var_dropna_norm)

# PCA
'''
n_comp = 10
pca = sklearn.decomposition.PCA(n_comp)
x_transf = pca.fit_transform(features_var_dropna_norm)
features_remapped_dropna["PC1"] = x_transf[:, 0]
features_remapped_dropna["PC2"] = x_transf[:, 1]
features_remapped_dropna["PC3"] = x_transf[:, 2]

pk.dump(pca, open(os.path.join(OUTPUTS_FOLDER, "single_pca.pk"), "wb"))

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
features_remapped_dropna.loc[features_remapped_dropna.Compound == "ISO", "xColor"] = 1
features_remapped_dropna.loc[features_remapped_dropna.Compound == "TOL", "xColor"] = 2

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
'''

######################
#       LDA          #
######################
features_remapped_dropna["xColor"] = 0
features_remapped_dropna.loc[features_remapped_dropna.Compound == "ISO", "xColor"] = 1
features_remapped_dropna.loc[features_remapped_dropna.Compound == "TOL", "xColor"] = 2

lda = sklearn.discriminant_analysis.LinearDiscriminantAnalysis(n_components=3)

def apply_cat_conc(x):
    if x < 100:
        return "L"
    elif x >= 100 and x <= 200:
        return "M"
    else:
        return "H"


features_remapped_dropna["ConcentrationCat"] = features_remapped_dropna[
    "Concentration"
].apply(apply_cat_conc)

features_remapped_dropna["Compound-Conc"] = (
    features_remapped_dropna["Compound"]
    + " "
    + features_remapped_dropna["ConcentrationCat"].astype("str")
)

'''
X_r2 = lda.fit_transform(features_var_dropna_norm, features_remapped_dropna["Compound"])
pk.dump(lda, open(os.path.join(OUTPUTS_FOLDER, "single_lda.pkl"), "wb"))

features_remapped_dropna["LD1"] = X_r2[:, 0]
features_remapped_dropna["LD2"] = X_r2[:, 1]

fig, ax = plt.subplots(1, 1, figsize=(8, 6))
scatter1 = sns.scatterplot(
    x="LD1",
    y="LD2",
    data=features_remapped_dropna,
    hue="Compound",
    # size="Concentration",
    # style="Repetition",
    ax=ax,
)
'''

X_r2 = lda.fit_transform(
    features_var_dropna_norm, features_remapped_dropna["Compound-Conc"]
)
pk.dump(lda, open(os.path.join(OUTPUTS_FOLDER, "single_lda.pkl"), "wb"))
features_remapped_dropna["LD1"] = X_r2[:, 0]
features_remapped_dropna["LD2"] = X_r2[:, 1]
features_remapped_dropna["LD3"] = X_r2[:, 2]

fig, ax = plt.subplots(1, 1, figsize=(8, 6))
scatter1 = sns.scatterplot(
    x="LD1",
    y="LD2",
    data=features_remapped_dropna,
    hue="Compound-Conc",
    # size="Concentration",
    # style="Repetition",
    ax=ax,
)

plt.show()

# axes instance
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Convert to DataFrame
df = pd.DataFrame(features_remapped_dropna, columns=["LD1", "LD2", "LD3", "Compound", "ConcentrationCat"])

# Save to a .dat file for LaTeX
df["Class"] = df["Compound"] + "-" + df["ConcentrationCat"]
df.to_csv("LDA_singles_plot_data.dat", index=False, sep="\t")

# Python plotting
compound_colors = {"ACE": "#FF6B6B", "ISO": "#45B7D1", "TOL": "#FAD02E"}
concentration_markers = {"L": "o", "M": "^", "H": "s"}
concentration_order = {"L": 0, "M": 1, "H": 2}

# Initialize the figure and 3D axis
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(projection="3d")

# Plot each compound and concentration combination
legend_entries = []
compounds = ["ACE", "ISO", "TOL"]
concentrations = ["L", "M", "H"]
for compound in compounds:
    for conc_cat in concentrations:
        subset = df[(df["Compound"] == compound) & (df["ConcentrationCat"] == conc_cat)]
        if subset.empty:
            continue
        scatter = ax.scatter(
            subset["LD1"],
            subset["LD2"],
            subset["LD3"],
            color=compound_colors[compound],
            marker=concentration_markers[conc_cat],
            s=100,
            label=f"{compound} {conc_cat}"
        )
        legend_entries.append((scatter, f"{compound} {conc_cat}"))

# Set labels and title
ax.set_xlabel("LD1", fontsize=12)
ax.set_ylabel("LD2", fontsize=12)
ax.set_zlabel("LD3", fontsize=12)

# Create a legend with ordered entries
ordered_legend_entries = sorted(
    legend_entries, 
    key=lambda x: (x[1].split()[0], concentration_order[x[1].split()[1]])
)
handles, labels = zip(*ordered_legend_entries)

# Position the legend outside the plot
ax.legend(
    handles, 
    labels, 
    title="Compound & Concentration", 
    loc="upper right", 
    bbox_to_anchor=(1.3, 1),  # Adjust position for better view
    fontsize=10
)

plt.show()