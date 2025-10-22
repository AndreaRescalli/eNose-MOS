import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import seaborn as sns
import click


@click.command()
@click.option("--modulation", help="Temperature modulation pattern", default="Sine")
def visualize_data(modulation):
    with open("single_period_df.csv", "r") as f:
        first_line = f.readline()
        remove_baseline = first_line.split(",")[1][1:-1]
        if remove_baseline == "True":
            remove_baseline = True
        else:
            remove_baseline = False
        second_line = f.readline()
        normalize_cleaning = second_line.split(",")[1][1:-1]
        if normalize_cleaning == "True":
            normalize_cleaning = True
        else:
            normalize_cleaning = False
        normalize_max = f.readline().split(",")[1][1:-1]
        if normalize_max == "True":
            normalize_max = True
        else:
            normalize_max = False
    if modulation == "Ramp":
        min_rep = 0
    else:
        min_rep = 1
    single_period_df = pd.read_csv("single_period_df.csv", header=3)
    single_period_df.Data = single_period_df.Data.round(decimals=2)
    single_period_df["Time"] = single_period_df.x / 10
    single_period_df.loc[single_period_df.Concentration == 131, "Concentration"] = 130
    single_period_df = single_period_df[
        single_period_df["Temperature Modulation"] == modulation
    ]
    g = sns.FacetGrid(
        data=single_period_df[
            (single_period_df.Sensor.isin(["S-1", "S-2", "S-3", "S-4"]))
            & (single_period_df.Repetition >= min_rep)
            & (single_period_df.Repetition < 11)
        ],
        col="Sensor",
        row="Compound",
    )
    g.map(sns.lineplot, "Time", "Data", "Concentration")
    g.add_legend()
    if not remove_baseline and not normalize_cleaning:
        g.set_axis_labels(x_var="Time (s)", y_var="Resistance ($\Omega$)")
    elif remove_baseline and not normalize_cleaning:
        g.set_axis_labels(x_var="Time (s)", y_var="$(R_s-R_b) (\Omega$)")
    elif not remove_baseline and normalize_cleaning:
        g.set_axis_labels(x_var="Time (s)", y_var="$R_s/R_0$")
    else:
        g.set_axis_labels(x_var="Time (s)", y_var="$(R_s-R_b)/R_0$")

    g = sns.FacetGrid(
        data=single_period_df[
            (single_period_df.Sensor.isin(["S-5", "S-6"]))
            & (single_period_df.Repetition >= min_rep)
            & (single_period_df.Repetition < 11)
        ],
        col="Sensor",
        row="Compound",
    )
    g.map(sns.lineplot, "Time", "Data", "Concentration")
    g.add_legend()
    if not remove_baseline and not normalize_cleaning:
        g.set_axis_labels(x_var="Time (s)", y_var="Resistance ($\Omega$)")
    elif remove_baseline and not normalize_cleaning:
        g.set_axis_labels(x_var="Time (s)", y_var="$(R_s-R_b) (\Omega$)")
    elif not remove_baseline and normalize_cleaning:
        g.set_axis_labels(x_var="Time (s)", y_var="$R_s/R_0$")
    else:
        g.set_axis_labels(x_var="Time (s)", y_var="$(R_s-R_b)/R_0$")

    g = sns.FacetGrid(
        data=single_period_df[
            (single_period_df.Sensor.isin(["S-7", "S-8"]))
            & (single_period_df.Repetition >= min_rep)
            & (single_period_df.Repetition < 11)
        ],
        col="Sensor",
        row="Compound",
    )
    g.map(sns.lineplot, "Time", "Data", "Concentration")
    g.add_legend()
    if not remove_baseline and not normalize_cleaning:
        g.set_axis_labels(x_var="Time (s)", y_var="Resistance ($\Omega$)")
    elif remove_baseline and not normalize_cleaning:
        g.set_axis_labels(x_var="Time (s)", y_var="$(R_s-R_b) (\Omega$)")
    elif not remove_baseline and normalize_cleaning:
        g.set_axis_labels(x_var="Time (s)", y_var="$R_s/R_0$")
    else:
        g.set_axis_labels(x_var="Time (s)", y_var="$(R_s-R_b)/R_0$")
    # plt.suptitle(f"{modulation}")
    plt.show()


if __name__ == "__main__":
    visualize_data()
