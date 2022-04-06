import rasterio
import rasterio.plot
import matplotlib.pyplot as plt
import numpy as np
import rasterio.features
from osgeo import gdal
from gdalconst import GA_ReadOnly
from collections import Counter
import pandas as pd
from matplotlib import colors
import datetime as dt
import glob
import os
import matplotlib as mpl
mpl.rcParams.update({'font.size': 15})  # updating the matplotlib fontsize


def landcover_fractions_in_SA(sa_tif_path):
    """
    Reads scintillometer source area and returns information about the type of landcover fractions present within
    :return:
    """

    landcover_location = 'C:/Users/beths/OneDrive - University of Reading/Model_Eval/QGIS/BIG_MAP/BIG_MAP_CROP.tif'

    # crop square extent of landcover fractions file to the same as the
    maskDs = gdal.Open(sa_tif_path, GA_ReadOnly)  # your mask raster
    projection = maskDs.GetProjectionRef()
    geoTransform = maskDs.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * maskDs.RasterXSize
    miny = maxy + geoTransform[5] * maskDs.RasterYSize
    data = gdal.Open(landcover_location, GA_ReadOnly)  # Your data the one you want to clip
    output = 'C:/Users/beths\Desktop/LANDING/mask_tests/output.tif'  # output file
    gdal.Translate(output, data, format='GTiff', projWin=[minx, maxy, maxx, miny], outputSRS=projection)

    # reads this cropped dataset
    landcover_crop = rasterio.open(output)
    landcover_array = landcover_crop.read(1)

    # reads sa tif
    sa_raster = rasterio.open(sa_tif_path)
    sa_array = sa_raster.read(1)
    # remove last row/col
    sa_array = sa_array[0:sa_array.shape[0] - 1, 0:sa_array.shape[1] - 1]

    # test of two arrays have the same shape
    assert sa_array.shape == landcover_array.shape

    # mask array
    mask = np.ma.masked_where(np.isnan(sa_array), landcover_array, copy=True)

    color_list = ["white", "dimgrey", "lightgrey", "deepskyblue", "lawngreen", "darkgreen", "limegreen", "olive"]

    # make a color map of fixed colors
    cmap = colors.ListedColormap(color_list)
    bounds = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    # tell imshow about color map so that only set colors are used
    img = plt.imshow(mask, interpolation='nearest',
                     cmap=cmap, norm=norm)

    # make a color bar
    cbar = plt.colorbar(img, cmap=cmap, norm=norm, boundaries=bounds)
    cbar.set_ticks([1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5])
    cbar.set_ticklabels(['Building', 'Impervious', 'Water', 'Grass', 'Deciduous', 'Evergreen', 'Shrub'])

    plt.show()
    # plt.savefig('C:/Users/beths/Desktop/LANDING/mask_tests/yeet.png', figsize=(50,50))

    print('end')

    temp = mask.filled(0)

    # how frequent do the pixel types appear
    count = Counter(temp.flatten())

    # convert to df
    df = pd.DataFrame.from_dict(count, orient='index')
    df.columns = ['count']
    df = df.sort_index()

    df['colours'] = color_list

    df['labels'] = ['None', 'Building', 'Impervious', 'Water', 'Grass', 'Deciduous', 'Evergreen', 'Shrub']

    df = df.drop(0, axis=0)

    total = np.sum(df['count'])

    df['percent'] = (df['count'] / total) * 100

    plt.pie(df['percent'], colors=df['colours'], labels=df['labels'], autopct='%1.2f%%')

    plt.show()

    print('end')


def landcover_fractions_in_SA_weighted(sa_tif_path):
    """
    Reads scintillometer source area and returns information about the type of landcover fractions present within
    :return:
    """

    landcover_location = 'C:/Users/beths/OneDrive - University of Reading/Model_Eval/QGIS/BIG_MAP/BIG_MAP_CROP.tif'

    # crop square extent of landcover fractions file to the same as the
    maskDs = gdal.Open(sa_tif_path, GA_ReadOnly)  # your mask raster
    projection = maskDs.GetProjectionRef()
    geoTransform = maskDs.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * maskDs.RasterXSize
    miny = maxy + geoTransform[5] * maskDs.RasterYSize
    data = gdal.Open(landcover_location, GA_ReadOnly)  # Your data the one you want to clip
    output = 'C:/Users/beths/Desktop/LANDING/mask_tests/output.tif'  # output file
    gdal.Translate(output, data, format='GTiff', projWin=[minx, maxy, maxx, miny], outputSRS=projection)

    # reads this cropped dataset
    landcover_crop = rasterio.open(output)
    landcover_array = landcover_crop.read(1)

    # reads sa tif
    sa_raster = rasterio.open(sa_tif_path)
    sa_array = sa_raster.read(1)
    # remove last row/col
    sa_array = sa_array[0:sa_array.shape[0] - 1, 0:sa_array.shape[1] - 1]

    # test of two arrays have the same shape
    assert sa_array.shape == landcover_array.shape

    # mask array
    mask = np.ma.masked_where(np.isnan(sa_array), landcover_array, copy=True)

    color_list = ["white", "dimgrey", "lightgrey", "deepskyblue", "lawngreen", "darkgreen", "limegreen", "olive"]

    # make a color map of fixed colors
    cmap = colors.ListedColormap(color_list)
    bounds = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    # # tell imshow about color map so that only set colors are used
    # img = plt.imshow(mask, interpolation='nearest',
    #                  cmap=cmap, norm=norm)
    # # make a color bar
    # cbar = plt.colorbar(img, cmap=cmap, norm=norm, boundaries=bounds)
    # cbar.set_ticks([1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5])
    # cbar.set_ticklabels(['Building', 'Impervious', 'Water', 'Grass', 'Deciduous', 'Evergreen', 'Shrub'])
    # plt.show()
    # # plt.savefig('C:/Users/beths/Desktop/LANDING/mask_tests/yeet.png', figsize=(50,50))
    # print('end')

    # fill masked area with 0s
    masked_filled = mask.filled(0)

    # find the assossiated sa weights for each type of land cover present
    # dict to append to in loop
    sa_percent_lc = {}
    # total sum of sa array
    sa_tot_sum = np.nansum(sa_array)

    for i in range(1, 8):
        # take a copy of maked landcover array
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

    # plt.pie(df_merge['sa_weight_percent'], colors=df_merge['colours'], labels=df_merge['labels'], autopct='%1.2f%%')
    # plt.show()

    return df_merge


def lc_fract_multiple_sas(sa_list):
    """

    :param sa_list:
    :return:
    """

    df = pd.DataFrame()

    for sa_path in sa_list:
        # get the time from the path name
        time_string = sa_path[-18:-4]
        datetime_object = dt.datetime.strptime(time_string, '%Y_%j_%H_%M')
        time_label = datetime_object.strftime('%j %H:%M')

        sa_df = landcover_fractions_in_SA_weighted(sa_path)

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


def lc_in_sa_stacked_bar(sas_df_in):
    """
    Takes a dataframe of the land cover fractions present in the peropd's source areas
        And produces a stacked bar chart of them
    :param sas_df:
    :return:
    """

    if type(sas_df_in) == str:  # added option for reading in csv files

        sas_df = pd.read_csv(sas_df_in)
        sas_df.index = sas_df['Unnamed: 0']
        sas_df = sas_df.drop('Unnamed: 0', 1)

        title_label = sas_df_in.split('/')[-1][:3]

        sas_df.index = pd.to_datetime(sas_df.index, dayfirst=True)

    else:

        sas_df = sas_df_in

        # format the title string
        title_label = sas_df.index[0].strftime('%j')

        dt_index = sas_df.index.copy()

    # get rid of the masks: must be a better way of doing this
    dict_for_df = {}

    for col in sas_df.columns:

        new_col = []

        for item in sas_df[col]:
            if type(item) != float:
                new_col.append(0)
            else:
                new_col.append(item)

        dict_for_df[col] = new_col

    new_df = pd.DataFrame.from_dict(dict_for_df)
    new_df.index = sas_df.index


    print('end')

    # Box plot
    # """

    # take only building, impervious, grass, water
    df_select = new_df[['Building', 'Impervious', 'Water', 'Grass']]

    df_select.index.names = ['Time']
    df_select['Hour'] = df_select.index.hour + 1

    if df_select.index[0].strftime('%j') == '123':
        end_remove = pd.to_datetime('2016-05-02 17:00:00')
        df_select = df_select.loc[(df_select.index < end_remove)]

    elif df_select.index[0].strftime('%j') == '126':
        start_remove = pd.to_datetime('2016-05-05 06:00:00')
        end_remove = pd.to_datetime('2016-05-05 18:00:00')

        df_select = df_select.loc[(df_select.index >= start_remove)]
        df_select = df_select.loc[(df_select.index < end_remove)]

    fig, ax = plt.subplots(1, figsize=(12, 12))

    props_building = dict(boxes='#696969', whiskers="Black", medians="Black", caps="Black")
    props_imperv = dict(boxes="#BEBEBE", whiskers="Black", medians="Black", caps="Black")
    props_water = dict(boxes="#00BFFF", whiskers="Black", medians="Black", caps="Black")
    props_grass = dict(boxes="#7CFC00", whiskers="Black", medians="Black", caps="Black")

    df_select.boxplot('Building', 'Hour', ax=ax, color=props_building, patch_artist=True, sym='#696969', widths=0.95)
    df_select.boxplot('Impervious', 'Hour', ax=ax, color=props_imperv, patch_artist=True, sym='#BEBEBE', widths=0.95)
    df_select.boxplot('Water', 'Hour', ax=ax, color=props_water, patch_artist=True, sym='#00BFFF', widths=0.95)
    df_select.boxplot('Grass', 'Hour', ax=ax, color=props_grass, patch_artist=True, sym='#7CFC00', widths=0.95)

    fig.suptitle('')
    ax.set_title('')

    # plt.show()

    plt.savefig('C:/Users/beths/Desktop/LANDING/mask_tests/boxplot.png', bbox_inches='tight')

    print('end')

    # """




    # stacked bar
    """
    # format index for plotting
    sas_df.index = sas_df.index.strftime('%H:%M')

    color_list = ["dimgrey", "lightgrey", "deepskyblue", "lawngreen", "darkgreen", "limegreen", "olive"]

    fig, ax = plt.subplots(figsize=(12, 12))

    new_df.plot(ax=ax, kind='bar', stacked=True, color=color_list, width=0.85)

    # plt.gcf().autofmt_xdate()
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    ax.set_ylim(0, 100)
    ax.set_xlim(-.5, len(new_df.index) - 0.5)

    # half the amount of xticks present
    plt.locator_params(axis='x', nbins=len(new_df.index) / 3)

    plt.xlabel('Time UTC (hh:mm)')

    plt.savefig('C:/Users/beths/Desktop/LANDING/mask_tests/output.png', bbox_inches='tight')
    # plt.show()

    print('end')
    """



# CHOICES
doy_choice = 126
# av_period = 'hourly'
av_period = '10_mins'


save_path = 'C:/Users/beths/Desktop/LANDING/mask_tests/'
csv_file_name = str(doy_choice) + '_' + av_period + '.csv'

csv_file_path = save_path + csv_file_name

# check to see if the csv file exists
if os.path.isfile(csv_file_path):



    sas_df = csv_file_path

else:

    # create the dataframe
    main_dir = 'C:/Users/beths/Desktop/LANDING/fp_output/' + str(doy_choice) + '/' + av_period + '/'
    os.chdir(main_dir)
    file_list = []
    for file in glob.glob("*.tif"):
        file_list.append(main_dir + file)

    sas_df = lc_fract_multiple_sas(sa_list=file_list)

    # save the df as a csv
    sas_df.to_csv(save_path + csv_file_name)



lc_in_sa_stacked_bar(sas_df)
print('end')
