# Beth Saunders 09/09/2021
# main script used to create source area files.
# This calls the source area model software (scintools) and provides it with the required input variables for each
# source area to be made.

import pandas as pd
import scintools as sct
import numpy as np
import os

from scint_flux import look_up


def create_footprints(pair, roughness_inputs, spatial_inputs, path_params,
                      out_dir, csv_name):
    """
    Main function used to create source area files.
    This calls the source area model software (scintools) and provides it with the required input variables for each
    source area to be made.

    # ToDo: fill this in
    :param pair:
    :param roughness_inputs:
    :param spatial_inputs:
    :param path_params:
    :param out_dir:
    :param csv_name:
    :return:
    """

    # read inputs csv
    df = pd.read_csv(out_dir + csv_name)
    df.rename(columns={'Unnamed: 0': 'time'}, inplace=True)
    df.time = pd.to_datetime(df['time'], dayfirst=True)
    df = df.set_index('time')

    # limit time - optional
    # df = df.between_time('11:00', '13:00')

    # create footprint for each entry in dataframe
    for index, row in df.iterrows():
        time = row.name
        sigv = row['sig_v']
        wd = row['wind_direction_convert']
        ustar = row['ustar']
        L = row['L']

        title_string = time.strftime('%Y') + '_' + time.strftime('%j') + '_' + time.strftime('%H_%M')

        print(' ')
        print(title_string)
        print(' ')

        met_inputs = sct.MetInputs(obukhov=L,
                                   sigv=sigv,
                                   ustar=ustar,
                                   wind_dir=wd
                                   )

        fp_path = sct.run_pathfootprint(scint_pair=pair,
                                        met_inputs=met_inputs,
                                        roughness_inputs=roughness_inputs,
                                        path_params=path_params,
                                        target_percentage=0.6,
                                        spatial_inputs=spatial_inputs)

        # ToDo: temp fix. Need to take out once fixed in scintools
        fp_path.roughness_outputs.z_m = -999.0
        fp_path.footprint[fp_path.footprint == 0.0] = np.nan

        string_to_save = str(pair.pair_id) + '_' + str(spatial_inputs.domain_size) + '_' + title_string
        file_out = out_dir + string_to_save + '.tif'
        fp_path.save(out_dir + string_to_save)
        fp_path.save_tiff(file_out)

        print(title_string)

        print('END')


# run the create footprints function for the selection of SAs to be made in the input csv
if __name__ == "__main__":

    out_dir_base = 'test_outputs/'
    # days read in from csv
    csv_path = './DOY_in.csv'
    DOY_in_df = pd.read_csv(csv_path)

df_list = []

for index, row in DOY_in_df.iterrows():

    # make sure DOY is padded with zeros
    doy_string = str(row.DOY).zfill(3)

    doy = int(str(row.Year) + doy_string)

    run_location = row.run_location
    if run_location == 'cluster':
        bdsm_path = '/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintools/example_inputs/rasters/height_surface_4m.tif'
        cdsm_path = '/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintools/example_inputs/rasters/height_veg_4m.tif'
        dem_path = '/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintools/example_inputs/rasters/height_terrain_4m.tif'
    elif run_location == 'local':
        bdsm_path = 'D:/Documents/scintools/example_inputs/rasters/height_surface_4m.tif'
        cdsm_path = 'D:/Documents/scintools/example_inputs/rasters/height_veg_4m.tif'
        dem_path = 'D:/Documents/scintools/example_inputs/rasters/height_terrain_4m.tif'
    elif run_location == 'mount':
        bdsm_path = 'D:/Documents/scintools/example_inputs/rasters/height_surface_4m.tif'
        cdsm_path = 'D:/Documents/scintools/example_inputs/rasters/height_veg_4m.tif'
        dem_path = 'D:/Documents/scintools/example_inputs/rasters/height_terrain_4m.tif'

    average_period = row.average

    pair_id = row.pair

    if row.mins_ending_10 == 1:
        mins_ending_10 = True
    else:
        mins_ending_10 = False

    if row.unstable_only == 1:
        unstable_only = True
    else:
        unstable_only = False

    # construct csv name based on imputs
    if average_period == 10:
        if unstable_only:
            if mins_ending_10:
                average_period_string = 'minutes_ending'
            else:
                average_period_string = 'minutes'
        else:
            if mins_ending_10:
                average_period_string = 'minutes_all_stab_ending'
            else:
                average_period_string = 'minutes_all_stab'
    elif average_period == 60:
        if unstable_only:
            average_period_string = 'hourly'
        else:
            average_period_string = 'hourly_all_stab'

    # csv_name = 'met_inputs_' + average_period_string + '_' + doy_string + '.csv'

    csv_name = 'met_inputs_' + average_period_string + '_' + pair_id + '_' + str(doy) + '.csv'

    # construct out_dir based on inputs
    if average_period == 10:
        if mins_ending_10:
            out_string = '10_mins_ending'
        else:
            out_string = '10_mins'
    elif average_period == 60:
        out_string = 'hourly'

    out_dir = out_dir_base + out_string + '/' + str(doy) + '/'

    pair_id = row.pair
    # construct path using scintools
    tr_string = pair_id.split('_')[0]
    rx_string = pair_id.split('_')[1]

    pair = sct.ScintillometerPair(x=[look_up.site_info[tr_string]['x'], look_up.site_info[rx_string]['x']],
                                  y=[look_up.site_info[tr_string]['y'], look_up.site_info[rx_string]['y']],
                                  z_asl=[look_up.site_info[tr_string]['z_asl'], look_up.site_info[rx_string]['z_asl']],
                                  pair_id=pair_id,
                                  crs='epsg:32631')

    roughness_inputs = sct.RoughnessInputs()

    spatial_inputs = sct.SpatialInputs(
        domain_size=15000,
        x=float(pair.path_center().x),
        y=float(pair.path_center().y),
        z_asl=pair.path_center_z(),
        bdsm_path=bdsm_path,
        cdsm_path=cdsm_path,
        dem_path=dem_path)

    point_res = 50
    weightings = (100, 200)
    path_params = {'point_res': point_res,
                   'weightings': weightings}

    # see if directory exists
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    create_footprints(pair, roughness_inputs, spatial_inputs, path_params,
                      out_dir, csv_name)

    print('END')

print('end')
