"""
This script extract all the features from the data collected with MOS Sensors.
The following compounds and concentrations (ppm) were tested:
- Acetone
    - 75
    - 131
    - 300
- Isopropanol
    - 75
    - 130
    - 300
- Toluene
    - 75
    - 130
    - 300

All the files are loaded, and the features and extracted. The output of this script
is a csv file with the following columns:

Repetition | Feature1 | Feature2 | ... | ... | Compound | Concentration | Temperature Modulation | Sensor |

Where:
- Compound: the compound under analysis
- Concentration: the concentration of the compound
- Temperature Modulation: the applied temperature modulation pattern
- Sensor: the sensor from which the feature was extracted
"""

import click
import pandas as pd
import os
from pathlib import Path
import matplotlib.pyplot as plt
import scipy.integrate
import scipy.signal
import scipy.stats
import numpy as np
import sys
from loguru import logger
import pathlib
from typing import Optional

CURRENT_DIR = pathlib.Path(__file__).parent.resolve()

_BASE_FOLDER = Path(r"C:\Users\resca\OneDrive - Politecnico di Milano\_Dottorato\6 - Tesisti\2024_2025_Vegetali\2_Misure sacche\_Trial-101")
_OUTPUT_DIR = CURRENT_DIR / Path("Outputs") / "Features" / "TEST_R_NORM_ZSCORE"
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
_OUTPUT_DIR_SVG = CURRENT_DIR / Path("Outputs") / "Features" / "TEST_R_NORM_ZSCORE" / "Plots"
_OUTPUT_DIR_SVG.mkdir(parents=True, exist_ok=True)

_SAMPLE_RATE = 0.1
_SENSOR_LABELS = ["S-1", "S-2", "S-3", "S-4", "S-5", "S-6"]#, "S-7", "S-8"]
STAGE_COL = "Stage"
SENSOR_COL = "Sensor"
REPETITION_COL = "Repetition"
CLEANING_STAGE = "Cleaning"
TEMPERATURE_MODULATION_COL = "Temperature Modulation"

SQ_TR_COL = "Sq+Tr"
SQ_TR_PERIOD_SECONDS = 100
SQ_TR_PERIOD_SAMPLES = SQ_TR_PERIOD_SECONDS / _SAMPLE_RATE
SQ_TR_PERIODS = 12


def extract_square_tr_features(data, comp, conc, plot: bool):
    features_df = pd.DataFrame(
        columns=[
            "DeltaH",
            "DeltaT1",
            "DeltaT2",
            "DeltaT3",
            "SlopeH",
            "SlopeL",
            "AreaS",
            "AreaT",
            "DeltaR",
            "Temperature Modulation",
            "Sensor",
            "Repetition",
        ]
    )
    repetitions = np.squeeze(
        np.reshape(
            [np.arange(0, SQ_TR_PERIODS, 1) for x in range(len(_SENSOR_LABELS))],
            (SQ_TR_PERIODS * len(_SENSOR_LABELS), 1),
        )
    )

    sensors = np.squeeze(
        np.reshape(
            [[x] * SQ_TR_PERIODS for x in _SENSOR_LABELS],
            (SQ_TR_PERIODS * len(_SENSOR_LABELS), 1),
        )
    )

    features_df["Repetition"] = repetitions
    features_df["Sensor"] = sensors
    features_df["Temperature Modulation"] = SQ_TR_COL
    for sensor_label in _SENSOR_LABELS:
        # Convert to resistance
        res_values = 5 / data[sensor_label] * 10000 - 10000
        #res_values = 5 - data[sensor_label]
        
        # We need to find the start and end point of the real measurement phase
        meas_rec_data = res_values[data[TEMPERATURE_MODULATION_COL] == SQ_TR_COL]

        # Calculate r0 as the mean resistance over the first 25 seconds of the first repetition
        r0 = 0
        time_window = 45  # seconds
        samples_to_include = int(time_window / _SAMPLE_RATE)
        r0 = meas_rec_data.iloc[:samples_to_include].mean()
        r0 = res_values.loc[data[STAGE_COL] == CLEANING_STAGE].mean()
        meas_rec_data = meas_rec_data / r0 #baseline shift

        mu = np.mean(meas_rec_data)
        sigma = np.std(meas_rec_data)
        meas_rec_data = scipy.stats.zscore(meas_rec_data)        

        r_max_cycle1 = 0
        r_max_cycle10 = 0

        
        for sq_tr_period in range(SQ_TR_PERIODS):
            # For loop over each period
            if sq_tr_period < (SQ_TR_PERIODS - 1):
                # If we are not at the last period

                # Get the data
                period_data = meas_rec_data.iloc[
                    int(sq_tr_period * SQ_TR_PERIOD_SAMPLES) : int(
                        (sq_tr_period + 1) * SQ_TR_PERIOD_SAMPLES
                    )
                ].reset_index(drop=True)
                if plot:
                    fig, ax = plt.subplots()
                    x_values = np.arange(
                        int(sq_tr_period * SQ_TR_PERIOD_SAMPLES),
                        int((sq_tr_period + 1) * SQ_TR_PERIOD_SAMPLES),
                    )
                    x_values = np.linspace(0, 100, 1000)
                    ax2 = ax.twinx()
                    line1,=ax.plot(x_values, period_data, "-", label='Sensor data')
                    #ax.plot(period_data, "-")

                    square_values = 0
                    square_values = np.append(square_values, np.ones(int(SQ_TR_PERIOD_SAMPLES / 2) - 2) * 5) #-2 just to get 1000 values otherwise it has 1001 and cannot plot
                    square_values = np.append(square_values, [0])
                    square_values = np.append(
                        square_values, [0.02 * x for x in range(250)]
                    )
                    square_values = np.append(
                        square_values, [5 - 0.02 * x for x in range(250)]
                    )
                    line2,=ax2.plot(
                        x_values,
                        square_values,
                        c="orange",
                        alpha=0.7,
                        label='SqTr'
                    )
                    #ax.set_title(f'{comp} {conc} ppm - {sensor_label} #{sq_tr_period}')
                    ax.set_xlabel("Time [s]")
                    ax.set_ylabel("Normalized resistance")
                    ax2.set_ylabel("Heater voltage [V]")
                    # Combine legends from ax and ax2
                    lines = [line1, line2]
                    labels = [line.get_label() for line in lines]
                    #ax.legend(lines, labels, fontsize=8)

            if len(period_data) == 0:
                continue
            # Compute values

            # Initial resistance
            initial_resistance = period_data.iloc[0]
            # End resistance
            end_resistance = period_data.iloc[-1]

            # Max resistance during the square phase
            resistance_values = period_data.iloc[
                0 : int(len(period_data) / 2) - 50
            ]
            resistance_values_filt = scipy.signal.savgol_filter(resistance_values, 35, 2)
            # Compute the first derivative
            dy_dx = np.gradient(resistance_values_filt, _SAMPLE_RATE)  # First derivative            
            target_dy_dx = 0.7 * np.max(dy_dx) # Find 70% of the maximum dy_dx
            target_dy_dx_time = np.where(dy_dx >= target_dy_dx)[0][0]  # First point reaching 0.7 of max
            resistance_value_target_dy_dx = resistance_values[target_dy_dx_time]
            # Define the threshold for the second reference point
            threshold = 0.7 * np.max(dy_dx)  # 70% of the max slope as a threshold
            threshold_crossing_time = np.where(dy_dx[target_dy_dx_time:] < threshold)[0][0] + target_dy_dx_time
            resistance_value_threshold_dy_dx = resistance_values[threshold_crossing_time]

            #resistance_values = period_data.iloc[
            #    0 : int(len(period_data) / 2) - 2
            #]
            max_resistance_square = np.max(resistance_values)
            if sq_tr_period == 1:
                r_max_cycle1 = max_resistance_square
            elif sq_tr_period == 10:
                r_max_cycle10 = max_resistance_square
            else:
                pass
            
            max_resistance_square_time = np.argmax(resistance_values)

            if plot:
                ax.plot(0, initial_resistance, "o", c="red")
                ax.plot(
                    max_resistance_square_time* _SAMPLE_RATE, max_resistance_square, "o", c="black"
                )
                ax.plot(
                target_dy_dx_time* _SAMPLE_RATE, resistance_value_target_dy_dx, "o", c="pink"
                )
                ax.plot(
                    threshold_crossing_time* _SAMPLE_RATE, resistance_value_threshold_dy_dx, "o", c="magenta"
                )

            # Max resistance during the triangle phase
            max_resistance_triangle = period_data.iloc[
                int(len(period_data) * 5.5 / 8) :
            ].max()
            # Sample of the max resistance during the triangle phase
            max_resistance_triangle_time = period_data.iloc[
                int(len(period_data) * 5.5 / 8) :
            ].argmax()

            # Minimum resistance during the first half of the triangle phase
            min_resistance_first_half_triangle = period_data.iloc[
                int(len(period_data) / 2 + 10) : int(len(period_data) * 3 / 4)
            ].min()
            # Sample of the min resistance during the first half of the triangle phase
            min_resistance_first_half_triangle_time = period_data.iloc[
                int(len(period_data) / 2 + 10) : int(len(period_data) * 3 / 4)
            ].argmin()

            # Minimum resistance during the second half of the triangle phase
            min_resistance_second_half_triangle = period_data.iloc[
                int(len(period_data) * 3 / 4) :
            ].min()
            # Sample of the min resistance during the second half of the triangle phase
            min_resistance_second_half_triangle_time = period_data.iloc[
                int(len(period_data) * 3 / 4) :
            ].argmin()

            if plot:
                ax.plot(
                    (int(len(period_data) * 5.5 / 8) + max_resistance_triangle_time)* _SAMPLE_RATE,
                    max_resistance_triangle,
                    "o",
                    c="orange",
                )
                ax.plot(
                    (int(len(period_data) / 2 + 10)
                    + min_resistance_first_half_triangle_time)* _SAMPLE_RATE,
                    min_resistance_first_half_triangle,
                    "o",
                    c="tab:green",
                )
                ax.plot(
                    (int(len(period_data) * 3 / 4)
                    + min_resistance_second_half_triangle_time)* _SAMPLE_RATE,
                    min_resistance_second_half_triangle,
                    "o",
                    c="tab:blue",
                )
                filename_cycles = _OUTPUT_DIR_SVG / f"{comp}_{conc}_ppm_{sensor_label}_{sq_tr_period}.svg"
                plt.savefig(filename_cycles, dpi=300, bbox_inches="tight")  # Save with high resolution
                filename_cycles = _OUTPUT_DIR_SVG / f"{comp}_{conc}_ppm_{sensor_label}_{sq_tr_period}.jpg"
                plt.savefig(filename_cycles, dpi=300, bbox_inches="tight")  # Save with high resolution
                plt.close(fig)
                
            # DeltH is Max resistance - Initial resistance
            delta_high = max_resistance_square - initial_resistance
            features_df.loc[
                (features_df[SENSOR_COL] == sensor_label)
                & (features_df[REPETITION_COL] == sq_tr_period),
                "DeltaH",
            ] = delta_high

            # SlopeH is the slope between of the linear region during the square phase response
            slope_high = (resistance_value_threshold_dy_dx - resistance_value_target_dy_dx) / (threshold_crossing_time - target_dy_dx_time) * _SAMPLE_RATE
            features_df.loc[
                (features_df[SENSOR_COL] == sensor_label)
                & (features_df[REPETITION_COL] == sq_tr_period),
                "SlopeH",
            ] = slope_high

            delta_t1 = max_resistance_square - min_resistance_first_half_triangle
            features_df.loc[
                (features_df[SENSOR_COL] == sensor_label)
                & (features_df[REPETITION_COL] == sq_tr_period),
                "DeltaT1",
            ] = delta_t1

            delta_t2 = (
                min_resistance_first_half_triangle - max_resistance_triangle
            )
            features_df.loc[
                (features_df[SENSOR_COL] == sensor_label)
                & (features_df[REPETITION_COL] == sq_tr_period),
                "DeltaT2",
            ] = delta_t2

            delta_t3 = max_resistance_triangle - min_resistance_second_half_triangle
            features_df.loc[
                (features_df[SENSOR_COL] == sensor_label)
                & (features_df[REPETITION_COL] == sq_tr_period),
                "DeltaT3",
            ] = delta_t3

            slope_low = (min_resistance_first_half_triangle - max_resistance_triangle) / (
                (min_resistance_first_half_triangle_time - max_resistance_square_time)
                * _SAMPLE_RATE
            )
            features_df.loc[
                (features_df[SENSOR_COL] == sensor_label)
                & (features_df[REPETITION_COL] == sq_tr_period),
                "SlopeL",
            ] = slope_low

            area_high = scipy.integrate.simpson(
                y=period_data.iloc[0 : int(len(period_data) / 2) - 10]
                - initial_resistance,
                x=np.arange(0, int(len(period_data) / 2 - 10)),
                # even="avg",
            )
            try:
                area_low = scipy.integrate.simpson(
                    y=period_data.iloc[int(len(period_data) / 2) + 10 :]
                    - end_resistance,
                    x=np.arange(0, int(len(period_data) / 2 - 10)),
                    # even="avg",
                )
                features_df.loc[
                    (features_df.Sensor == sensor_label)
                    & (features_df.Repetition == sq_tr_period),
                    "AreaT",
                ] = area_low
            except:
                print(len(period_data.iloc[int(len(period_data) / 2) :]))
                print(len(np.arange(0, int(len(period_data) / 2))))
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == sq_tr_period),
                "AreaS",
            ] = area_high
        features_df.loc[
            (features_df.Sensor == sensor_label),
            "DeltaR",
        ] = (r_max_cycle10 - r_max_cycle1)
        
        if plot:
            x_values = np.linspace(0, 5*SQ_TR_PERIOD_SECONDS, int(5*SQ_TR_PERIOD_SECONDS/_SAMPLE_RATE))
            plt.figure()
            plt.plot(x_values, meas_rec_data[int(SQ_TR_PERIOD_SECONDS/_SAMPLE_RATE):6*int(SQ_TR_PERIOD_SECONDS/_SAMPLE_RATE)])
            #plt.title(f'{comp} {conc} ppm - {sensor_label}')
            plt.xlabel("Time [s]")
            plt.ylabel("Normalized resistance")
            #filename = _OUTPUT_DIR_SVG / f"{comp}_{conc}_ppm_{sensor_label}.svg"
            #plt.savefig(filename, dpi=300, bbox_inches="tight")  # Save with high resolution
            filename = _OUTPUT_DIR_SVG / f"{comp}_{conc}_ppm_{sensor_label}.jpg"
            plt.savefig(filename, dpi=300, bbox_inches="tight")  # Save with high resolution
            plt.close()
    return features_df


@click.command()
@click.option("--data-folder", default=None)
@click.option("--plot/--no-plot", "-p", is_flag=True, default=False)
def extract_features(data_folder: Optional[Path], plot: bool):
    if data_folder is None:
        data_folder = _BASE_FOLDER
    else:
        data_folder = Path(data_folder)
        if not data_folder.exists():
            raise FileNotFoundError(f"Could not find folder {data_folder}")
    logger.debug(f"Retrieving data from {data_folder}")
    complete_features_df = pd.DataFrame(columns=["Compound", "Concentration"])
    for folder in data_folder.iterdir():
        compound = folder.name.split("_")[0]
        conc = folder.name.split("_")[1][:-3]
        # For each concentration
        folder = data_folder / f"{compound}_{conc}ppm"
        if folder.exists():
            # If the folder exists
            for csv_file in folder.iterdir():
                if csv_file.is_file() and "csv" in csv_file.name:
                    # If we have a CSV file
                    tmp_data = pd.read_csv(csv_file, header=6)
                    tmp_data["Seconds"] = [
                        x * _SAMPLE_RATE for x in range(len(tmp_data))
                    ]
                    # Get temperature modulation patterns
                    temperature_modulation_patterns = tmp_data[
                        "Temperature Modulation"
                    ].unique()

                    if "Sq+Tr" in temperature_modulation_patterns:
                        sq_tr_features = extract_square_tr_features(tmp_data, compound, conc, plot=plot)
                        sq_tr_features["Compound"] = compound
                        sq_tr_features["Concentration"] = conc
                        complete_features_df = pd.concat(
                            [complete_features_df, sq_tr_features]
                        ).reset_index(drop=True)
    output_file_path = _OUTPUT_DIR / "single_compounds_features.csv"
    logger.debug(f"Saving data to {output_file_path}")
    complete_features_df.to_csv(output_file_path)


if __name__ == "__main__":
    extract_features()
