"""
Script for extraction and manipulation of relative humidity GRIB data
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
campaign = "Campaign_08-09-2024_30-09-2024"
data_fol = "data/"+campaign+"/"
out_fol = "out/"
os.makedirs(out_fol, exist_ok=True)

"""
--- Meteoroligical variable ---
"""
varname = "relative humidity [%/100]"
input_file = "temp_dewtemp.grib"
output_file = "rh.in"

"""
--- Time window ---
"""
start_date = datetime(2024, 9, 8, 00, 00)
end_date = datetime(2024, 9, 30, 00, 00)
time_step = 3600  # hrs -> seconds

# Allocation
temp_data = {}  

with open(data_fol+input_file, "rb") as f:
    while True: # Loop through all messages
        gid = codes_grib_new_from_file(f)
        if gid is None: # End of loop
            break
        try:
            # Pick out the variable name
            short_name = codes_get(gid, "shortName")
            if short_name not in ["2t", "2d"]:
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
            if valid_time not in temp_data:
                temp_data[valid_time] = {}
            temp_data[valid_time][short_name] = avg_val

            print(f"Appended data from {valid_time}")
        finally: # Frees memory
            codes_release(gid)

# Compute relative humidity from temperature and dew point temp
RH_series = []
for t in sorted(temp_data.keys()):
    temp = temp_data[t].get("2t")
    dewtemp = temp_data[t].get("2d")
    if temp is not None and dewtemp is not None:
        # Convert to Celsius
        temp = temp - 273.15
        dewtemp = dewtemp - 273.15

        # Magnus formula
        es = 6.112 * math.exp((17.67 * temp) / (temp + 243.5))
        ed = 6.112 * math.exp((17.67 * dewtemp) / (dewtemp + 243.5))
        # RH = 100 * (ed / es)
        RH = ed / es
        RH_series.append(RH)

# Construct output file
with open(out_fol+output_file, "w") as out:
    out.write(f"# time {varname}\n")
    for i, val in enumerate(RH_series):
        seconds = i * time_step
        out.write(f"{seconds} {val}\n")

print(f"Saved hourly time series to {output_file}")
