import os
import glob
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

path_string = 'BCT_IMU'

# main_dir = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintillometer_footprints/scint_fp/test_outputs/10_mins_ending/'
main_dir = '/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintillometer_footprints/scint_fp/test_outputs/10_mins_ending/'

out_dir = './'

csv_path = '../DOY_in.csv'
DOY_in_df = pd.read_csv(csv_path)
DOY_in_df['doy_string'] = DOY_in_df.Year.astype(str) + DOY_in_df.DOY.astype(str).str.zfill(3)
DOYlist = DOY_in_df['doy_string'].astype(int).to_list()

file_list = []
for DOY in DOYlist:
    # make filepath for the given day
    DOYstring = str(DOY)
    current_dir = main_dir + DOYstring + '/'

    # find all files for the current day and append to list
    os.chdir(current_dir)
    for file in glob.glob("*"+path_string+"*.tif"):
        file_list.append(current_dir + file)


# take first raster
raster = rasterio.open(file_list[0])
raster_array = raster.read(1)
raster_array[np.isnan(raster_array)] = 0


for i in range(1, len(file_list)):
    raster_add = rasterio.open(file_list[i])
    raster_array_add = raster_add.read(1)
    raster_array_add[np.isnan(raster_array_add)] = 0
    raster_array += raster_array_add
    raster_add.close()


# get rid of zero values
raster_array[raster_array == 0.0] = np.nan

# Write to TIFF
kwargs = raster.meta
kwargs.update(
    dtype=rasterio.float32,
    count=1,
    compress='lzw')

with rasterio.open(os.path.join(out_dir, 'combine.tif'), 'w', **kwargs) as dst:
    dst.write_band(1, raster_array.astype(rasterio.float32))



print('end')
