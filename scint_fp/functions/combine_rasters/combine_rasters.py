import os
import glob
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# from scint_fp.functions import landcover_type_present as lc


def combine_sa_rasters(path_string,
                       main_dir='//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintillometer_footprints/scint_fp/test_outputs/10_mins_ending/',
                       # main_dir='/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintillometer_footprints/scint_fp/test_outputs/10_mins_ending/'
                       ):
    """
    Takes a list of days (from csv, e.g. DOY_in) and combine each source area of that day (all times) into one
    source area - representing a "climatology" source area of the given target period (days included).

    # ToDo: fill these out
    :param path_string:
    :param main_dir:
    :return:
    """

    out_dir = '../'

    # reads in target days from a csv file
    csv_path = '../../DOY_in.csv'
    DOY_in_df = pd.read_csv(csv_path)
    DOY_in_df['doy_string'] = DOY_in_df.Year.astype(str) + DOY_in_df.DOY.astype(str).str.zfill(3)
    DOYlist = DOY_in_df['doy_string'].astype(int).to_list()

    file_list = []
    for DOY in DOYlist:
        # construct filepath for the given day
        DOYstring = str(DOY)
        current_dir = main_dir + DOYstring + '/'

        # find all the sa files (e.g. for each time period) for the current target day and append to list
        os.chdir(current_dir)
        for file in glob.glob("*" + path_string + "*.tif"):
            file_list.append(current_dir + file)

    # take first raster separately for dimensions
    raster = rasterio.open(file_list[0])
    raster_array = raster.read(1)
    raster_array[np.isnan(raster_array)] = 0

    # now for each raster (but not including the first, as this has already been read above
    for i in range(1, len(file_list)):
        print(file_list[i])
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


if __name__ == '__main__':
    # CHANGE HERE
    target_path = 'IMU_BTT'

    # calls function
    combine_sa_rasters(target_path)

    print('end')
