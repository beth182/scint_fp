import os
import glob
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# from scint_fp.functions import landcover_type_present as lc


def combine_sa_rasters(path_string,
                       main_dir='//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintillometer_footprints/scint_fp/test_outputs/10_mins_ending/',
                       # main_dir='/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintillometer_footprints/scint_fp/test_outputs/10_mins_ending/'
                       ):
    """
    Takes a list of days (from csv, e.g. DOY_in) and combine each source area of that day (all times) into one
    source area - representing a "climatology" source area of the given target period (days included).

    # ToDo: fill these out
    :param path_string:
    :param main_dir:
    :return:
    """

    out_dir = '../'

    csv_path = '../../DOY_in.csv'
    DOY_in_df = pd.read_csv(csv_path)
    DOY_in_df['doy_string'] = DOY_in_df.Year.astype(str) + DOY_in_df.DOY.astype(str).str.zfill(3)
    DOYlist = DOY_in_df['doy_string'].astype(int).to_list()

    file_list = []
    for DOY in DOYlist:
        # make filepath for the given day
        DOYstring = str(DOY)
        current_dir = main_dir + DOYstring + '/'

        # find all files for the current day and append to list
        os.chdir(current_dir)
        for file in glob.glob("*" + path_string + "*.tif"):
            file_list.append(current_dir + file)

    # take first raster
    raster = rasterio.open(file_list[0])
    raster_array = raster.read(1)
    raster_array[np.isnan(raster_array)] = 0

    for i in range(1, len(file_list)):
        print(file_list[i])
        raster_add = rasterio.open(file_list[i])
        raster_array_add = raster_add.read(1)
        raster_array_add[np.isnan(raster_array_add)] = 0
        raster_array += raster_array_add
        raster_add.close()

    # get rid of zero values
    raster_array[raster_array == 0.0] = np.nan

    # Write to TIFF
    kwargs = raster.meta
    kwargs.update(
        dtype=rasterio.float32,
        count=1,
        compress='lzw')

    with rasterio.open(os.path.join(out_dir, 'combine.tif'), 'w', **kwargs) as dst:
        dst.write_band(1, raster_array.astype(rasterio.float32))


# combine_rasters('IMU_BTT')
print('end')

# optional post-evaluation

df_sa_columns = ['Building', 'Impervious', 'Water', 'Grass', 'Deciduous', 'Evergreen', 'Shrub']

P13_file = 'C:/Users/beths/OneDrive - University of Reading/Paper 2/combine_rasters/IMU_BTT.tif'
P13_sa_df = lc.landcover_fractions_in_SA_weighted(P13_file)

P13_df_sa_data = [[P13_sa_df.loc[1]['sa_weight_percent'],
                   P13_sa_df.loc[2]['sa_weight_percent'],
                   P13_sa_df.loc[3]['sa_weight_percent'],
                   P13_sa_df.loc[4]['sa_weight_percent'],
                   P13_sa_df.loc[5]['sa_weight_percent'],
                   P13_sa_df.loc[6]['sa_weight_percent'],
                   P13_sa_df.loc[7]['sa_weight_percent']]]

P13_sa_df = pd.DataFrame(P13_df_sa_data, columns=df_sa_columns)
P13_sa_df.index = ['IMU_BTT']

P15_file = 'C:/Users/beths/OneDrive - University of Reading/Paper 2/combine_rasters/SCT_SWT.tif'
P15_sa_df = lc.landcover_fractions_in_SA_weighted(P15_file)

P15_df_sa_data = [[P15_sa_df.loc[1]['sa_weight_percent'],
                   P15_sa_df.loc[2]['sa_weight_percent'],
                   P15_sa_df.loc[3]['sa_weight_percent'],
                   P15_sa_df.loc[4]['sa_weight_percent'],
                   P15_sa_df.loc[5]['sa_weight_percent'],
                   P15_sa_df.loc[6]['sa_weight_percent'],
                   P15_sa_df.loc[7]['sa_weight_percent']]]

P15_sa_df = pd.DataFrame(P15_df_sa_data, columns=df_sa_columns)
P15_sa_df.index = ['SCT_SWT']

P11_file = 'C:/Users/beths/OneDrive - University of Reading/Paper 2/combine_rasters/BTT_BCT.tif'
P11_sa_df = lc.landcover_fractions_in_SA_weighted(P11_file)

P11_df_sa_data = [[P11_sa_df.loc[1]['sa_weight_percent'],
                   P11_sa_df.loc[2]['sa_weight_percent'],
                   P11_sa_df.loc[3]['sa_weight_percent'],
                   P11_sa_df.loc[4]['sa_weight_percent'],
                   P11_sa_df.loc[5]['sa_weight_percent'],
                   P11_sa_df.loc[6]['sa_weight_percent'],
                   P11_sa_df.loc[7]['sa_weight_percent']]]

P11_sa_df = pd.DataFrame(P11_df_sa_data, columns=df_sa_columns)
P11_sa_df.index = ['BTT_BCT']

P12_file = 'C:/Users/beths/OneDrive - University of Reading/Paper 2/combine_rasters/BCT_IMU.tif'
P12_sa_df = lc.landcover_fractions_in_SA_weighted(P12_file)

P12_df_sa_data = [[P12_sa_df.loc[1]['sa_weight_percent'],
                   P12_sa_df.loc[2]['sa_weight_percent'],
                   P12_sa_df.loc[3]['sa_weight_percent'],
                   P12_sa_df.loc[4]['sa_weight_percent'],
                   P12_sa_df.loc[5]['sa_weight_percent'],
                   P12_sa_df.loc[6]['sa_weight_percent'],
                   P12_sa_df.loc[7]['sa_weight_percent']]]
# a dataframe of one source area
P12_sa_df = pd.DataFrame(P12_df_sa_data, columns=df_sa_columns)
P12_sa_df.index = ['BCT_IMU']

combine = pd.concat([P13_sa_df, P12_sa_df, P11_sa_df, P15_sa_df])

color_list = ["dimgrey", "lightgrey", "deepskyblue", "lawngreen", "darkgreen", "limegreen", "olive"]

fig, ax = plt.subplots(figsize=(12, 12))

combine.plot(ax=ax, kind='bar', stacked=True, color=color_list, width=0.85)

plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
ax.set_ylim(0, 100)
ax.set_xlim(-.5, len(combine.index) - 0.5)

plt.savefig('C:/Users/beths/OneDrive - University of Reading/Paper 1/mask_tests/output.png', bbox_inches='tight')
# plt.show()


print('end')
