import pandas as pd
import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from loguru import logger

# Constants
_BASE_FOLDER = Path(r"C:\Users\resca\OneDrive - Politecnico di Milano\_Dottorato\6 - Tesisti\2024_2025_Vegetali\2_Misure sacche\_Trial-101")
_OUTPUT_DIR = Path("Outputs") / "ACE_Subplots"
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
_DATA_EXPORT_DIR = _OUTPUT_DIR / "Data_Export"
_DATA_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

_SAMPLE_RATE = 0.1
_SENSOR_LABELS = ["S-2", "S-3", "S-4", "S-5"]
TEMPERATURE_MODULATION_COL = "Temperature Modulation"
SQ_TR_COL = "Sq+Tr"
SQ_TR_PERIOD_SECONDS = 100
SQ_TR_PERIOD_SAMPLES = int(SQ_TR_PERIOD_SECONDS / _SAMPLE_RATE)
SQ_TR_PERIOD_START_IDX = SQ_TR_PERIOD_SAMPLES
SQ_TR_PERIOD_END_IDX = 2 * SQ_TR_PERIOD_SAMPLES

# Concentration details
CONCENTRATIONS = [73, 173, 319]  # ppm
CONC_LABELS = ["ACE L", "ACE M", "ACE H"]
CONC_COLORS = ["green", "orange", "red"]

# Function to plot data
def plot_ace_subplots(data_folder: Path):
    ace_folder = data_folder
    if not ace_folder.exists():
        raise FileNotFoundError(f"Could not find folder for ACE compound at {ace_folder}")
    
    fig, axes = plt.subplots(1, 4, figsize=(20, 5), sharey=True)
    
    for sensor_idx, sensor_label in enumerate(_SENSOR_LABELS):
        ax = axes[sensor_idx]
        export_data = pd.DataFrame(columns=["Time [s]", "Voltage", "Concentration"])
        
        for conc, label, color in zip(CONCENTRATIONS, CONC_LABELS, CONC_COLORS):
            folder = ace_folder / f"ACE_{conc}ppm"
            if not folder.exists():
                logger.warning(f"Folder for ACE {conc}ppm does not exist. Skipping.")
                continue
            
            for csv_file in folder.iterdir():
                if csv_file.is_file() and "csv" in csv_file.name:
                    tmp_data = pd.read_csv(csv_file, header=6)
                    tmp_data["Seconds"] = [x * _SAMPLE_RATE for x in range(len(tmp_data))]
                    
                    if SQ_TR_COL in tmp_data[TEMPERATURE_MODULATION_COL].unique():
                        # Extract data for the second Sq+Tr period
                        volt_values = 5 - tmp_data[sensor_label]
                        meas_volt_data = volt_values[tmp_data[TEMPERATURE_MODULATION_COL] == SQ_TR_COL]
                        meas_volt_data_period = meas_volt_data[SQ_TR_PERIOD_START_IDX:SQ_TR_PERIOD_END_IDX]
                        
                        # Time values
                        time_values = np.linspace(
                            0, SQ_TR_PERIOD_SECONDS, len(meas_volt_data_period)
                        )
                        
                        # Plot the data
                        ax.plot(time_values, meas_volt_data_period, label=label, color=color)
                        
                        # Prepare data for export
                        sensor_export_data = pd.DataFrame({
                            "Time [s]": time_values,
                            "Voltage": meas_volt_data_period.values,
                            "Concentration": label,
                        })
                        export_data = pd.concat([export_data, sensor_export_data], ignore_index=True)
        
        # Export data for each concentration separately
        for conc_label in CONC_LABELS:
            conc_data = export_data[export_data["Concentration"] == conc_label]
            if not conc_data.empty:
                export_file_path = _DATA_EXPORT_DIR / f"ACE_{sensor_label}_{conc_label.replace(' ', '_')}.csv"
                conc_data[["Time [s]", "Voltage"]].copy().to_csv(export_file_path, index=False, header=False)
                logger.info(f"Data for {sensor_label} ({conc_label}) exported to {export_file_path}")
        
        # Finalize subplot
        ax.set_title(f"Sensor: {sensor_label}")
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("Voltage [V]")
        ax.legend(loc="upper right")
    
    # Finalize figure
    plt.tight_layout()
    output_file_path = _OUTPUT_DIR / "ACE_Subplots.png"
    plt.savefig(output_file_path, dpi=300, bbox_inches="tight")
    plt.show()
    logger.info(f"Plot saved at {output_file_path}")


# Run the function
if __name__ == "__main__":
    plot_ace_subplots(_BASE_FOLDER)