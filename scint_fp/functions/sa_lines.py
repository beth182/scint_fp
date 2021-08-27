import contextily as cx
import rasterio.plot
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import geopandas as gpd


# sa_dir = 'C:/Users/beths/Desktop/LANDING/fp_output/111/10_mins/'
sa_dir = 'C:/Users/beths/Desktop/LANDING/fp_output/111/hourly/'

# deal with files
file_list = []
os.chdir(sa_dir)
for file in glob.glob("*.tif"):
    file_list.append(sa_dir + file)

# file_list = ['C:/Users/beths/Desktop/LANDING/fp_output/111/10_mins/BCT_IMU_15000_2016_111_11_00.tif',
#              'C:/Users/beths/Desktop/LANDING/fp_output/111/10_mins/BCT_IMU_15000_2016_111_11_10.tif']

# colours ##############################################################################################################
cmap = plt.cm.inferno  # define the colormap
# extract all colors from the .jet map
cmaplist = [cmap(i) for i in range(cmap.N)]

list_len = len(file_list)

colour_len = len(cmaplist)

colour_intervals = int(colour_len / list_len)

colour_list = []

count = 0
for i in file_list:
    color_choice = cmaplist[count]
    colour_list.append(color_choice)
    count += colour_intervals

# initalize plot #######################################################################################################
raster0 = rasterio.open(file_list[0])
fig, ax = plt.subplots(figsize=(10, 10))
rasterio.plot.show(raster0, ax=ax, alpha=0.0)
cx.add_basemap(ax, crs=raster0.crs, alpha=0.5)


# handle raster ########################################################################################################
for i, filename in enumerate(file_list):
    replc = filename.replace('.', '_')
    splt = replc.split('_')
    time_string = splt[-3] + ':' + splt[-2]

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

    # make plot ########################################################################################################

    colour_here = list(colour_list[i])

    rasterio.plot.show(bool_arr, transform=raster.transform, contour=True, contour_label_kws={}, ax=ax,
                       colors=[colour_here])
    ax.scatter(max_coords[0], max_coords[1], color=colour_here, marker='o', s=30, label=time_string)


# plot path
df = gpd.read_file('C:/Users/beths/Desktop/LANDING/scint_path_shp/scint_path.shp')
df.plot(edgecolor='green', ax=ax, linewidth=4.0)

plt.legend()
plt.show()

print('end')


def sa_lines(domain_size=15000,
             tr_rx='BCT_IMU',
             sa_dir='C:/Users/beths/Desktop/LANDING/fp_output/111/10_mins'):
    """
    Function to create a plot of sa's on a map - represented by a line at their furtherst extent (or set % cut off)
        And a marker at the value of the highest weight
    :return:
    """
