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


features_remapped_dropna = features_remapped.dropna(axis=0).copy()
features_var_dropna_norm = features_remapped_dropna.drop(
    ["Mixture", "Repetition", "Acetone", "Toluene", "Isopropanol"], axis=1
)
features_var_dropna_norm = scipy.stats.zscore(features_var_dropna_norm)


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle as pk
from matplotlib import cm
from matplotlib.colors import to_hex
import sklearn.discriminant_analysis

# Assuming your features and labels are already loaded as features_remapped_dropna and features_var_dropna_norm
color_map = [
    (255, 128, 128),  # Light red
    (128, 255, 128),  # Light green
    (128, 128, 255),  # Light blue
    (255, 255, 128),  # Light yellow
    (255, 128, 255),  # Light magenta
    (128, 255, 255),  # Light cyan
    (255, 191, 64),   # Orange
    (64, 191, 255),   # Sky blue
    (230, 51, 102),   # Pinkish red
    (204, 153, 51),   # Tan
    (153, 102, 230),  # Purple
    (77, 255, 153),   # Greenish cyan
    (179, 179, 179),  # Gray
    (230, 153, 153),  # Light pink
    (51, 204, 128),   # Emerald green
    (153, 51, 204),   # Violet
    (179, 230, 77),   # Lime green
    (102, 102, 153),  # Steel blue
    (204, 204, 102),  # Olive
    (77, 179, 230),   # Light blue
    (102, 153, 204),  # Cornflower blue
    (230, 77, 153),   # Raspberry pink
    (153, 204, 77),   # Yellow-green
    (77, 230, 153),   # Aquamarine
    (51, 51, 204),    # Royal blue
    (179, 77, 230),   # Orchid
    (128, 204, 153),  # Mint green
]
# Convert color map to hexadecimal
hex_colors = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in color_map]

############################
#         LDA              #
############################
# Remove dashes from the 'Mixture' column
features_remapped_dropna["Mixture"] = features_remapped_dropna["Mixture"].str.replace("-", "", regex=False)
# Encode the 'Mixture' column to numeric values
mixture_labels, mixture_encoded = np.unique(features_remapped_dropna["Mixture"], return_inverse=True)
print(mixture_labels)
print('----------------')
print(mixture_encoded)

# Create a colormap
colormap = cm.get_cmap('tab20', len(mixture_labels))
colors = [to_hex(color) for color in colormap(mixture_encoded)]  # Convert to hex
# Create symbolic names for each mixture
symbolic_labels = [i for i in range(len(mixture_labels))]
mixture_to_symbolic = dict(zip(mixture_labels, symbolic_labels))

# Perform LDA transformation
lda = sklearn.discriminant_analysis.LinearDiscriminantAnalysis(n_components=3)
X_r2 = lda.fit_transform(features_var_dropna_norm, features_remapped_dropna["Mixture"])

# Add LDA components to the dataframe
features_remapped_dropna["LD1"] = X_r2[:, 0]
features_remapped_dropna["LD2"] = X_r2[:, 1]
features_remapped_dropna["LD3"] = X_r2[:, 2]
features_remapped_dropna["SymbolicLabel"] = features_remapped_dropna["Mixture"].map(mixture_to_symbolic)

# Compute centroids for each class in the LDA-transformed space
centroids = features_remapped_dropna.groupby("Mixture")[["LD1", "LD2", "LD3"]].mean()

# Calculate the Euclidean distance of each observation from its class centroid
features_remapped_dropna["Dispersity_LDA1"] = features_remapped_dropna.apply(
    lambda row: np.linalg.norm(
        row[["LD1", "LD2", "LD3"]] - centroids.loc[row["Mixture"]].values
    ),
    axis=1,
)

# Calculate the mean dispersity for each class
class_dispersity_LDA1 = features_remapped_dropna.groupby("Mixture")["Dispersity_LDA1"].mean().reset_index()

# Visualization: Bar plot of dispersity (First LDA)
plt.figure(figsize=(12, 6))
sns.barplot(x="Mixture", y="Dispersity_LDA1", data=class_dispersity_LDA1, palette=hex_colors)
plt.xticks(rotation=90)
plt.xlabel("Mixture")
plt.ylabel("Dispersity [a.u.]")
plt.tight_layout()
plt.show()

##########################
# Second LDA - "Single" #
##########################

# REMAPPING MIXTURES INTO SINGLES SPACE
with open(r"C:\Users\resca\OneDrive - Politecnico di Milano\_Dottorato\4 - Code\temperature-enose-data-analysis\mos-v2\Outputs\Features\TEST_R_NORM_ZSCORE\single_lda.pkl", "rb") as file:
    lda_single = pk.load(file)

X_r2_single = lda_single.transform(features_var_dropna_norm)
features_remapped_dropna["LD1_Single"] = X_r2_single[:, 0]
features_remapped_dropna["LD2_Single"] = X_r2_single[:, 1]
features_remapped_dropna["LD3_Single"] = X_r2_single[:, 2]

# Compute centroids for the second LDA-transformed space
centroids_single = features_remapped_dropna.groupby("Mixture")[["LD1_Single", "LD2_Single", "LD3_Single"]].mean()

# Calculate the Euclidean distance of each observation from its class centroid (Second LDA)
features_remapped_dropna["Dispersity_LDA2"] = features_remapped_dropna.apply(
    lambda row: np.linalg.norm(
        row[["LD1_Single", "LD2_Single", "LD3_Single"]] - centroids_single.loc[row["Mixture"]].values
    ),
    axis=1,
)

# Calculate the mean dispersity for each class in the second LDA space
class_dispersity_LDA2 = features_remapped_dropna.groupby("Mixture")["Dispersity_LDA2"].mean().reset_index()

# Visualization: Bar plot of dispersity (Second LDA)
plt.figure(figsize=(12, 6))
sns.barplot(x="Mixture", y="Dispersity_LDA2", data=class_dispersity_LDA2, palette=hex_colors)
plt.xticks(rotation=90)
plt.xlabel("Mixture", fontsize=20)
plt.ylabel("Dispersity [a.u.]", fontsize=20)
plt.tight_layout()
plt.show()

##########################
# Save data to CSV for LaTeX
##########################

# Merge both dispersity dataframes for comparison
dispersity_df = pd.merge(
    class_dispersity_LDA1,
    class_dispersity_LDA2,
    on="Mixture",
    suffixes=("_LDA1", "_LDA2"),
)
dispersity_df["SymbolicLabel"] = dispersity_df["Mixture"].map(mixture_to_symbolic)

# Save the dispersity data to a CSV file for later use in LaTeX
dispersity_df.to_csv("dispersity_data.csv", index=False)