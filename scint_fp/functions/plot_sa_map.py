# Beth Saunders 01/06/21
# script to produce maps of source area, model grid & building height's all in one figure

# imports
import rasterio
import matplotlib.pyplot as plt
import shapefile as shp  # Requires the pyshp package
import scintools as sct
import copy
from scintools.PointFootprint import _load_rasters

import contextily as cx

import geopandas as gpd



def plot_map(shpfile_dir):
    """
    Function to produce plots of SAs and maps
    """
    # ToDo: docstring

    # take first site (BFCL) to define ax
    df_initial = gpd.read_file(shpfile_dir + 'BFCL.shp')
    ax = df_initial.plot(edgecolor='k')

    # plotting model grids as shape files:
    # all sites with a unique model grid
    site_list = ['BTT', 'KSSW', 'NK', 'RGS', 'SWT']
    for site in site_list:
        shp_file_path = shpfile_dir + site + '.shp'
        df = gpd.read_file(shp_file_path)
        df.plot(edgecolor='k', axes=ax)

    cx.add_basemap(ax, crs=df.crs)
    plt.show()

    print('end')



shpfile_dir = 'C:/Users/beths/Desktop/LANDING/UKV_shapefiles/'

plot_map(shpfile_dir)

print('end')