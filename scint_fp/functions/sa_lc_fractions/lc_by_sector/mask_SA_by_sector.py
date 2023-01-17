# Beth Saunders 13/01/23
# split landcover dataset into sectors by angle and calculate land cover fraction

# imports
import numpy as np
from rasterio.mask import mask
import rasterio
import os
import glob

from scint_fp.functions.sa_lc_fractions.lc_by_sector import define_sectors


def mask_raster_by_sector(raster_filepath,
                          centre_point,
                          save_path,
                          num_of_sectors=12):
    # read in raster file
    sa_raster = rasterio.open(raster_filepath)

    # define sectors
    # using define_sectors.py

    # get biggest dimention of SA raster
    # height or width?

    raster_width = np.abs(sa_raster.bounds.right - sa_raster.bounds.left)
    raster_height = np.abs(sa_raster.bounds.top - sa_raster.bounds.bottom)

    max_dim = max(raster_width, raster_height)

    # take this as radius - to make a circle twice as large as the SA file

    # define sectors
    polys = define_sectors.define_sectors(centre_point,
                                          num_of_sectors,
                                          max_dim,
                                          start=0,
                                          end=360,
                                          steps=90)

    # sanity checks
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    sa_array = sa_raster.read(1)
    rasterio.plot.show(sa_array, transform=sa_raster.transform, ax=ax)
    ax.scatter(centre_point.x[0], centre_point.y[0], marker='o', s=100, color='red')

    for poly in polys:
        x, y = poly.exterior.xy
        ax.plot(x, y)
    plt.show()
    """

    # set up raster saves
    raster_save_path = save_path + 'sector_rasters/'
    assert os.path.isdir(raster_save_path)  # make sure file path exists before saving

    # remove old files if they exist
    files = glob.glob(raster_save_path + '*')
    for f in files:
        os.remove(f)

    # mask raster by sector polygon
    for i in range(0, len(polys)):
        masked_SA, masked_SA_transform = mask(sa_raster, [polys[i]])
        masked_SA[0][masked_SA[0] == 0] = np.nan

        sector_name = i + 1

        # sanity checks
        """
        import rasterio.plot
        rasterio.plot.show(masked_SA[0], transform=masked_SA_transform)
        """

        # save the sector as a raster
        new_dataset = rasterio.open(raster_save_path + str(sector_name) + '.tif', 'w', driver='GTiff',
                                    height=masked_SA.shape[1], width=masked_SA.shape[2],
                                    count=1, dtype=str(masked_SA.dtype),
                                    crs=sa_raster.crs,
                                    transform=masked_SA_transform)

        new_dataset.write(masked_SA)
        new_dataset.close()
