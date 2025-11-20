"""
Code for interpolation of hourly meteodata mainly from ERA5
on a chosen timeseries range
Author: Vaclav Steinbach
Date: 15.08.2025
Dissertation Work
"""
import numpy as np
from datetime import datetime 
import os

# In/Out folder
data_fol = "out/"
out_fol = "out/"
os.makedirs(out_fol, exist_ok=True)

# Array of filenames
filenames = ["temp",
             "rh",
             "clouds",
             "wind"] 
headers = ["temperature 2m [˚C]",
          "relative humidity 2m [%/100]",
           "total cloud cover [-]",
          "windspeed 10m [m/s]"]

# define campaign
start_date = datetime(2024, 9, 8, 00, 00)
end_date = datetime(2024, 9, 30, 00, 00)

# set time step
time_step = 600 # seconds
             
for i in range(len(filenames)): 
    # Load the data 
    data = np.loadtxt(data_fol+filenames[i]+".in", comments="#")

    # Separate columns
    time = data[:, 0]
    meteo_var = data[:, 1]

    # Create new time array with arbitrary time step
    new_time = np.arange(time[0], time[-1]+time_step, time_step) 

    # Interpolate
    meteo_var_interp = np.interp(new_time, time, meteo_var)

    full_header = (
        f"campaign: {start_date} {end_date}\n"
        f"time[s] {headers[i]}"
    )

    # Save to new file
    np.savetxt(
        out_fol+filenames[i]+"_interp.in",
        np.column_stack([new_time, meteo_var_interp]),
        fmt="%.0f %.10f",
        header=full_header,
        comments="# "
    )

    print(f"Interpolation done: {filenames[i]}_interp.in created")

                 
