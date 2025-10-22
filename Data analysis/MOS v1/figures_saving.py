"""
This script allows to create figures of the collected data, and to save
them in the preferred location.
Just run the script with a path as a parameter, that is the folder where
you want to save the figures. If this directory does not exist, 
the script will try to create it.
"""

from pathlib import Path
from sys import argv

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import click

_DEFAULT_DATA_DIR = Path(
    "C:/Users/resca/OneDrive - Politecnico di Milano/_Dottorato/6 - Tesisti/2021_2022_Tasso/_Data"
)

compounds = ["BUT", "CH4", "CO2"]
concentrations = ["75", "131", "130", "303"]
sensor_labels = ["S-1", "S-2", "S-3", "S-4", "S-5", "S-6", "S-7", "S-8"]


@click.command()
@click.option(
    "--data_dir", default=_DEFAULT_DATA_DIR, help="Folder containing raw data."
)
@click.option(
    "--output_dir", default="_figures", help="Folder where figures will be stored."
)
def create_figures(data_dir, output_dir):
    """Create figures of data collected with temperature modulation electronic nose."""
    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    except:
        raise

    try:
        data_dir = Path(data_dir)
    except:
        raise
    for compound in compounds:
        for conc in concentrations:
            folder = data_dir / f"{compound}_{conc}ppm"
            if folder.exists():
                print(f"{compound}-{conc}")
                for csv_file in folder.iterdir():
                    if csv_file.is_file() and "csv" in csv_file.name:
                        # Get temperature modulation from file name
                        temperature_m = csv_file.name.split("_")[-1][:-4]
                        tmp_data = pd.read_csv(csv_file, header=6)
                        tmp_data["Seconds"] = [x * 0.1 for x in range(len(tmp_data))]

                        temp_options = tmp_data["Temperature Modulation"].unique()
                        if len(temp_options) == 1:
                            temperature_m_value = temp_options[0]
                        else:
                            temperature_m_value = temp_options[1]

                        fig, ax = plt.subplots(1, 2, figsize=(12, 6))
                        for sensor_label in sensor_labels:
                            ax[0].plot(
                                tmp_data["Seconds"],
                                tmp_data[sensor_label],
                                label=sensor_label,
                            )
                        ax[0].set_title(
                            f'{compound}-{conc}-{tmp_data["Temperature Modulation"].unique()}'
                        )
                        ax[0].set_xlabel("Seconds")
                        ax[0].legend()

                        ax2 = ax[1].twinx()
                        lns1 = ax[1].plot(
                            tmp_data["Seconds"],
                            tmp_data["Temperature"],
                            label="Temperature",
                        )
                        ax[1].set_ylabel("Temperature [$^\circ$C]")
                        # secax_y = plt.secondary_yaxis('left')
                        lns2 = ax2.plot(
                            tmp_data["Seconds"],
                            tmp_data["Humidity"],
                            c="orange",
                            label="Humidity",
                        )
                        ax2.set_ylabel("Humidity [%]")
                        ax[1].set_xlabel("Seconds")
                        lns = lns1 + lns2
                        labs = [l.get_label() for l in lns]
                        ax[1].legend(lns, labs, loc=0)

                        fig.savefig(
                            output_dir / f"{compound}-{conc}-{temperature_m_value}.png"
                        )
                        plt.close()


if __name__ == "__main__":
    create_figures()
