# Beth Saunders 09/09/2021
# main script used to create inputs to the source area model software (scintools)
# which requires 4 variables (1. Obukhov length, 2. friction velocity, 3. the standard deviation of the v component
# of wind, 4. wind direction).
# This script creates csv files which provide these 4 required variables for every source area to be made.

# imports
import pandas as pd
import os

from scint_flux import run_function
from scint_flux import look_up

from scint_fp.functions import wx_u_v_components
from scint_fp.functions import time_average_sa_input
from scint_fp.functions import sa_creation_selecting
from scint_fp.create_input_csvs import create_input_functions

# CHANGE HERE
out_dir_base = 'test_outputs/'

########################################################################################################################
# days read in from csv
csv_path = './DOY_in.csv'
DOY_in_df = pd.read_csv(csv_path)

# empty list to append to:
# each item will be a df of scint_flux outputs
df_list = []

for index, row in DOY_in_df.iterrows():

    # define site where the radiation data comes from
    rad_site = row.rad_site

    run_location = row.run_location
    if run_location == 'cluster':
        bdsm_path = '/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintools/example_inputs/rasters/height_surface_4m.tif'
        cdsm_path = '/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintools/example_inputs/rasters/height_veg_4m.tif'
        dem_path = '/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintools/example_inputs/rasters/height_terrain_4m.tif'
        raw_scint_path = '/storage/basic/micromet/Tier_raw/'
        processed_wx_path = '/storage/basic/micromet/Tier_processing/rv006011/new_data_scint/'
    elif run_location == 'local':
        bdsm_path = 'D:/Documents/scintools/example_inputs/rasters/height_surface_4m.tif'
        cdsm_path = 'D:/Documents/scintools/example_inputs/rasters/height_veg_4m.tif'
        dem_path = 'D:/Documents/scintools/example_inputs/rasters/height_terrain_4m.tif'
        raw_scint_path = 'C:/Users/beths/OneDrive - University of Reading/local_runs_data/data_wifi_problems/'
        processed_wx_path = 'C:/Users/beths/OneDrive - University of Reading/local_runs_data/data_wifi_problems/'
    elif run_location == 'mount':
        bdsm_path = 'D:/Documents/scintools/example_inputs/rasters/height_surface_4m.tif'
        cdsm_path = 'D:/Documents/scintools/example_inputs/rasters/height_veg_4m.tif'
        dem_path = 'D:/Documents/scintools/example_inputs/rasters/height_terrain_4m.tif'
        raw_scint_path = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/'
        processed_wx_path = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_scint/'
    else:
        raise TypeError('run_location in given csv is not an option.')

    if rad_site == 'KSSW':
        rad_file_path = raw_scint_path
    elif rad_site == 'BTT':
        if run_location == 'mount':
            rad_file_path = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/'
        elif run_location == 'cluster':
            rad_file_path = '/storage/basic/micromet/Tier_processing/rv006011/scint_data_testing/'
        else:
            raise TypeError('run_location in given csv is not an option.')
    else:
        raise TypeError('rad_site given in scv not an option.')

    # make sure DOY is padded with zeros
    doy_string = str(row.DOY).zfill(3)
    doy = int(str(row.Year) + doy_string)

    print(' ')
    print(doy)

    average_period = row.average

    if row.mins_ending_10 == 1:
        mins_ending_10 = True
    else:
        mins_ending_10 = False

    if row.unstable_only == 1:
        unstable_only = True
    else:
        unstable_only = False

    pair_id = row.pair
    las_instrument_type = look_up.pair_instruments[pair_id]

    # runs scint flux
    df = run_function.main_QH_calcs(doy=doy,
                                    pair_id=pair_id,
                                    sa_res=average_period,
                                    raw_scint_path=raw_scint_path,
                                    processed_wx_path=processed_wx_path,
                                    rad_file_path=rad_file_path,
                                    bdsm_path=bdsm_path,
                                    cdsm_path=cdsm_path,
                                    dem_path=dem_path,
                                    las_instrument_type=las_instrument_type,
                                    rad_site=rad_site,
                                    run_location=run_location,
                                    sa_path=False,
                                    write_file=False)

    # test plot - optional
    # plots.plot_qh(df)

    # APPEND BEFORE AVERAGING
    df_list.append(df)

    # wind calculations
    component_df = wx_u_v_components.ws_wd_to_u_v(df['wind_speed_adj'], df['wind_direction_corrected'])
    df = pd.concat([df, component_df], axis=1)

    # take the last 10 minute averages and calculate the standard deviation of wind for that period
    df_av = time_average_sa_input.time_average_sa(df, average_period)

    # convert the averages of the u and the v component back to wind speed and direction
    av_comp = wx_u_v_components.u_v_to_ws_wd(df_av['u_component'], df_av['v_component'])
    df_av = pd.concat([df_av, av_comp], axis=1)

    # determine which times are made into source areas here:
    df_selection = df_av
    # find unstable times only
    if unstable_only:
        df_selection = sa_creation_selecting.find_unstable_times(df_selection, neutral_limit=0.03)

    # remove nan rows
    df_selection = sa_creation_selecting.remove_nan_rows(df_selection)

    if average_period == 10:
        if mins_ending_10:
            # only take the 10-min average SAs on the hour ending
            df_selection = create_input_functions.take_hourly_vars(df_selection)

    # save to csv
    if average_period == 10:
        if unstable_only:
            if mins_ending_10:
                csv_out_string = 'met_inputs_minutes_ending_'
            else:
                csv_out_string = 'met_inputs_minutes_'
        else:
            if mins_ending_10:
                csv_out_string = 'met_inputs_minutes_all_stab_ending_'
            else:
                csv_out_string = 'met_inputs_minutes_all_stab_'
    elif average_period == 60:
        if unstable_only:
            csv_out_string = 'met_inputs_hourly_'
        else:
            csv_out_string = 'met_inputs_hourly_all_stab_'
    else:
        raise TypeError('average_period in given csv currently not an option.')

    # csv_name = csv_out_string + str(doy)[-3:] + '.csv'
    csv_name = csv_out_string + pair_id + '_' + str(doy) + '.csv'

    # construct out_dir based on inputs
    if average_period == 10:
        if mins_ending_10:
            out_string = '10_mins_ending'
        else:
            out_string = '10_mins'
    elif average_period == 60:
        out_string = 'hourly'
    else:
        raise TypeError('average_period in given csv currently not an option.')

    out_dir = out_dir_base + out_string + '/' + str(doy) + '/'

    # see if directory exists
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    csv_save_path = out_dir + csv_name
    df_selection.to_csv(csv_save_path)
    print('SAVED')

print('END')
