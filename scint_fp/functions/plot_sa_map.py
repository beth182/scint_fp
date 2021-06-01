# Beth Saunders 01/06/21
# script to produce maps of source area, model grid & building height's all in one figure

# imports
import matplotlib.pyplot as plt
import contextily as cx
import geopandas as gpd
import rasterio
import rasterio.plot


def plot_map(shpfile_dir, fp_raster):
    """
    Function to produce plots of SAs and maps
    """
    # ToDo: docstring

    raster = rasterio.open(fp_raster)
    fig, ax = plt.subplots()

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
    fig.colorbar(image_hidden, ax=ax)

    rasterio.plot.show(raster, ax=ax)

    plt.show()

    print('end')


shpfile_dir = 'C:/Users/beths/Desktop/LANDING/UKV_shapefiles/'
fp_raster = 'C:/Users/beths/Desktop/LANDING/fp_raster_tests/BCT_IMU_15000_2016_142_12.tif'

plot_map(shpfile_dir, fp_raster)

print('end')
