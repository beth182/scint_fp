# Beth Saunders 13/01/23
# split landcover dataset into sectors by angle and calculate land cover fraction

# imports
import os
import matplotlib.pyplot as plt

from scint_fp.functions.sa_lc_fractions.lc_by_sector import lc_by_sector

save_path = os.getcwd().replace('\\', '/') + '/'

# run this to make sector rasters
"""
from scint_fp.functions.sa_lc_fractions.lc_by_sector import mask_SA_by_sector
from shapely.geometry import Point

import scintools as sct

# define a centre point (in this case, the centre of the path)
# path 12 - BCT -> IMU
pair_raw = sct.ScintillometerPair(x=[285440.6056, 284562.3107],
                                  y=[5712253.017, 5712935.032],
                                  z_asl=[142, 88],
                                  pair_id='BCT_IMU',
                                  crs='epsg:32631')

centre_point = Point(pair_raw.path_center()[0].x, pair_raw.path_center()[0].y)
raster_filepath = 'C:/Users/beths/OneDrive - University of Reading/Paper 2/combine_rasters/BCT_IMU.tif'

mask_SA_by_sector.mask_raster_by_sector(raster_filepath, centre_point, save_path)
"""

# landcover function
# ToDo: currently manually feeding first raster as test. Need to make this a loop
lc_by_sector.lc_by_sector(sa_sector_tif_path=save_path + 'sector_rasters/1.tif',
                          save_path=save_path)

print('end')
