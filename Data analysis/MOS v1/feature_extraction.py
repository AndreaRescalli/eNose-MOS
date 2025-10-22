"""
This script extract all the features from the data collected with MOS Sensors.
The following compounds and concentrations (ppm) were tested:
- Butanone
    - 75
    - 131
    - 300
- CH4
    - 75
    - 130
    - 300
All the files are loaded, and the features and extracted. The output of this script
is a csv file with the following columns:

Repetition | Delta | Slope | AUC | Ratio | Compound | Concentration | Temperature Modulation | Sensor |

Where:
- Repetition refers to the single temperature modulation cycle (number of times the there is a full cycle of TM)
- Delta: feature extracted as the difference between maximum and minimum voltage
- Slope: feature extracted as the slope of the linear curve from the maximum/minimum to maximum/minimum
- AUC: area under the curve
- Ratio: Ratio between maximum and minimum resistance
- Compound: the compound under analysis
- Concentration: the concentration of the compound
- Temperature Modulation: the applied temperature modulation pattern
- Sensor: the sensor from which the feature was extracted
"""

import pandas as pd
import os
from pathlib import Path
from loguru import logger
import matplotlib.pyplot as plt
import scipy.integrate
import numpy as np

_COMPOUNDS = ["BUT", "CH4", "CO2"]
_CONCENTRATIONS = ["75", "131", "130", "303"]
# _BASE_FOLDER = Path(
#    "C:/Users/resca/OneDrive - Politecnico di Milano/_Dottorato/6 - Tesisti/2021_2022_Tasso/_Data/_Trial-002"
# )
_BASE_FOLDER = Path("E:\My Drive\_Papers\_2023_Chemosensors\_Data\Trial_001")

_SAMPLE_RATE = 0.1
_SENSOR_LABELS = ["S-1", "S-2", "S-3", "S-4", "S-5", "S-6", "S-7", "S-8"]
_CLEANING_STAGE_COL = "Cleaning"
_TEMPERATURE_MODULATION_COL = "Temperature Modulation"

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

'''
def extract_ramp_feature(data, plot=True):
    """Extract features from ramp pattern.

    This function extracts Delta, Slope, area and TimeToThreshold features from data collected
    with sensors exposed to the ramp pattern.


    Parameters
    ----------
    data : pd.DataFrame
        DataFrame with raw data.
    plot : bool, optional
        Plot graphs, by default True

    Returns
    -------
    pd.DataFrame
        DataFrame with the extracted features
    """
    features_df = pd.DataFrame(
        columns=[
            "Delta",
            "Slope",
            "TimeToThreshold",
            "Temperature Modulation",
            "Sensor",
            "Repetition",
        ]
    )
    repetitions = np.squeeze(
        np.reshape(
            [np.arange(0, _RAMP_PERIODS, 1) for x in range(len(_SENSOR_LABELS))],
            (_RAMP_PERIODS * len(_SENSOR_LABELS), 1),
        )
    )

    sensors = np.squeeze(
        np.reshape(
            [[x] * _RAMP_PERIODS for x in _SENSOR_LABELS],
            (_RAMP_PERIODS * len(_SENSOR_LABELS), 1),
        )
    )

    features_df.Repetition = repetitions
    features_df.Sensor = sensors
    features_df["Temperature Modulation"] = _RAMP_COL

    for sensor_label in _SENSOR_LABELS:
        # Convert to resistance
        res_values = (5 / data[sensor_label]) * 10000 - 10000
        # Get baseline voltage during cleaning
        r0 = res_values.loc[data.Stage == _CLEANING_STAGE_COL].mean()
        # We need to find the start and end point of the real measurement phase
        meas_rec_data = res_values.loc[data[_TEMPERATURE_MODULATION_COL] == _RAMP_COL,]
        for ramp_period in range(_RAMP_PERIODS):
            if ramp_period < (_RAMP_PERIODS - 1):
                period_data = meas_rec_data.iloc[
                    int(ramp_period * _RAMP_PERIOD_SAMPLES) : int(
                        (ramp_period + 1) * _RAMP_PERIOD_SAMPLES
                    )
                ].reset_index(drop=True)
                if plot:
                    plt.figure()
                    x_values = np.arange(
                        int(ramp_period * _RAMP_PERIOD_SAMPLES),
                        int((ramp_period + 1) * _RAMP_PERIOD_SAMPLES),
                    )
                    plt.plot(x_values, period_data, "-")
            else:
                period_data = meas_rec_data.iloc[
                    int(ramp_period * _RAMP_PERIOD_SAMPLES) :
                ].reset_index(drop=True)
                if plot:
                    plt.figure()
                    x_values = np.arange(
                        int(ramp_period * _RAMP_PERIOD_SAMPLES),
                        ramp_period * _RAMP_PERIOD_SAMPLES + len(period_data),
                    )
                    plt.plot(x_values, period_data, "-")
            # Compute values -> max to be found in second half, min to be found in first half
            initial_resistance = period_data.iloc[0]
            max_resistance_heating_on = period_data.iloc[
                int(len(period_data) / 2) : int(len(period_data))
            ].max()
            max_resistance_heating_on_time = period_data.iloc[
                int(len(period_data) / 2) : int(len(period_data))
            ].argmax()
            min_resistance_heating_off = period_data.iloc[
                0 : int(len(period_data) / 2)
            ].min()
            min_resistance_heating_off_time = period_data.iloc[
                0 : int(len(period_data) / 2)
            ].argmin()

            # Compute and save features
            delta = max_resistance_heating_on - min_resistance_heating_off
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == ramp_period),
                "Delta",
            ] = delta

            slope = delta / (max_resistance_heating_on_time * _SAMPLE_RATE)

            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == ramp_period),
                "Delta",
            ] = delta
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == ramp_period),
                "Slope",
            ] = slope

            # time needed to reach 75% of delta
            time_to_threshold = 0
            for index, res_value in enumerate(
                period_data.iloc[int(len(period_data) / 4) :]
            ):
                if res_value >= 75 / 100 * delta:
                    time_to_threshold = index * _SAMPLE_RATE  # in seconds
                    break
                else:
                    time_to_threshold = -1

            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == ramp_period),
                "TimeToThreshold",
            ] = time_to_threshold

        if plot:
            plt.figure()
            plt.plot(res_values[data[_TEMPERATURE_MODULATION_COL] == _RAMP_COL])
            plt.show()
    return features_df
'''


def extract_square_feature(data, plot=True):
    """Extract features from square pattern.

    This function extracts Delta and Slope features from data collected
    with sensors exposed to the square pattern.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame with raw data.
    plot : bool, optional
        Plot graphs, by default True

    Returns
    -------
    pd.DataFrame
        DataFrame with the extracted features
    """
    features_df = pd.DataFrame(
        columns=[
            "DeltaH",
            "DeltaL",
            "SlopeH",
            "SlopeL",
            "Temperature Modulation",
            "Sensor",
            "Repetition",
        ]
    )
    repetitions = np.squeeze(
        np.reshape(
            [np.arange(0, _SQUARE_PERIODS, 1) for x in range(len(_SENSOR_LABELS))],
            (_SQUARE_PERIODS * len(_SENSOR_LABELS), 1),
        )
    )

    sensors = np.squeeze(
        np.reshape(
            [[x] * _SQUARE_PERIODS for x in _SENSOR_LABELS],
            (_SQUARE_PERIODS * len(_SENSOR_LABELS), 1),
        )
    )

    features_df.Repetition = repetitions
    features_df.Sensor = sensors
    features_df["Temperature Modulation"] = _SQUARE_COL

    for sensor_label in _SENSOR_LABELS:
        # Convert to resistance
        res_values = (5 / data[sensor_label]) * 10000 - 10000
        # Get baseline voltage during cleaning
        r0 = res_values.loc[data.Stage == _CLEANING_STAGE_COL].mean()
        # We need to find the start and end point of the real measurement phase
        meas_rec_data = res_values.loc[
            data[_TEMPERATURE_MODULATION_COL] == _SQUARE_COL,
        ]
        for square_period in range(_SQUARE_PERIODS):
            if square_period < (_SQUARE_PERIODS - 1):
                period_data = meas_rec_data.iloc[
                    int(square_period * _SQUARE_PERIOD_SAMPLES) : int(
                        (square_period + 1) * _SQUARE_PERIOD_SAMPLES
                    )
                ].reset_index(drop=True)
                if plot:
                    plt.figure()
                    x_values = np.arange(
                        int(square_period * _SQUARE_PERIOD_SAMPLES),
                        int((square_period + 1) * _SQUARE_PERIOD_SAMPLES),
                    )
                    plt.plot(x_values, period_data, "-")
            """
            else:
                period_data = meas_rec_data.iloc[
                    int(square_period * _SQUARE_PERIOD_SAMPLES) :
                ].reset_index(drop=True)
                if plot:
                    plt.figure()
                    x_values = np.arange(
                        int(square_period * _SQUARE_PERIOD_SAMPLES),
                        square_period * _SQUARE_PERIOD_SAMPLES + len(period_data),
                    )
                    plt.plot(x_values, period_data, "-")
            """
            if len(period_data) == 0:
                continue
            # Compute values
            initial_resistance = period_data.iloc[0]
            max_resistance_heating_on = period_data.iloc[
                0 : int(len(period_data) / 2)
            ].max()
            max_resistance_heating_on_time = period_data.iloc[
                0 : int(len(period_data) / 2)
            ].argmax()
            min_resistance_heating_off = period_data.iloc[
                int(len(period_data) / 2) :
            ].min()
            min_resistance_heating_off_time = period_data.iloc[
                int(len(period_data) / 2) :
            ].argmin()

            # Compute and save features
            delta_high = max_resistance_heating_on - initial_resistance
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == square_period),
                "DeltaH",
            ] = delta_high

            slope_high = delta_high / (max_resistance_heating_on_time * _SAMPLE_RATE)

            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == square_period),
                "DeltaH",
            ] = delta_high
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == square_period),
                "SlopeH",
            ] = slope_high

            delta_low = max_resistance_heating_on - min_resistance_heating_off
            slope_low = delta_low / (
                (min_resistance_heating_off_time - len(period_data) / 2) * _SAMPLE_RATE
            )
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == square_period),
                "DeltaL",
            ] = delta_low
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == square_period),
                "SlopeL",
            ] = slope_low

        if plot:
            plt.figure()
            plt.plot(res_values[data[_TEMPERATURE_MODULATION_COL] == _SQUARE_COL])
            plt.show()
    return features_df


def extract_sine_features(data, plot=False):
    features_df = pd.DataFrame(
        columns=[
            "DeltaH",
            "DeltaL",
            "SlopeH",
            "SlopeL",
            "AreaH",
            "AreaL",
            "Temperature Modulation",
            "Sensor",
            "Repetition",
        ]
    )
    repetitions = np.squeeze(
        np.reshape(
            [np.arange(0, _SINE_PERIODS, 1) for x in range(len(_SENSOR_LABELS))],
            (_SINE_PERIODS * len(_SENSOR_LABELS), 1),
        )
    )

    sensors = np.squeeze(
        np.reshape(
            [[x] * _SINE_PERIODS for x in _SENSOR_LABELS],
            (_SINE_PERIODS * len(_SENSOR_LABELS), 1),
        )
    )

    features_df.Repetition = repetitions
    features_df.Sensor = sensors
    features_df["Temperature Modulation"] = _SINE_COL
    for sensor_label in _SENSOR_LABELS:
        # Convert to resistance
        res_values = 5 / data[sensor_label] * 10000 - 10000
        # Get baseline voltage during cleaning
        r0 = res_values.loc[data.Stage == _CLEANING_STAGE_COL].mean()
        # We need to find the start and end point of the real measurement phase
        meas_rec_data = res_values[data[_TEMPERATURE_MODULATION_COL] == _SINE_COL]
        for sine_period in range(_SINE_PERIODS):
            if sine_period < (_SINE_PERIODS - 1):
                period_data = meas_rec_data.iloc[
                    int(sine_period * _SINE_PERIOD_SAMPLES) : int(
                        (sine_period + 1) * _SINE_PERIOD_SAMPLES
                    )
                ].reset_index(drop=True)
                if plot:
                    fig, ax = plt.subplots()
                    x_values = np.arange(
                        int(sine_period * _SINE_PERIOD_SAMPLES),
                        int((sine_period + 1) * _SINE_PERIOD_SAMPLES),
                    )
                    ax2 = ax.twinx()
                    ax.plot(x_values, period_data, "-")

                    sin_values = (
                        np.sin(np.arange(0, 2 * np.pi, (2 * np.pi) / 500)) * 2.5
                    ) + 2.5
                    ax2.plot(x_values, sin_values, c="orange")
                    plt.title(sensor_label)
            """
            else:
                period_data = meas_rec_data.iloc[
                    int(sine_period * _SINE_PERIOD_SAMPLES) :
                ].reset_index(drop=True)
                if plot:
                    plt.figure()
                    x_values = np.arange(
                        int(sine_period * _SINE_PERIOD_SAMPLES),
                        sine_period * _SINE_PERIOD_SAMPLES + len(period_data),
                    )
                    plt.plot(x_values, period_data, "-")
                    plt.title(sensor_label)
            """
            if len(period_data) == 0:
                continue
            # Compute values
            initial_resistance = period_data.iloc[0]
            end_resistance = period_data.iloc[-1]
            max_resistance_heating_on = period_data.iloc[
                0 : int(len(period_data) / 2)
            ].max()
            max_resistance_heating_on_time = period_data.iloc[
                0 : int(len(period_data) / 2)
            ].argmax()
            min_resistance_heating_off = period_data.iloc[
                int(len(period_data) / 2) :
            ].min()
            min_resistance_heating_off_time = period_data.iloc[
                int(len(period_data) / 2) :
            ].argmin()

            # Compute and save features
            delta_high = max_resistance_heating_on - initial_resistance
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == sine_period),
                "DeltaH",
            ] = delta_high

            slope_high = delta_high / (max_resistance_heating_on_time * _SAMPLE_RATE)

            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == sine_period),
                "DeltaH",
            ] = delta_high
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == sine_period),
                "SlopeH",
            ] = slope_high

            delta_low = max_resistance_heating_on - min_resistance_heating_off
            slope_low = delta_low / (
                (min_resistance_heating_off_time - len(period_data) / 2) * _SAMPLE_RATE
            )
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == sine_period),
                "DeltaL",
            ] = delta_low
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == sine_period),
                "SlopeL",
            ] = slope_low

            area_high = scipy.integrate.simpson(
                period_data.iloc[0 : int(len(period_data) / 2)] - initial_resistance,
                np.arange(0, int(len(period_data) / 2)),
                even="avg",
            )

            try:
                area_low = scipy.integrate.simpson(
                    period_data.iloc[int(len(period_data) / 2) :] - end_resistance,
                    np.arange(0, int(len(period_data) / 2)),
                    even="avg",
                )
                features_df.loc[
                    (features_df.Sensor == sensor_label)
                    & (features_df.Repetition == sine_period),
                    "AreaL",
                ] = area_low
            except:
                print(sensor_label)
                print(sine_period)
                print(len(period_data.iloc[int(len(period_data) / 2) :]))
                print(len(np.arange(0, int(len(period_data) / 2))))
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == sine_period),
                "AreaH",
            ] = area_high
        if plot:
            plt.figure()
            plt.plot(meas_rec_data)
            plt.show()
    return features_df


def extract_triangle_features(data, plot=True):
    """Extract features from raw data when triangle pattern is applied.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame with raw data.
    plot : bool, optional
        Plot raw data, by default True

    Returns
    -------
    _type_
        _description_
    """
    features_df = pd.DataFrame(
        columns=[
            "DeltaH",
            "DeltaL",
            "SlopeH",
            "SlopeL",
            "AreaH",
            "AreaL",
            "Temperature Modulation",
            "Sensor",
            "Repetition",
        ]
    )
    repetitions = np.squeeze(
        np.reshape(
            [np.arange(0, _TRIANGLE_PERIODS, 1) for x in range(len(_SENSOR_LABELS))],
            (_TRIANGLE_PERIODS * len(_SENSOR_LABELS), 1),
        )
    )

    sensors = np.squeeze(
        np.reshape(
            [[x] * _TRIANGLE_PERIODS for x in _SENSOR_LABELS],
            (_TRIANGLE_PERIODS * len(_SENSOR_LABELS), 1),
        )
    )

    features_df.Repetition = repetitions
    features_df.Sensor = sensors
    features_df["Temperature Modulation"] = _TRIANGLE_COL
    for sensor_label in _SENSOR_LABELS:
        # Convert to resistance
        res_values = 5 / data[sensor_label] * 10000 - 10000
        # Get baseline voltage during cleaning
        r0 = res_values.loc[data.Stage == _CLEANING_STAGE_COL].mean()
        # We need to find the start and end point of the real measurement phase
        meas_rec_data = res_values[data[_TEMPERATURE_MODULATION_COL] == _TRIANGLE_COL]
        for triangle_period in range(_TRIANGLE_PERIODS):
            if triangle_period < (_TRIANGLE_PERIODS - 1):
                period_data = meas_rec_data.iloc[
                    int(triangle_period * _TRIANGLE_PERIOD_SAMPLES) : int(
                        (triangle_period + 1) * _TRIANGLE_PERIOD_SAMPLES
                    )
                ].reset_index(drop=True)
                if plot:
                    fig, ax = plt.subplots()
                    x_values = np.arange(
                        int(triangle_period * _TRIANGLE_PERIOD_SAMPLES),
                        int((triangle_period + 1) * _TRIANGLE_PERIOD_SAMPLES),
                    )
                    ax2 = ax.twinx()
                    ax.plot(x_values, period_data, "-")

                    triangle_values = [0.01 * x for x in range(500)]
                    triangle_values = np.append(
                        triangle_values, [5 - 0.01 * x for x in range(500)]
                    )
                    ax2.plot(
                        x_values,
                        triangle_values,
                        c="orange",
                    )
                    plt.title(sensor_label)
                    plt.show()
            """
            else:
                period_data = meas_rec_data.iloc[
                    int(triangle_period * _TRIANGLE_PERIOD_SAMPLES) :
                ].reset_index(drop=True)
                if plot:
                    plt.figure()
                    x_values = np.arange(
                        int(triangle_period * _TRIANGLE_PERIOD_SAMPLES),
                        triangle_period * _TRIANGLE_PERIOD_SAMPLES + len(period_data),
                    )
                    plt.plot(x_values, period_data, "-")
                    plt.title(sensor_label)
            """
            if len(period_data) == 0:
                continue
            # Compute values
            initial_resistance = period_data.iloc[0]
            end_resistance = period_data.iloc[-1]

            max_resistance_heating_on = period_data.max()
            max_resistance_heating_on_time = period_data.argmax()

            min_resistance_heating_off = period_data.iloc[
                int(len(period_data) / 2) :
            ].min()
            min_resistance_heating_off_time = period_data.iloc[
                int(len(period_data) / 2) :
            ].argmin()

            # Compute and save features
            delta_high = max_resistance_heating_on - initial_resistance
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == triangle_period),
                "DeltaH",
            ] = delta_high

            slope_high = delta_high / (max_resistance_heating_on_time * _SAMPLE_RATE)

            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == triangle_period),
                "DeltaH",
            ] = delta_high
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == triangle_period),
                "SlopeH",
            ] = slope_high

            delta_low = max_resistance_heating_on - min_resistance_heating_off
            slope_low = delta_low / (
                (min_resistance_heating_off_time - len(period_data) / 2) * _SAMPLE_RATE
            )
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == triangle_period),
                "DeltaL",
            ] = delta_low
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == triangle_period),
                "SlopeL",
            ] = slope_low

            try:
                area_low = scipy.integrate.simpson(
                    period_data.iloc[max_resistance_heating_on_time:] - end_resistance,
                    np.arange(
                        0,
                        len(period_data[max_resistance_heating_on_time:]),
                    ),
                    even="avg",
                )
                features_df.loc[
                    (features_df.Sensor == sensor_label)
                    & (features_df.Repetition == triangle_period),
                    "AreaL",
                ] = area_low
            except:
                continue

            try:
                area_high = scipy.integrate.simpson(
                    period_data.iloc[0:max_resistance_heating_on_time]
                    - initial_resistance,
                    np.arange(0, max_resistance_heating_on_time),
                    even="avg",
                )
                features_df.loc[
                    (features_df.Sensor == sensor_label)
                    & (features_df.Repetition == triangle_period),
                    "AreaH",
                ] = area_high
            except:
                continue
            if plot:
                plt.figure()
                plt.plot(meas_rec_data)
                plt.show()
    return features_df


def extract_square_tr_features(data, plot=False):
    features_df = pd.DataFrame(
        columns=[
            "DeltaH",
            "DeltaL",
            "SlopeH",
            "SlopeL",
            "AreaH",
            "AreaL",
            "Temperature Modulation",
            "Sensor",
            "Repetition",
        ]
    )
    repetitions = np.squeeze(
        np.reshape(
            [np.arange(0, _SQ_TR_PERIODS, 1) for x in range(len(_SENSOR_LABELS))],
            (_SQ_TR_PERIODS * len(_SENSOR_LABELS), 1),
        )
    )

    sensors = np.squeeze(
        np.reshape(
            [[x] * _SQ_TR_PERIODS for x in _SENSOR_LABELS],
            (_SQ_TR_PERIODS * len(_SENSOR_LABELS), 1),
        )
    )

    features_df.Repetition = repetitions
    features_df.Sensor = sensors
    features_df["Temperature Modulation"] = _SQ_TR_COL
    for sensor_label in _SENSOR_LABELS:
        # Convert to resistance
        res_values = 5 / data[sensor_label] * 10000 - 10000
        # Get baseline voltage during cleaning
        r0 = res_values.loc[data.Stage == _CLEANING_STAGE_COL].mean()
        # We need to find the start and end point of the real measurement phase
        meas_rec_data = res_values[data[_TEMPERATURE_MODULATION_COL] == _SQ_TR_COL]
        for sq_tr_period in range(_SQ_TR_PERIODS):
            if sq_tr_period < (_SINE_PERIODS - 1):
                period_data = meas_rec_data.iloc[
                    int(sq_tr_period * _SQ_TR_PERIOD_SAMPLES) : int(
                        (sq_tr_period + 1) * _SQ_TR_PERIOD_SAMPLES
                    )
                ].reset_index(drop=True)
                if plot:
                    fig, ax = plt.subplots()
                    x_values = np.arange(
                        int(sq_tr_period * _SQ_TR_PERIOD_SAMPLES),
                        int((sq_tr_period + 1) * _SQ_TR_PERIOD_SAMPLES),
                    )
                    ax2 = ax.twinx()
                    ax.plot(x_values, period_data, "-")

                    square_values = np.ones(int(_SQ_TR_PERIOD_SAMPLES / 2) - 1) * 5
                    square_values = np.append(square_values, [0])
                    square_values = np.append(
                        square_values, [0.02 * x for x in range(250)]
                    )
                    square_values = np.append(
                        square_values, [5 - 0.02 * x for x in range(250)]
                    )
                    ax2.plot(
                        x_values,
                        square_values,
                        c="orange",
                    )
                    plt.title(sensor_label)
            """
            else:
                period_data = meas_rec_data.iloc[
                    int(sq_tr_period * _SQ_TR_PERIOD_SAMPLES) :
                ].reset_index(drop=True)
                if plot:
                    plt.figure()
                    x_values = np.arange(
                        int(sq_tr_period * _SQ_TR_PERIOD_SAMPLES),
                        sq_tr_period * _SQ_TR_PERIOD_SAMPLES + len(period_data),
                    )
                    plt.plot(x_values, period_data, "-")
                    plt.title(sensor_label)
            """
            if len(period_data) == 0:
                continue
            print(period_data.shape)
            # Compute values
            initial_resistance = period_data.iloc[0]
            end_resistance = period_data.iloc[-1]
            max_resistance_heating_on = period_data.iloc[
                0 : int(len(period_data) / 2)
            ].max()
            max_resistance_heating_on_time = period_data.iloc[
                0 : int(len(period_data) / 2)
            ].argmax()
            max_resistance_heating_off = period_data.iloc[
                int(len(period_data) / 2) :
            ].max()
            max_resistance_heating_off_time = period_data.iloc[
                int(len(period_data) / 2) :
            ].argmax()
            min_resistance_heating_off = period_data.iloc[
                int(len(period_data) / 2) :
            ].min()
            min_resistance_heating_off_time = period_data.iloc[
                int(len(period_data) / 2) :
            ].argmin()

            # Compute and save features
            delta_high = max_resistance_heating_on - initial_resistance
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == sq_tr_period),
                "DeltaH",
            ] = delta_high

            slope_high = delta_high / (max_resistance_heating_on_time * _SAMPLE_RATE)

            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == sq_tr_period),
                "DeltaH",
            ] = delta_high
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == sq_tr_period),
                "SlopeH",
            ] = slope_high

            delta_low = max_resistance_heating_off - min_resistance_heating_off
            slope_low = delta_low / (
                (max_resistance_heating_off_time - min_resistance_heating_off_time) * _SAMPLE_RATE
            )
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == sq_tr_period),
                "DeltaL",
            ] = delta_low
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == sq_tr_period),
                "SlopeL",
            ] = slope_low

            area_high = scipy.integrate.simpson(
                period_data.iloc[0 : int(len(period_data) / 2)] - initial_resistance,
                np.arange(0, int(len(period_data) / 2)),
                even="avg",
            )
            try:
                area_low = scipy.integrate.simpson(
                    period_data.iloc[int(len(period_data) / 2) :] - end_resistance,
                    np.arange(0, int(len(period_data) / 2)),
                    even="avg",
                )
                features_df.loc[
                    (features_df.Sensor == sensor_label)
                    & (features_df.Repetition == sq_tr_period),
                    "AreaL",
                ] = area_low
            except:
                print(len(period_data.iloc[int(len(period_data) / 2) :]))
                print(len(np.arange(0, int(len(period_data) / 2))))
            features_df.loc[
                (features_df.Sensor == sensor_label)
                & (features_df.Repetition == sq_tr_period),
                "AreaH",
            ] = area_high
        if plot:
            plt.figure()
            plt.plot(meas_rec_data)
            plt.show()
    return features_df


def extract_features():
    complete_features_df = pd.DataFrame(columns=["Compound", "Concentration"])
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
                        # If we have a CSV file
                        tmp_data = pd.read_csv(csv_file, header=6)
                        tmp_data["Seconds"] = [
                            x * _SAMPLE_RATE for x in range(len(tmp_data))
                        ]
                        # Get temperature modulation patterns
                        temperature_modulation_patterns = tmp_data[
                            "Temperature Modulation"
                        ].unique()
                        """
                        if "Ramp" in temperature_modulation_patterns:
                            ramp_features = extract_ramp_feature(tmp_data, plot=False)
                            ramp_features["Compound"] = compound
                            ramp_features["Concentration"] = conc
                            complete_features_df = pd.concat(
                                [complete_features_df, ramp_features]
                            ).reset_index(drop=True)
                        """
                        if "Square" in temperature_modulation_patterns:
                            square_features = extract_square_feature(
                                tmp_data, plot=False
                            )
                            square_features["Compound"] = compound
                            square_features["Concentration"] = conc
                            complete_features_df = pd.concat(
                                [complete_features_df, square_features]
                            ).reset_index(drop=True)
                        if "Sine" in temperature_modulation_patterns:
                            sine_features = extract_sine_features(tmp_data, plot=False)
                            sine_features["Compound"] = compound
                            sine_features["Concentration"] = conc
                            complete_features_df = pd.concat(
                                [complete_features_df, sine_features]
                            ).reset_index(drop=True)
                        if "Sq+Tr" in temperature_modulation_patterns:
                            sq_tr_features = extract_square_tr_features(
                                tmp_data, plot=False
                            )
                            sq_tr_features["Compound"] = compound
                            sq_tr_features["Concentration"] = conc
                            complete_features_df = pd.concat(
                                [complete_features_df, sq_tr_features]
                            ).reset_index(drop=True)
                        if "Triangle" in temperature_modulation_patterns:
                            triangle_features = extract_triangle_features(
                                tmp_data, plot=False
                            )
                            triangle_features["Compound"] = compound
                            triangle_features["Concentration"] = conc
                            complete_features_df = pd.concat(
                                [complete_features_df, triangle_features]
                            ).reset_index(drop=True)
    complete_features_df.to_csv("complete_features.csv")


if __name__ == "__main__":
    extract_features()
