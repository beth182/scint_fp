# Beth Saunders 13/01/23
# split landcover dataset into sectors by angle and calculate land cover fraction

# imports
import numpy as np
from rasterio.mask import mask
import rasterio

from scint_fp.functions.sa_lc_fractions.lc_by_sector import define_sectors


def mask_raster_by_sector(raster_filepath,
                          centre_point,
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

    # mask raster by sector polygon
    raster_by_sector_image = {}
    raster_by_sector_transform = {}

    for i in range(0, len(polys)):
        masked_SA, masked_SA_transform = mask(sa_raster, [polys[i]])
        masked_SA[0][masked_SA[0] == 0] = np.nan

        out_image, out_transform = mask(sa_raster, [polys[i]])

        key_name = i + 1

        raster_by_sector_image[key_name] = out_image
        raster_by_sector_image[key_name] = out_transform

        # sanity checks
        """
        import rasterio.plot
        rasterio.plot.show(masked_SA[0], transform=masked_SA_transform)
        """

    return {'images': raster_by_sector_image, 'transform': raster_by_sector_image}
