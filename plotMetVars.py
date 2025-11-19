"""
Script for ploting of chosen meteorological variables
Author: Vaclav Steinbach
Date: 19.11.2025
Dissertation work
"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# Parameters
start_date = datetime(2024, 9, 8, 0, 0, 0)  # replace with your start date
in_dir = Path("out")
files = ["clouds.in", "rh.in", "solar.in", "temp.in", "wind.in"]
labels = ["Cloud Cover [-]", "Relative Humidity [%]", "Solar Radiation [W/m²]", "Temperature [°C]", "Wind Speed [m/s]"]

# Create figure with 5 rows, 1 column, shared x-axis
fig, axes = plt.subplots(nrows=5, ncols=1, figsize=(12, 10), sharex=True)

for ax, file, label in zip(axes, files, labels):
    # Read file
    data = pd.read_csv(in_dir / file, sep=" ", comment="#", header=None, names=["time", "value"])
    
    # Convert seconds to datetime
    data["datetime"] = start_date + pd.to_timedelta(data["time"], unit="s")
    
    # Plot
    ax.plot(data["datetime"], data["value"], label=label)
    ax.set_ylabel(label)
    ax.grid(True)

# Common x-axis formatting
axes[-1].set_xlabel("Time")
fig.autofmt_xdate(rotation=30)
plt.tight_layout()
plt.savefig("out/metVars.png", dpi=300)
print("Figure saved!")
plt.show()

