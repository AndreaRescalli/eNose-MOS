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
_SENSOR_LABELS = ["S-3"]
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
            if sq_tr_period == 1:
                # Initialize CSV data
                marker_points = []

                # Get the data
                period_data = meas_rec_data.iloc[
                    int(sq_tr_period * SQ_TR_PERIOD_SAMPLES) : int(
                        (sq_tr_period + 1) * SQ_TR_PERIOD_SAMPLES
                    )
                ].reset_index(drop=True)

                # Generate the square-triangle pattern waveform
                square_values = [0]
                square_values = np.append(square_values, np.ones(int(SQ_TR_PERIOD_SAMPLES / 2) - 2) * 5)
                square_values = np.append(square_values, [0])
                square_values = np.append(square_values, [0.02 * x for x in range(250)])
                square_values = np.append(square_values, [5 - 0.02 * x for x in range(250)])
                sample_numbers = np.arange(0, len(square_values))
                sqtr_pattern_df = pd.DataFrame({
                    'Time': sample_numbers*_SAMPLE_RATE,   # Column 1: Time
                    'Value': square_values      # Column 2: Corresponding values
                })

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

                marker_points.append([
                    0, initial_resistance,                    
                    target_dy_dx_time * _SAMPLE_RATE, resistance_value_target_dy_dx,
                    threshold_crossing_time * _SAMPLE_RATE, resistance_value_threshold_dy_dx,
                    max_resistance_square_time * _SAMPLE_RATE, max_resistance_square,                    
                    (int(len(period_data) / 2 + 10) + min_resistance_first_half_triangle_time)* _SAMPLE_RATE, min_resistance_first_half_triangle,
                    (int(len(period_data) * 5.5 / 8) + max_resistance_triangle_time)* _SAMPLE_RATE, max_resistance_triangle,
                    (int(len(period_data) * 3 / 4) + min_resistance_second_half_triangle_time)* _SAMPLE_RATE, min_resistance_second_half_triangle,
                ])

                # Save the data after all cycles for the current sensor to CSV files
                sample_numbers = np.arange(0, len(period_data.values))
                sensor_data_df = pd.DataFrame({
                    'Time': sample_numbers*_SAMPLE_RATE,   # Column 1: Time
                    'Value': period_data.values      # Column 2: Corresponding values
                })
                marker_points_df = pd.DataFrame(marker_points, columns=[
                    "Start Resistance Time", "Start Resistance",                     
                    "Target dY/dX Time", "Target dY/dX Resistance",
                    "Threshold Crossing Time", "Threshold Crossing Resistance",
                    "Max Resistance Time", "Max Resistance",
                    "Min Resistance Triangle First Half Time", "Min Resistance Triangle First Half",
                    "Max Resistance Triangle Time", "Max Resistance Triangle",
                    "Min Resistance Triangle Second Half Time", "Min Resistance Triangle Second Half",
                ])
                
                sensor_data_df.to_csv(f"sensor_data_{comp}_{conc}_{sensor_label}.csv", index=False)
                sqtr_pattern_df.to_csv(f"sqtr_pattern_{comp}_{conc}_{sensor_label}.csv", index=False)
                marker_points_df.to_csv(f"marker_points_{comp}_{conc}_{sensor_label}.csv", index=False)


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

                    if "Sq+Tr" in temperature_modulation_patterns and compound == "ACE" and conc == "173":
                        extract_square_tr_features(tmp_data, compound, conc, plot=plot)


if __name__ == "__main__":
    extract_features()
