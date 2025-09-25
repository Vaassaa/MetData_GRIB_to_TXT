"""
Script for extraction and manipulation of Wind GRIB data
Author: Vaclav Steinbach
Date: 13.06.2025
Dissertation work
"""
from eccodes import codes_grib_new_from_file, codes_release, codes_get, codes_grib_find_nearest
from datetime import datetime, timedelta
import math
import os

# GPS location of amalia
target_lat, target_lon = 50.125, 13.875 

# In/Out folder
campaign = "Amalie_2025-08-26_2025-09-07"
data_fol = "data/"+campaign+"/"
out_fol = "out/"
os.makedirs(out_fol, exist_ok=True)

"""
--- Meteoroligical variable ---
"""
varname, shortname_u, shortname_v = "wind speed 10m", "10u", "10v"
input_file = "wind.grib"
output_file = "wind.in"

"""
--- Time window ---
"""
start_date = datetime(2025, 9, 5, 00, 00)
end_date = datetime(2025, 9, 6, 12, 00)
time_step = 3600  # hrs -> seconds

# Allocation
wind_data = {}  # valid_time: {"10u": val, "10v": val}

with open(data_fol+input_file, "rb") as f:
    while True: # Loop through all messages
        gid = codes_grib_new_from_file(f)
        if gid is None: # End of loop
            break
        try:
            # Pick out the variable name
            short_name = codes_get(gid, "shortName")
            if short_name not in ["10u", "10v"]:
                continue

            date = codes_get(gid, "dataDate")      # YYYYMMDD
            time = codes_get(gid, "dataTime")      # HHMM
            step = codes_get(gid, "step")          # in hours

            base_time = datetime.strptime(f"{date:08d}{time:04d}", "%Y%m%d%H%M")
            valid_time = base_time + timedelta(hours=step)

            # Skip this message if its outside the time window
            if not (start_date <= valid_time <= end_date):
                continue

            # Average of 4 points
            nearest_points = codes_grib_find_nearest(gid, target_lat, target_lon, is_lsm=False, npoints=4)
            values = [pt['value'] for pt in nearest_points]
            avg_val = sum(values) / len(values)

            # # Nearest
            # val = codes_grib_find_nearest(gid, target_lat, target_lon)[0]['value']
            # data.append((valid_time, val))

            # Store in dict
            if valid_time not in wind_data:
                wind_data[valid_time] = {}
            wind_data[valid_time][short_name] = avg_val

            print(f"Appended data from {valid_time}")
        finally: # Frees memory
            codes_release(gid)

# Compute Euler norm of wind vector
wind_series = []
for t in sorted(wind_data.keys()):
    u = wind_data[t].get("10u")
    v = wind_data[t].get("10v")
    if u is not None and v is not None:
        wind_speed = math.sqrt(u**2 + v**2)
        wind_series.append(wind_speed)

# Construct output file
with open(out_fol+output_file, "w") as out:
    out.write(f"# time {varname}\n")
    for i, val in enumerate(wind_series):
        seconds = i * time_step
        out.write(f"{seconds} {val}\n")

print(f"Saved hourly time series to {output_file}")
