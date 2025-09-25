"""
Script for extraction and manipulation of GRIB data
Author: Vaclav Steinbach
Date: 13.06.2025
Dissertation work
"""
from eccodes import codes_grib_new_from_file, codes_release, codes_get, codes_grib_find_nearest
from datetime import datetime, timedelta
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
# varname, shortname = "precipitation", "tp"
# input_file = "precipitation_total.grib"
# output_file = "rain.in"

varname, shortname = "temperature 2m", "2t"
input_file = "temp_dewtemp.grib"
output_file = "temp.in"

# varname, shortname = "low cloud cover", "lcc"
# input_file = "clouds.grib"
# output_file = "clouds.in"

"""
--- Time window ---
"""
start_date = datetime(2025, 9, 5, 00, 00)
end_date = datetime(2025, 9, 6, 12, 00)
time_step = 3600  # hrs -> seconds

# Allocation
data = []

with open(data_fol+input_file, "rb") as f:
    while True: # Loop through all messages
        gid = codes_grib_new_from_file(f)
        if gid is None: # End of loop
            break
        try:
            # Pick out the variable name
            if codes_get(gid, "shortName") != shortname: 
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
            if shortname == "2t": 
                avg_val = avg_val - 272.15 # Kelvin to Celsius conversion for temperature
            data.append((valid_time, avg_val))

            # # Nearest
            # val = codes_grib_find_nearest(gid, target_lat, target_lon)[0]['value']
            # data.append((valid_time, val))

            print(f"Appended data from {valid_time}")
        finally: # Frees memory
            codes_release(gid)

# Sort and construct precip array 
data.sort()
precip_hourly = [val for (_, val) in data]
# If not hourly but accumulated
# precip_hourly = [round(data[0][1], 5)] + [
    # round(b - a, 5) for (_, a), (_, b) in zip(data[:-1], data[1:])
# ]

# Construct output file
with open(out_fol+output_file, "w") as out:
    out.write(f"# time {varname}\n")
    for i, val in enumerate(precip_hourly):
        seconds = i * time_step
        out.write(f"{seconds} {val}\n")

print(f"Saved hourly time series to {output_file}")
