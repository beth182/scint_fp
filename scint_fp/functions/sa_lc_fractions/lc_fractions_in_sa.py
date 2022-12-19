# Beth Saunders 19/12/2022

# imports
import rasterio
import rasterio.plot
import numpy as np
import rasterio.features
from osgeo import gdal
from gdalconst import GA_ReadOnly
from collections import Counter
import pandas as pd
import datetime as dt


def landcover_fractions_in_SA_weighted(sa_tif_path, save_path):
    """
    Reads scintillometer source area and returns information about the type of landcover fractions present within
    :return:
    """

    # ToDo: move this file
    landcover_location = 'C:/Users/beths/OneDrive - University of Reading/Model_Eval/QGIS/Elliott/LandUseMM_7classes_32631.tif'

    # crop square extent of landcover fractions file to the same as the
    maskDs = gdal.Open(sa_tif_path, GA_ReadOnly)  # your mask raster
    projection = maskDs.GetProjectionRef()
    geoTransform = maskDs.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * maskDs.RasterXSize
    miny = maxy + geoTransform[5] * maskDs.RasterYSize
    data = gdal.Open(landcover_location, GA_ReadOnly)

    # Your data the one you want to clip
    output = save_path + 'output.tif'  # output file
    gdal.Translate(output, data, format='GTiff', projWin=[minx, maxy, maxx, miny], outputSRS=projection)

    # reads this cropped dataset
    landcover_crop = rasterio.open(output)
    landcover_array = landcover_crop.read(1)

    # reads sa tif
    sa_raster = rasterio.open(sa_tif_path)
    sa_array = sa_raster.read(1)

    # test of two arrays have the same shape
    if sa_array.shape == landcover_array.shape:
        pass
    else:
        if landcover_array.shape == sa_array[0:sa_array.shape[0] - 1, 0:sa_array.shape[1] - 2].shape:
            sa_array = sa_array[0:sa_array.shape[0] - 1, 0:sa_array.shape[1] - 2]
        elif landcover_array.shape == sa_array[0:sa_array.shape[0] - 1, 0:sa_array.shape[1] - 1].shape:
            # remove last row/col
            sa_array = sa_array[0:sa_array.shape[0] - 1, 0:sa_array.shape[1] - 1]
        else:
            assert sa_array.shape == landcover_array.shape

    # mask array
    mask = np.ma.masked_where(np.isnan(sa_array), landcover_array, copy=True)

    color_list = ["white", "dimgrey", "lightgrey", "deepskyblue", "lawngreen", "darkgreen", "limegreen", "olive"]

    # fill masked area with 0s
    masked_filled = mask.filled(0)

    # find the associated sa weights for each type of land cover present
    # dict to append to in loop
    sa_percent_lc = {}
    # total sum of sa array
    sa_tot_sum = np.nansum(sa_array)

    for i in range(1, 8):
        # take a copy of masked landcover array
        only_target_lc = masked_filled.copy()

        # find which pixels in the masked landcover array are the target type
        only_target_lc[np.where(only_target_lc != i)] = 0

        # mask the source area array only where the target landcover is
        sa_mask_target_lc = np.ma.masked_where(only_target_lc == 0, sa_array, copy=True)

        # sum the sa weights for this lc type
        sum_sa_target_lc = np.nansum(sa_mask_target_lc)

        # represent this as a total percentage of the sa weights
        sa_target_lc_percent = (sum_sa_target_lc / sa_tot_sum) * 100

        sa_percent_lc[i] = sa_target_lc_percent

    # create a df from this dict
    df_sa_percents = pd.DataFrame.from_dict(sa_percent_lc, orient='index')
    df_sa_percents.columns = ['sa_weight_percent']

    # how frequent do the pixel types appear in the total masked lc array?
    # flatten the 2d array to 1d & count how often the pixels appear
    count = Counter(masked_filled.flatten())

    # convert to df
    df = pd.DataFrame.from_dict(count, orient='index')
    df.columns = ['pixel_count']
    df = df.sort_index()

    print(sa_tif_path)

    # need to check whether all values (0-7) are included
    for i in range(0, 8):
        # check whether i is in df.index
        if i in df.index:
            pass
        else:
            d = {'ind': [i], 'pixel_count': [0]}
            new_df = pd.DataFrame(data=d)
            new_df = new_df.set_index('ind')
            df = df.append(new_df)
            df = df.sort_index()

    df['colours'] = color_list

    df['labels'] = ['None', 'Building', 'Impervious', 'Water', 'Grass', 'Deciduous', 'Evergreen', 'Shrub']

    df = df.drop(0, axis=0)

    total_count = np.sum(df['pixel_count'])

    df['percent_of_type_in_lc'] = (df['pixel_count'] / total_count) * 100

    df_merge = df.merge(df_sa_percents, how='outer', left_index=True, right_index=True)

    return df_merge


def lc_fract_multiple_sas(sa_list, save_path):
    """
    Returns df of sa-weighted lc fractions present in each timestep's obs sa
    :param sa_list:
    :return:
    """

    df = pd.DataFrame()

    for sa_path in sa_list:
        # get the time from the path name
        time_string = sa_path[-18:-4]
        datetime_object = dt.datetime.strptime(time_string, '%Y_%j_%H_%M')

        sa_df = landcover_fractions_in_SA_weighted(sa_path, save_path)

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
        df_sa.index = [datetime_object]

        df = df.append(df_sa)

    return df
