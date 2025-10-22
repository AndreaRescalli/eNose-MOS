import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import seaborn as sns
import click

_COMPOUNDS = ["BUT", "CH4", "CO2"]
_CONCENTRATIONS = ["75", "131", "130", "303"]
_BASE_FOLDER = Path("E:\My Drive\_Papers\_2023_Chemosensors\_Data\Trial_002")
# _BASE_FOLDER = Path("C:/Users/resca/OneDrive - Politecnico di Milano/_Dottorato/6 - Tesisti/2021_2022_Tasso/_Data/_Trial-002")
_SAMPLE_RATE = 0.1
_SENSOR_LABELS = ["S-1", "S-2", "S-3", "S-4", "S-5", "S-6", "S-7", "S-8"]

_SINE_COL = "Sine"
_SINE_PERIOD_SECONDS = 50
_SINE_PERIOD_SAMPLES = _SINE_PERIOD_SECONDS / _SAMPLE_RATE
_SINE_PERIODS = 12

_SQUARE_COL = "Square"
_SQUARE_PERIOD_SECONDS = 60
_SQUARE_PERIOD_SAMPLES = _SQUARE_PERIOD_SECONDS / _SAMPLE_RATE
_SQUARE_PERIODS = 12

_SQ_TR_COL = "Sq+Tr"
_SQ_TR_PERIOD_SECONDS = 100
_SQ_TR_PERIOD_SAMPLES = _SQ_TR_PERIOD_SECONDS / _SAMPLE_RATE
_SQ_TR_PERIODS = 12

_TRIANGLE_COL = "Triangle"
_TRIANGLE_PERIOD_SECONDS = 100
_TRIANGLE_PERIOD_SAMPLES = _TRIANGLE_PERIOD_SECONDS / _SAMPLE_RATE
_TRIANGLE_PERIODS = 12


def get_sine_df(tmp_data, remove_baseline, normalize_cleaning, normalize_max):
    sine_df = pd.DataFrame(columns=["Repetition", "Sensor", "Data", "x"])
    for sensor_label in _SENSOR_LABELS:
        # Convert to resistance
        res_values = (5 / tmp_data[sensor_label]) * 10000 - 10000
        r0 = res_values.loc[tmp_data.Stage == "Cleaning"].mean()
        # We need to find the start and end point of the real measurement phase
        meas_rec_data = res_values[tmp_data["Temperature Modulation"] == _SINE_COL]
        for sine_period in range(_SINE_PERIODS):
            if sine_period < (_SINE_PERIODS - 1):
                end = int((sine_period + 1) * _SINE_PERIOD_SAMPLES)
            else:
                end = -1
            r_initial = meas_rec_data.iloc[int(sine_period * _SINE_PERIOD_SAMPLES)]
            if remove_baseline:
                period_data = (
                    meas_rec_data.iloc[int(sine_period * _SINE_PERIOD_SAMPLES) : end]
                    - r_initial
                ).reset_index(drop=True)
            else:
                period_data = (
                    meas_rec_data.iloc[int(sine_period * _SINE_PERIOD_SAMPLES) : end]
                ).reset_index(drop=True)
            rmax = period_data.max()
            if normalize_cleaning:
                period_data = period_data / r0
            if normalize_max:
                period_data = period_data / rmax
            period_data_df = pd.DataFrame(
                {
                    "Repetition": sine_period,
                    "Sensor": sensor_label,
                    "Data": period_data.values,
                    "x": np.arange(len(period_data.values)),
                }
            )
            sine_df = pd.concat([sine_df, period_data_df], ignore_index=True)
    return sine_df


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


def get_triangle_df(tmp_data, remove_baseline, normalize_cleaning, normalize_max):
    sq_tr_df = pd.DataFrame(columns=["Repetition", "Sensor", "Data", "x"])
    for sensor_label in _SENSOR_LABELS:
        # Convert to resistance
        res_values = (5 / tmp_data[sensor_label]) * 10000 - 10000
        r0 = res_values.loc[tmp_data.Stage == "Cleaning"].mean()
        # We need to find the start and end point of the real measurement phase
        meas_rec_data = res_values[tmp_data["Temperature Modulation"] == _TRIANGLE_COL]
        for triangle_period in range(_TRIANGLE_PERIODS):
            if triangle_period < (_TRIANGLE_PERIOD_SAMPLES - 1):
                end = int((triangle_period + 1) * _TRIANGLE_PERIOD_SAMPLES)
            else:
                end = -1
            r_initial = meas_rec_data.iloc[
                int(triangle_period * _TRIANGLE_PERIOD_SAMPLES)
            ]
            if remove_baseline:
                period_data = (
                    meas_rec_data.iloc[
                        int(triangle_period * _TRIANGLE_PERIOD_SAMPLES) : end
                    ]
                    - r_initial
                ).reset_index(drop=True)
            else:
                period_data = (
                    meas_rec_data.iloc[
                        int(triangle_period * _TRIANGLE_PERIOD_SAMPLES) : end
                    ]
                ).reset_index(drop=True)
            rmax = period_data.max()
            if normalize_cleaning:
                period_data = period_data / r0
            if normalize_max:
                period_data = period_data / rmax
            period_data_df = pd.DataFrame(
                {
                    "Repetition": triangle_period,
                    "Sensor": sensor_label,
                    "Data": period_data.values,
                    "x": np.arange(len(period_data.values)),
                }
            )
            sq_tr_df = pd.concat([sq_tr_df, period_data_df], ignore_index=True)
    return sq_tr_df


def get_square_df(tmp_data, remove_baseline, normalize_cleaning, normalize_max):
    square_df = pd.DataFrame(columns=["Repetition", "Sensor", "Data", "x"])
    for sensor_label in _SENSOR_LABELS:
        # Convert to resistance
        res_values = (5 / tmp_data[sensor_label]) * 10000 - 10000
        r0 = res_values.loc[tmp_data.Stage == "Cleaning"].mean()
        # We need to find the start and end point of the real measurement phase
        meas_rec_data = res_values[tmp_data["Temperature Modulation"] == _SQUARE_COL]
        for square_period in range(_SQUARE_PERIODS):
            if square_period < (_SQUARE_PERIODS - 1):
                end = int((square_period + 1) * _SQUARE_PERIOD_SAMPLES)
            else:
                end = -1
            r_initial = meas_rec_data.iloc[int(square_period * _SQUARE_PERIOD_SAMPLES)]
            if remove_baseline:
                period_data = (
                    meas_rec_data.iloc[
                        int(square_period * _SQUARE_PERIOD_SAMPLES) : end
                    ]
                    - r_initial
                ).reset_index(drop=True)
            else:
                period_data = (
                    meas_rec_data.iloc[
                        int(square_period * _SQUARE_PERIOD_SAMPLES) : end
                    ]
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
            square_df = pd.concat([square_df, period_data_df], ignore_index=True)
    return square_df


def get_ramp_df(tmp_data, remove_baseline, normalize_cleaning, normalize_max):
    ramp_df = pd.DataFrame(columns=["Repetition", "Sensor", "Data", "x"])
    for sensor_label in _SENSOR_LABELS:
        # Convert to resistance
        res_values = (5 / tmp_data[sensor_label]) * 10000 - 10000
        r0 = res_values.loc[tmp_data.Stage == "Cleaning"].mean()
        # We need to find the start and end point of the real measurement phase
        meas_rec_data = res_values[tmp_data["Temperature Modulation"] == "Ramp"]

        r_initial = meas_rec_data.iloc[0]
        if remove_baseline:
            period_data = (meas_rec_data - r_initial).reset_index(drop=True)
        else:
            period_data = (meas_rec_data).reset_index(drop=True)
        rmax = period_data.max()
        if normalize_cleaning:
            period_data = period_data / r0
        if normalize_max:
            period_data = period_data / rmax
        period_data_df = pd.DataFrame(
            {
                "Repetition": 0,
                "Sensor": sensor_label,
                "Data": period_data.values,
                "x": np.arange(len(period_data.values)),
            }
        )
        ramp_df = pd.concat([ramp_df, period_data_df], ignore_index=True)
    return ramp_df


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
    for compound in _COMPOUNDS:
        # For each compound
        for conc in _CONCENTRATIONS:
            # For each concentration
            folder = _BASE_FOLDER / f"{compound}_{conc}ppm"
            if folder.exists():
                # If the folder exists
                for csv_file in folder.iterdir():
                    if (
                        csv_file.is_file()
                        and "csv" in csv_file.name
                        and "notprecise" not in csv_file.name
                    ):
                        tmp_data = pd.read_csv(csv_file, header=6)
                        temperature_modulation_patterns = tmp_data[
                            "Temperature Modulation"
                        ].unique()
                        if len(temperature_modulation_patterns) == 2:
                            pattern = tmp_data[
                                tmp_data["Temperature Modulation"] != "5V"
                            ]["Temperature Modulation"].unique()[0]
                            if pattern == "Sine":
                                pattern_df = get_sine_df(
                                    tmp_data,
                                    remove_baseline,
                                    normalize_cleaning,
                                    normalize_max,
                                )
                            elif pattern == "Square":
                                pattern_df = get_square_df(
                                    tmp_data,
                                    remove_baseline,
                                    normalize_cleaning,
                                    normalize_max,
                                )
                            elif pattern == "Sq+Tr":
                                pattern_df = get_sq_tr_df(
                                    tmp_data,
                                    remove_baseline,
                                    normalize_cleaning,
                                    normalize_max,
                                )
                            elif pattern == "Triangle":
                                pattern_df = get_triangle_df(
                                    tmp_data,
                                    remove_baseline,
                                    normalize_cleaning,
                                    normalize_max,
                                )
                            elif pattern == "Ramp":
                                pattern_df = get_ramp_df(
                                    tmp_data,
                                    remove_baseline,
                                    normalize_cleaning,
                                    normalize_max,
                                )
                            if pattern in (
                                ["Sine", "Square", "Sq+Tr", "Triangle", "Ramp"]
                            ):
                                pattern_df["Compound"] = compound
                                pattern_df["Concentration"] = float(conc)
                                pattern_df["Temperature Modulation"] = pattern
                                single_period_df = pd.concat(
                                    [single_period_df, pattern_df]
                                )
    with open("single_period_df.csv", "w") as f:
        f.write(f"%remove_baseline, {remove_baseline}\n")
        f.write(f"%normalize_cleaning, {normalize_cleaning}\n")
        f.write(f"%normalize_max, {normalize_max}\n")
        single_period_df.to_csv(
            f, header=True, index=False, mode="a", lineterminator="\n"
        )


if __name__ == "__main__":
    extract_single_period_df()
