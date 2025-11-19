"""
Script for exploration and manipulation of GRIB files
Author: Vaclav Steinbach
Date: 11.06.2025
Dissertation work
"""
import xarray as xr # working with GRIB files
import sys

grib_file = str(sys.argv[1]) + '.grib'
# In/Out folder
data_fol = "data/"
out_fol = "out/"
os.makedirs(out_dir, exist_ok=True)
ds = xr.open_dataset(data_fol+grib_file, engine="cfgrib")
print(ds['tp']) 
