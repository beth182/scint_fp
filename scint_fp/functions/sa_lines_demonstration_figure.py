import contextily as cx
import rasterio.plot
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import geopandas as gpd
import matplotlib as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable


# sa_dir = 'C:/Users/beths/Desktop/LANDING/fp_output/demonstration_figure/point_fp/'
sa_dir = 'C:/Users/beths/Desktop/LANDING/fp_output/demonstration_figure/'

# deal with files
file_list = []
os.chdir(sa_dir)
for file in glob.glob("*.tif"):
    file_list.append(sa_dir + file)

grid_dir = 'C:/Users/beths/Desktop/LANDING/UKV_shapefiles/'
grid_file_list = []
os.chdir(grid_dir)
for file in glob.glob("*.shp"):
    grid_file_list.append(grid_dir + file)

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
fig, ax = plt.subplots(figsize=(12, 12))
rasterio.plot.show(raster0, ax=ax, alpha=0.0)
cx.add_basemap(ax, crs=raster0.crs, alpha=0.5)

# sex ax lims
ax.set_xlim(281314.7269919119, 285676.31545750913)
ax.set_ylim(5709795.207536185, 5713837.796845389)



image_hidden = ax.imshow(raster0.read(1))


divider = make_axes_locatable(ax)
# cax = divider.append_axes("top", size="5%", pad=0.05)
cax = fig.add_axes([0.27, 0.18, 0.5, 0.02])
fig.colorbar(image_hidden, ax=ax, cax=cax, orientation='horizontal')


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


    # make plot ########################################################################################################

    colour_here = list(colour_list[i])

    # rasterio.plot.show(bool_arr, transform=raster.transform, contour=True, contour_label_kws={}, ax=ax,
    #                    colors=[colour_here])

    rasterio.plot.show(raster_array, transform=raster.transform, ax=ax)


# plot path
df = gpd.read_file('C:/Users/beths/Desktop/LANDING/scint_path_shp/scint_path.shp')
# df.plot(edgecolor='green', ax=ax, linewidth=3.0, zorder=1, alpha=0.6)
df.plot(edgecolor='green', ax=ax, linewidth=4.0, zorder=1)

# plot points
# df_points = gpd.read_file('C:/Users/beths/Desktop/LANDING/fp_output/demonstration_figure/points/weighted.shp')
# colour_list_cmap = mpl.colors.LinearSegmentedColormap.from_list("", colour_list)
# df_points.plot(ax=ax, cmap=colour_list_cmap, zorder=2)

df_points = gpd.read_file('C:/Users/beths/Desktop/LANDING/fp_output/demonstration_figure/points/equal.shp')
df_points.plot(ax=ax, color='white', zorder=2, marker='.', markersize=10)


for file in grid_file_list:
    df_grid = gpd.read_file(file)
    df_grid.plot(ax=ax, zorder=0)

# plt.show()
plt.savefig('C:/Users/beths/Desktop/LANDING/yeeeeeeee.png', bbox_inches='tight')

print('end')


def sa_lines(domain_size=15000,
             tr_rx='BCT_IMU',
             sa_dir='C:/Users/beths/Desktop/LANDING/fp_output/111/10_mins'):
    """
    Function to create a plot of sa's on a map - represented by a line at their furtherst extent (or set % cut off)
        And a marker at the value of the highest weight
    :return:
    """
