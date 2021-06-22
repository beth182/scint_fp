# Beth Saunders 01/06/21
# script to produce maps of source area, model grid & building height's all in one figure

# imports
import matplotlib.pyplot as plt
import contextily as cx
import geopandas as gpd
import rasterio
import rasterio.plot
from mpl_toolkits.axes_grid1 import make_axes_locatable


def plot_map(fp_raster,
             ax,
             fig,
             shpfile_dir='C:/Users/beths/Desktop/LANDING/UKV_shapefiles/'):
    """
    Function to produce plots of SAs and maps
    :param fp_raster: file path for raster containing source area
    :param shpfile_dir: Path to directory where UKV grid shape files are saved.
    :return:
    """
    # ToDo: docstring

    raster = rasterio.open(fp_raster)
    # fig, ax = plt.subplots()

    # plotting model grids as shape files:
    # all sites with a unique model grid
    site_list = ['BFCL', 'BTT', 'KSSW', 'NK', 'RGS', 'SWT']
    for site in site_list:
        shp_file_path = shpfile_dir + site + '.shp'
        df = gpd.read_file(shp_file_path)
        df.plot(edgecolor='k', ax=ax)

    cx.add_basemap(ax, crs=df.crs)

    # use imshow so that we have something to map the colorbar to
    image_hidden = ax.imshow(raster.read(1))
    # create an axes on the right side of ax. The width of cax will be 5%
    # of ax and the padding between cax and ax will be fixed at 0.05 inch.
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(image_hidden, ax=ax, cax=cax)

    plot = rasterio.plot.show(raster, ax=ax)

    return plot







hourly_dir = 'C:/Users/beths/Desktop/LANDING/fp_raster_tests/hourly/'
partial_name = 'BCT_IMU_65000_2016_142_'

# hours with source areas which fit in the UKV grids
# hours = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
# test hours
hours = [5, 12, 19]

# empty list for rasters
raster_paths = []
hour_strings = []

# get raster paths for every hour in list
for hour in hours:
    str_hour = str(hour)
    if hour < 10:
        hour_string = str_hour.zfill(2)
    else:
        hour_string = str_hour

    raster_path = hourly_dir + partial_name + hour_string + '.tif'
    raster_paths.append(raster_path)
    hour_strings.append(hour_string)


fig, axs = plt.subplots(len(hours), figsize = (30,30))

for i, raster in enumerate(raster_paths):

    plot_map(raster, axs[i], fig)
    plot_map(raster, axs[i], fig)



plt.show()

print('end')
