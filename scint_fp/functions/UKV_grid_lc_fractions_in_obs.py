# Getting the land cover fractions from the reference (observation) dataset - in the area of each UKV grid-box

# imports
import rasterio.plot
import geopandas
from rasterio.mask import mask
import numpy as np
import pandas as pd

# read in the reference dataset
landcover_raster_filepath = 'C:/Users/beths/OneDrive - University of Reading/Model_Eval/QGIS/Elliott/LandUseMM_7classes_32631.tif'
landcover_raster = rasterio.open(landcover_raster_filepath)

# read in the UKV grid geo-reference data for each grid
gpkg_dir_path = 'C:/Users/beths/OneDrive - University of Reading/UKV_grid_objects/grid_gpkg_files/'

grid_df_list = []

for i in range(1, 43):

    grid_num = str(i)
    gpkg_file_name = grid_num + '.gpkg'
    gpkg_file = gpkg_dir_path + gpkg_file_name
    grid_gpkg = geopandas.read_file(gpkg_file)

    # create a mask of the desired area
    grid_geometry = grid_gpkg.geometry

    masked, mask_transform = mask(dataset=landcover_raster,
                                  shapes=grid_geometry, crop=True,
                                  all_touched=False,
                                  filled=False)

    masked = masked.squeeze()

    lc_grids = {}

    total_sum_of_grid = masked.sum()

    for j in range(1, 8):
        # take a copy of maked landcover array
        only_target_lc = masked.copy()

        # find which pixels in the masked landcover array are the target type
        only_target_lc[np.where(only_target_lc != j)] = 0

        # sum this lc type
        type_sum = only_target_lc.sum()

        # get percent
        lc_percent = (type_sum / total_sum_of_grid) * 100

        # add to dict
        lc_grids[j] = [lc_percent]

    # make dict into df
    grid_df = pd.DataFrame.from_dict(lc_grids)
    grid_df.index = [i]

    grid_df_list.append(grid_df)

# combine all the df
df = pd.concat(grid_df_list)
df = df.rename(
    columns={1: 'Roof', 2: 'Canyon', 3: 'Water', 4: 'Grass', 5: 'Deciduous', 6: 'Evergreen', 7: 'Shrub'})

df['Built'] = df.Roof + df.Canyon
df['Vegetation'] = df.Grass + df.Deciduous + df.Evergreen + df.Shrub

df.to_csv(
    'C:/Users/beths/OneDrive - University of Reading/local_runs_data/reference_data_lc_fractions_in_UKV_grids.csv')

print('end')
