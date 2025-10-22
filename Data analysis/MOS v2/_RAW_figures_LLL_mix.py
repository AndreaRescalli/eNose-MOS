import pandas as pd
import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from loguru import logger

# Constants
_BASE_FOLDER = Path(r"C:\Users\resca\OneDrive - Politecnico di Milano\_Dottorato\6 - Tesisti\2024_2025_Vegetali\2_Misure sacche\sacche_merged")
_OUTPUT_DIR = Path("Outputs") / "S-4_LLL"
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
_DATA_EXPORT_DIR = _OUTPUT_DIR / "Data_Export"
_DATA_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

_SAMPLE_RATE = 0.1
_SENSOR_LABELS = ["S-4"]  # Only S-4
TEMPERATURE_MODULATION_COL = "Temperature Modulation"
SQ_TR_COL = "Sq+Tr"
SQ_TR_PERIOD_SECONDS = 100
SQ_TR_PERIOD_SAMPLES = int(SQ_TR_PERIOD_SECONDS / _SAMPLE_RATE)
SQ_TR_PERIOD_START_IDX = SQ_TR_PERIOD_SAMPLES
SQ_TR_PERIOD_END_IDX = 2 * SQ_TR_PERIOD_SAMPLES

# Function to plot data
def plot_ace_subplots(data_folder: Path):
    folder = data_folder / "53_43_112"
    if not folder.exists():
        raise FileNotFoundError(f"Could not find folder for LLL at {folder}")
    
    fig, ax = plt.subplots(figsize=(6, 5))  # Only one axis for S-4
    
    export_data = pd.DataFrame(columns=["Time [s]", "Voltage", "Concentration"])         
          
    # If folder exists, check each CSV file
    for csv_file in folder.iterdir():
        if csv_file.is_file() and "csv" in csv_file.name:
            
            tmp_data = pd.read_csv(csv_file, header=6)
            tmp_data["Seconds"] = [x * _SAMPLE_RATE for x in range(len(tmp_data))]
            
            if SQ_TR_COL in tmp_data[TEMPERATURE_MODULATION_COL].unique():
                # Extract data for the second Sq+Tr period
                volt_values = 5 - tmp_data["S-4"]  # Focusing only on S-4 sensor
                meas_volt_data = volt_values[tmp_data[TEMPERATURE_MODULATION_COL] == SQ_TR_COL]
                meas_volt_data_period = meas_volt_data[SQ_TR_PERIOD_START_IDX:SQ_TR_PERIOD_END_IDX]
                
                # Time values
                time_values = np.linspace(
                    0, SQ_TR_PERIOD_SECONDS, len(meas_volt_data_period)
                )
                
                # Plot the data for each compound with corresponding concentration label
                ax.plot(time_values, meas_volt_data_period)
                
                # Prepare data for export
                sensor_export_data = pd.DataFrame({
                    "Time [s]": time_values,
                    "Voltage": meas_volt_data_period.values,
                    "Concentration": "LLL",
                })
                export_data = pd.concat([export_data, sensor_export_data], ignore_index=True)

        if not export_data.empty:
            export_file_path = _DATA_EXPORT_DIR / f"S-4_LLL.csv"
            export_data[["Time [s]", "Voltage"]].copy().to_csv(export_file_path, index=False, header=False)
            logger.info(f"Data for LLL exported to {export_file_path}")
    
    # Finalize subplot
    ax.set_title("Sensor: S-4")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Voltage [V]")
    
    # Finalize figure
    plt.tight_layout()
    output_file_path = _OUTPUT_DIR / "S-4_Subplot_L_Only.png"
    plt.savefig(output_file_path, dpi=300, bbox_inches="tight")
    plt.show()
    logger.info(f"Plot saved at {output_file_path}")


# Run the function
if __name__ == "__main__":
    plot_ace_subplots(_BASE_FOLDER)
