# Beth Saunders 13/01/23
# split landcover dataset into sectors by angle and calculate land cover fraction

# imports
import numpy as np
from shapely.geometry import Point
from rasterio.mask import mask

import scintools as sct

from scint_fp.functions.sa_lc_fractions.lc_by_sector import define_sectors

# define a centre point (in this case, the centre of the path)
# path 12 - BCT -> IMU
pair_raw = sct.ScintillometerPair(x=[285440.6056, 284562.3107],
                                  y=[5712253.017, 5712935.032],
                                  z_asl=[142, 88],
                                  pair_id='BCT_IMU',
                                  crs='epsg:32631')

centre_point = pair_raw.path_center()

# read in SA file
# ToDo: temp file, replace to be dynamic in function
# example SA raster:
SA_file = 'C:/Users/beths/OneDrive - University of Reading/Paper 2/combine_rasters/BCT_IMU.tif'
sa_raster = rasterio.open(SA_file)

# define sectors

# get biggest dimention of SA raster
# height or width?

raster_width = np.abs(sa_raster.bounds.right - sa_raster.bounds.left)
raster_height = np.abs(sa_raster.bounds.top - sa_raster.bounds.bottom)

max_dim = max(raster_width, raster_height)

# take this as radius - to make a circle twice as large as the SA file

# define sectors
polys = define_sectors.define_sectors(Point(centre_point[0].x, centre_point[0].y),
                                      12,
                                      max_dim,
                                      start=0,
                                      end=360,
                                      steps=90)

# sanity checks
"""
import matplotlib.pyplot as plt
import rasterio.plot

fig, ax = plt.subplots()
sa_array = sa_raster.read(1)
rasterio.plot.show(sa_array, transform=sa_raster.transform, ax=ax)
ax.scatter(centre_point.x[0], centre_point.y[0], marker='o', s=100, color='red')

for poly in polys:
    x, y = poly.exterior.xy
    ax.plot(x, y)
plt.show()

rasterio.plot.show(masked_SA[0], transform=masked_SA_transform)
"""

masked_SA, masked_SA_transform = mask(sa_raster, [polys[0]])
masked_SA[0][masked_SA[0] == 0] = np.nan

print('end')

out_image, out_transform = mask(sa_raster, [polys[0]])
