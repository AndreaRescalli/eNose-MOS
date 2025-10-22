import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

data = pd.read_csv("complete_features.csv")
data.loc[data.Concentration == 131, "Concentration"] = 130
data.loc[data.Concentration == 303, "Concentration"] = 300

# Square
g = sns.FacetGrid(
    data=data[
        (data.Repetition > 0)
        & (data.Repetition < 11)
        & (data["Temperature Modulation"] == "Triangle")
        & (data["Sensor"].isin(["S-1", "S-6"]))
    ],
    col="Sensor",
    row="Compound",
)
g.map(sns.boxplot, "Concentration", "SlopeH")



'''
g = sns.FacetGrid(
    data=data[
        (data.Repetition > 0)
        & (data.Repetition < 11)
        & (data["Temperature Modulation"] == "Triangle")
        & (data["Sensor"].isin(["S-5", "S-6"]))
    ],
    col="Sensor",
    row="Compound",
)
g.map(sns.boxplot, "Concentration", "SlopeH")

g = sns.FacetGrid(
    data=data[
        (data.Repetition > 0)
        & (data.Repetition < 11)
        & (data["Temperature Modulation"] == "Triangle")
        & (data["Sensor"].isin(["S-7", "S-8"]))
    ],
    col="Sensor",
    row="Compound",
)
g.map(sns.boxplot, "Concentration", "SlopeH")





g = sns.FacetGrid(
    data=data[
        (data.Repetition > 0)
        & (data.Repetition < 11)
        & (data["Temperature Modulation"] == "Square")
        & (data["Sensor"].isin(["S-1", "S-2", "S-3", "S-4"]))
    ],
    col="Sensor",
    row="Compound",
)
g.map(sns.boxplot, "Concentration", "DeltaH")


g = sns.FacetGrid(
    data=data[
        (data.Repetition > 0)
        & (data.Repetition < 11)
        & (data["Temperature Modulation"] == "Sine")
        & (data["Sensor"].isin(["S-1", "S-2", "S-3", "S-4"]))
    ],
    col="Sensor",
    row="Compound",
)
g.map(sns.boxplot, "Concentration", "SlopeH")

g = sns.FacetGrid(
    data=data[
        (data.Repetition > 0)
        & (data.Repetition < 11)
        & (data["Temperature Modulation"] == "Triangle")
        & (data["Sensor"].isin(["S-1", "S-2", "S-3", "S-4"]))
    ],
    col="Sensor",
    row="Compound",
)
g.map(sns.boxplot, "Concentration", "DeltaH")
'''

plt.show()
