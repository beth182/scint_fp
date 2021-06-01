# Beth Saunders 01/06/21
# script to produce maps of source area, model grid & building height's all in one figure

# imports
import rasterio
import matplotlib.pyplot as plt
import shapefile as shp  # Requires the pyshp package


def plot_map(shpfile_dir):
    """
    Function to produce plots of SAs and maps
    """

    # all sites with a unique model grid
    site_list = ['BFCL', 'BTT', 'KSSW', 'NK', 'RGS', 'SWT']

    plt.figure()

    for site in site_list:

        shp_file_path = shpfile_dir + site + '.shp'

        shp_file = shp.Reader(shp_file_path)

        for shape in shp_file.shapeRecords():
            x = [i[0] for i in shape.shape.points[:]]
            y = [i[1] for i in shape.shape.points[:]]
            plt.plot(x, y)

    plt.show()


shpfile_dir = 'C:/Users/beths/Desktop/LANDING/UKV_shapefiles/'
plot_map(shpfile_dir)

print('end')