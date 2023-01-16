# Beth Saunders 13/01/23
# split landcover dataset into sectors by angle and calculate land cover fraction

# imports
import os
import pandas as pd
import matplotlib.pyplot as plt

from scint_fp.functions.sa_lc_fractions import lc_fractions_in_sa

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

# landcover functions in each sector - weighted by SA


sa_sector_dir = save_path + 'sector_rasters/'

df = pd.DataFrame()

for file in os.listdir(sa_sector_dir):
    file_path = sa_sector_dir + file

    sa_df = lc_fractions_in_sa.landcover_fractions_in_SA_weighted(sa_tif_path=file_path,
                                                               save_path=save_path)

    # getting df in correct format for bar plot
    df_sa_columns = ['Building', 'Impervious', 'Water', 'Grass', 'Deciduous', 'Evergreen', 'Shrub']
    df_sa_data = [[sa_df.loc[1]['sa_weight_percent'],
                   sa_df.loc[2]['sa_weight_percent'],
                   sa_df.loc[3]['sa_weight_percent'],
                   sa_df.loc[4]['sa_weight_percent'],
                   sa_df.loc[5]['sa_weight_percent'],
                   sa_df.loc[6]['sa_weight_percent'],
                   sa_df.loc[7]['sa_weight_percent']]]
    # a dataframe of one source area
    df_sa = pd.DataFrame(df_sa_data, columns=df_sa_columns)
    df_sa.index = [int(file.split('.')[0])]  # index as sector number

    df = df.append(df_sa)

df = df.sort_index()

print('end')
