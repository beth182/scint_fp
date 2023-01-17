# Beth Saunders 13/01/23
# split landcover dataset into sectors by angle and calculate land cover fraction

# imports
import os
import pandas as pd
from shapely.geometry import Point

from scint_fp.functions.sa_lc_fractions.lc_by_sector import mask_SA_by_sector
from scint_fp.functions.sa_lc_fractions import lc_fractions_in_sa
from scint_fp.functions.sa_lc_fractions.lc_by_sector import lc_by_sector

import scintools as sct

# user choices here
path_name = 'SCT_SWT'

save_path = os.getcwd().replace('\\', '/') + '/'

# Make sector rasters
# """
# define a centre point (in this case, the centre of the path)
if path_name == 'BCT_IMU':
    # path 12 - BCT -> IMU
    pair_raw = sct.ScintillometerPair(x=[285440.6056, 284562.3107],
                                      y=[5712253.017, 5712935.032],
                                      z_asl=[142, 88],
                                      pair_id='BCT_IMU',
                                      crs='epsg:32631')
elif path_name == 'BTT_BCT':
    # path 11 - BTT -> BCT
    pair_raw = sct.ScintillometerPair(x=[282251.14, 285440.6056],
                                      y=[5712486.47, 5712253.017],
                                      z_asl=[180, 142],
                                      pair_id='BTT_BCT',
                                      crs='epsg:32631')

elif path_name == 'IMU_BTT':
    # path 13 - IMU -> BTT
    pair_raw = sct.ScintillometerPair(x=[284562.3107, 282251.14],
                                      y=[5712935.032, 5712486.47],
                                      z_asl=[88, 180],
                                      pair_id='IMU_BTT',
                                      crs='epsg:32631')

elif path_name == 'SCT_SWT':
    # path 15 - SCT -> SWT
    pair_raw = sct.ScintillometerPair(x=[284450.1944, 285407],
                                      y=[5708094.734, 5708599.83],
                                      z_asl=[51, 44],
                                      pair_id='SCT_SWT',
                                      crs='epsg:32631')
else:
    raise ValueError('Path name not an option.')

centre_point = Point(pair_raw.path_center()[0].x, pair_raw.path_center()[0].y)
raster_filepath = 'C:/Users/beths/OneDrive - University of Reading/Paper 2/combine_rasters/' + path_name + '.tif'

# mask SA by sector and sae tif
mask_SA_by_sector.mask_raster_by_sector(raster_filepath, centre_point, save_path)
# """

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

# plot
lc_by_sector.lc_polar_plot(path_name, df)
print('end')
