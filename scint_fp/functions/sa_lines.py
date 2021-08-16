import contextily as cx
import rasterio
import rasterio.plot
import numpy as np
import matplotlib.pyplot as plt


filename = 'C:/Users/beths/Desktop/LANDING/fp_output/111/10_mins/BCT_IMU_15000_2016_111_11_00.tif'

# deal with files

# tbc





# handle raster ########################################################################################################

raster = rasterio.open(filename)

raster_array = raster.read()

# make all 0 vals in array nan
raster_array[raster_array == 0.0] = np.nan

# force non-zero vals to be 1
bool_arr = np.ones(raster_array.shape)

# remove nans in bool array
nan_index = np.where(np.isnan(raster_array))
bool_arr[nan_index] = 0.0

# get location of max val
ind_max_2d = np.unravel_index(np.nanargmax(raster_array), raster_array.shape)[1:]
max_coords = raster.xy(ind_max_2d[0], ind_max_2d[1])

# make plot ############################################################################################################
fig, ax = plt.subplots(figsize=(10, 10))
rasterio.plot.show(raster, ax=ax)
cx.add_basemap(ax, crs=raster.crs)
rasterio.plot.show(bool_arr, transform=raster.transform, contour=True, contour_label_kws={}, ax=ax)
ax.scatter(max_coords[0], max_coords[1], color='red', marker='o', s=30)

plt.show()



print('end')


def sa_lines(domain_size = 15000,
             tr_rx = 'BCT_IMU',
             sa_dir = 'C:/Users/beths/Desktop/LANDING/fp_output/111/10_mins'):
    """
    Function to create a plot of sa's on a map - represented by a line at their furtherst extent (or set % cut off)
        And a marker at the value of the highest weight
    :return:
    """

