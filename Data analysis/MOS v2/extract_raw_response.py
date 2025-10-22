import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import seaborn as sns
import click

#_BASE_FOLDER = Path("D:\\_Data\\_eNose\\_Trial-101\\")
_BASE_FOLDER = Path(r"C:\Users\resca\OneDrive - Politecnico di Milano\_Dottorato\6 - Tesisti\2024_2025_Vegetali\2_Misure sacche\_Trial-101")
_SAMPLE_RATE = 0.1
_SENSOR_LABELS = ["S-1", "S-2", "S-3", "S-4", "S-5", "S-6", "S-7", "S-8"]


_SQ_TR_COL = "Sq+Tr"
_SQ_TR_PERIOD_SECONDS = 100
_SQ_TR_PERIOD_SAMPLES = _SQ_TR_PERIOD_SECONDS / _SAMPLE_RATE
_SQ_TR_PERIODS = 12


def get_sq_tr_df(tmp_data, remove_baseline, normalize_cleaning, normalize_max):
    sq_tr_df = pd.DataFrame(columns=["Repetition", "Sensor", "Data", "x"])
    for sensor_label in _SENSOR_LABELS:
        # Convert to resistance
        res_values = (5 / tmp_data[sensor_label]) * 10000 - 10000
        r0 = res_values.loc[tmp_data.Stage == "Cleaning"].mean()
        # We need to find the start and end point of the real measurement phase
        meas_rec_data = res_values[tmp_data["Temperature Modulation"] == _SQ_TR_COL]
        for square_period in range(_SQ_TR_PERIODS):
            if square_period < (_SQ_TR_PERIODS - 1):
                end = int((square_period + 1) * _SQ_TR_PERIOD_SAMPLES)
            else:
                end = -1
            r_initial = meas_rec_data.iloc[int(square_period * _SQ_TR_PERIOD_SAMPLES)]
            if remove_baseline:
                period_data = (
                    meas_rec_data.iloc[int(square_period * _SQ_TR_PERIOD_SAMPLES) : end]
                    - r_initial
                ).reset_index(drop=True)
            else:
                period_data = (
                    meas_rec_data.iloc[int(square_period * _SQ_TR_PERIOD_SAMPLES) : end]
                ).reset_index(drop=True)
            rmax = period_data.max()
            if normalize_cleaning:
                period_data = period_data / r0
            if normalize_max:
                period_data = period_data / rmax
            period_data_df = pd.DataFrame(
                {
                    "Repetition": square_period,
                    "Sensor": sensor_label,
                    "Data": period_data.values,
                    "x": np.arange(len(period_data.values)),
                }
            )
            sq_tr_df = pd.concat([sq_tr_df, period_data_df], ignore_index=True)
    return sq_tr_df


@click.command()
@click.option(
    "--remove-baseline", help="Remove baseline from each response", default=False
)
@click.option(
    "--normalize-cleaning", help="Normalize wrt cleaning resistance", default=False
)
@click.option("--normalize-max", help="Normalize wrt max resistance", default=False)
def extract_single_period_df(remove_baseline, normalize_cleaning, normalize_max):
    single_period_df = pd.DataFrame(
        columns=[
            "Temperature Modulation",
            "Sensor",
            "Compound",
            "Concentration",
            "Repetition",
            "Data",
        ]
    )
    for folder in _BASE_FOLDER.iterdir():
        compound = folder.name.split("_")[0]
        conc = folder.name.split("_")[1][:-3]
        # For each concentration
        folder = _BASE_FOLDER / f"{compound}_{conc}ppm"
        if folder.exists():
            # If the folder exists
            for csv_file in folder.iterdir():
                if csv_file.is_file() and "csv" in csv_file.name:
                    tmp_data = pd.read_csv(csv_file, header=6)
                    temperature_modulation_patterns = tmp_data[
                        "Temperature Modulation"
                    ].unique()
                    if len(temperature_modulation_patterns) == 2:
                        pattern_df = get_sq_tr_df(
                            tmp_data,
                            remove_baseline,
                            normalize_cleaning,
                            normalize_max,
                        )

                        pattern_df["Compound"] = compound
                        pattern_df["Concentration"] = float(conc)
                        pattern_df["Temperature Modulation"] = "Sq+Tr"
                        single_period_df = pd.concat([single_period_df, pattern_df])
    with open("single_period_df.csv", "w") as f:
        f.write(f"%remove_baseline, {remove_baseline}\n")
        f.write(f"%normalize_cleaning, {normalize_cleaning}\n")
        f.write(f"%normalize_max, {normalize_max}\n")
        single_period_df.to_csv(
            f, header=True, index=False, mode="a", lineterminator="\n"
        )


if __name__ == "__main__":
    extract_single_period_df()
