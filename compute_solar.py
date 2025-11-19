"""
Python script for estimation of the solar noon and instantaneous 
solar radiation based on date, time, and geographic location. It implements 
empirical equations derived from NOAA's solar position algorithms.
Author: Michal Kuraz, Vaclav Steinbach
Date: 15.05.2025
Dissertation work
"""
import math
from datetime import datetime, timedelta
import pytz
import os

"""
--- Location and timezone ---
"""
latitude = 50.125
longitude = 13.875
timezone_offset = 1 # Prague

"""
--- Time range ---
"""
# start_date = datetime(2025, 7, 25, 00, 00)
# end_date = datetime(2025, 7, 30, 00, 00)
# start_date = datetime(2025, 9, 5, 00, 00)
# end_date = datetime(2025, 9, 6, 12, 00)
start_date = datetime(2024, 9, 8, 00, 00)
end_date = datetime(2024, 9, 30, 00, 00)
# set time step
# time_step = timedelta(hours=1)
time_step = timedelta(minutes=10)
# convert it into seconds
time_step_sec = time_step.total_seconds()

# Out folder
out_dir = "out/"
output_file = "solar.in"
os.makedirs(out_dir, exist_ok=True)

def solarnoon(long, doy, tz):
    gamma = 2 * math.pi / 365.0 * doy

    eqtime = 229.18 * (
        0.000075 + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma)
        - 0.040849 * math.sin(2 * gamma)
    )

    snoon = 720 - 4 * long - eqtime  # in minutes
    return snoon / 60.0 + tz  # convert to hours and adjust to timezone


def radiation(date_str, long, la, tz):
    a = 0.25
    b = 0.5
    G_sc = 1360.0  # solar constant

    # Convert date string to datetime
    date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    doy = int(date.strftime("%j"))
    t = date.hour + date.minute / 60 # fractional hours

    r_lat = math.radians(la)

    noon = solarnoon(long, doy, tz)

    delta = 0.409 * math.sin((2 * math.pi * doy / 365.0) - 1.39)

    try:
        ws = math.acos(-math.tan(r_lat) * math.tan(delta))
    except ValueError:
        ws = 0  # handle edge cases near poles

    dr = 1 + 0.033 * math.cos(2 * math.pi * doy / 365.0)

    R_a = G_sc * dr * (
        ws * math.sin(r_lat) * math.sin(delta)
        + math.cos(r_lat) * math.cos(delta) * math.sin(ws)
    ) / math.pi
    R_a = max(0.0, R_a)

    sin_e = (
        math.sin(r_lat) * math.sin(delta)
        + math.cos(r_lat) * math.cos(delta) * math.cos(2 * math.pi * (t - noon) / 24.0)
    )

    R_s = max(sin_e * R_a, 0.0)

    S_t = (a + b) * R_s

    return S_t

# Generate time series
with open(out_dir+output_file, "w") as out:
    out.write("# time[s] S_t[W/m2]\n")
    t = 0
    current = start_date
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%dT%H:%M:%SZ")
        S_t = radiation(date_str, longitude, latitude, timezone_offset)
        out.write(f"{t} {S_t}\n")
        current += time_step
        t += int(time_step_sec)

print(f"Saved solar radiation time series to {output_file}")
